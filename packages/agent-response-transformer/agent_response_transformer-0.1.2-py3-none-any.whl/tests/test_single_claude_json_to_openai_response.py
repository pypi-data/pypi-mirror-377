import pytest
from unittest.mock import Mock
from agent_response_transformer import ResponseTransformer
from agents.stream_events import (
    Agent,
    AgentUpdatedStreamEvent,
    RunItemStreamEvent,
    RawResponsesStreamEvent,
)
from agents.mcp.server import MCPServerSse
from agents import WebSearchTool
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from openai.types.responses.response_text_done_event import ResponseTextDoneEvent
from openai.types.responses.response_completed_event import ResponseCompletedEvent
from openai.types.responses.response_output_item_done_event import (
    ResponseOutputItemDoneEvent,
)
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
import json


def test_single_claude_json_to_openai_response_system_text():
    """Test the single_claude_json_to_openai_response function with system text type"""

    # Mock Claude response data for system text
    claude_response = {
        "type": "assistant",
        "message": {
            "id": "msg_01Cq4fs2jrMKgMCeFeHX93vy",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-20250514",
            "content": [{"type": "text", "text": "This is a test system message"}],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {
                "input_tokens": 4,
                "cache_creation_input_tokens": 17862,
                "cache_read_input_tokens": 4736,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 17862,
                    "ephemeral_1h_input_tokens": 0,
                },
                "output_tokens": 1,
                "service_tier": "standard",
            },
        },
        "parent_tool_use_id": None,
        "session_id": "757834a0-df6d-4381-83fd-570882f28722",
        "uuid": "83632f9a-9bae-4f56-a2d8-945654b1ac25",
    }

    # Call the function
    result = ResponseTransformer().single_claude_json_to_openai_response(
        claude_response
    )

    # Verify the result
    assert len(result) == 3

    # First item should be ResponseTextDeltaEvent
    assert isinstance(result[0], RawResponsesStreamEvent)
    assert isinstance(result[0].data, ResponseTextDeltaEvent)
    assert result[0].data.delta == "This is a test system message"

    # Second item should be ResponseTextDoneEvent
    assert isinstance(result[1], RawResponsesStreamEvent)
    assert isinstance(result[1].data, ResponseTextDoneEvent)
    assert result[1].data.text == "This is a test system message"

    # Third item should be ResponseCompletedEvent with usage
    assert isinstance(result[2], RawResponsesStreamEvent)
    assert isinstance(result[2].data, ResponseCompletedEvent)
    assert result[2].data.response.usage.input_tokens == 4 + 17862 + 4736
    assert result[2].data.response.usage.output_tokens == 1


def test_single_claude_json_to_openai_response_tool_use():
    """Test the single_claude_json_to_openai_response function with tool use type"""

    # Mock Claude response data for tool use
    claude_response = {
        "type": "assistant",
        "message": {
            "id": "msg_01Mc5SBNK1VjmKsrEPk3Tc4B",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-20250514",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_016Qabw3UzsBHr2Aw4BMsKhg",
                    "name": "mcp__google-maps__maps_directions",
                    "input": {
                        "origin": "Los Angeles, CA",
                        "destination": "Las Vegas, NV",
                        "mode": "driving",
                    },
                }
            ],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {
                "input_tokens": 7,
                "cache_creation_input_tokens": 527,
                "cache_read_input_tokens": 22598,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 527,
                    "ephemeral_1h_input_tokens": 0,
                },
                "output_tokens": 1,
                "service_tier": "standard",
            },
        },
        "parent_tool_use_id": None,
        "session_id": "757834a0-df6d-4381-83fd-570882f28722",
        "uuid": "ddb8558d-6bc6-4c2a-b792-b9ffdf581218",
    }

    # Call the function
    result = ResponseTransformer().single_claude_json_to_openai_response(
        claude_response
    )

    # Verify the result
    assert len(result) == 2

    # First item should be ResponseOutputItemDoneEvent with ResponseFunctionToolCall
    assert isinstance(result[0], RawResponsesStreamEvent)
    assert isinstance(result[0].data, ResponseOutputItemDoneEvent)
    assert isinstance(result[0].data.item, ResponseFunctionToolCall)
    assert result[0].data.item.name == "maps_directions"
    assert result[0].data.item.arguments == json.dumps(
        {"origin": "Los Angeles, CA", "destination": "Las Vegas, NV", "mode": "driving"}
    )
    assert result[0].data.item.call_id == "toolu_016Qabw3UzsBHr2Aw4BMsKhg"

    # Second item should be ResponseCompletedEvent with usage
    assert isinstance(result[1], RawResponsesStreamEvent)
    assert isinstance(result[1].data, ResponseCompletedEvent)
    assert result[1].data.response.usage.input_tokens == 7 + 527 + 22598
    assert result[1].data.response.usage.output_tokens == 1


def test_single_claude_json_to_openai_response_user_tool_result():
    """Test the single_claude_json_to_openai_response function with user tool result type"""

    # Mock Claude response data for user tool result
    claude_response = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "tool_use_id": "toolu_016Qabw3UzsBHr2Aw4BMsKhg",
                    "type": "tool_result",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is the tool result content"
                        }
                    ]
                }
            ]
        },
        "parent_tool_use_id": None,
        "session_id": "757834a0-df6d-4381-83fd-570882f28722",
        "uuid": "bdf84296-d597-4b23-9df8-9624be57fa5f"
    }

    # Call the function
    result = ResponseTransformer().single_claude_json_to_openai_response(
        claude_response
    )

    # Verify the result
    assert len(result) == 1

    # First item should be RunItemStreamEvent with ToolCallOutputItem
    assert isinstance(result[0], RunItemStreamEvent)
    assert result[0].name == "tool_output"
    assert result[0].item.type == "tool_call_output_item"
    # assert result[0].item.output == json.dumps([
    #                     {
    #                         "type": "text",
    #                         "text": "This is the tool result content"
    #                     }
    #                 ])


def test_single_claude_json_to_openai_response_empty_input():
    """Test the single_claude_json_to_openai_response function with empty input"""

    # Empty dict
    result = ResponseTransformer().single_claude_json_to_openai_response({})

    # Should return an empty list
    assert len(result) == 0


def test_single_claude_json_to_openai_response_result_type():
    """Test the single_claude_json_to_openai_response function with result type"""

    # Mock Claude response data for result type
    claude_response = {"type": "result"}

    # Call the function
    result = ResponseTransformer().single_claude_json_to_openai_response(
        claude_response
    )

    # Should return an empty list
    assert len(result) == 0
    

if __name__ == "__main__":
    pytest.main([__file__])
