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
import json

def test_claude_json_to_openai_response_with_system_and_run_item():
    """Test the claude_json_to_openai_response function with system and run_item_stream_event types"""
    
    # Mock Claude response data
    # read test data from response/claude_xxx_response.json
    with open("response/claude_cmd_response.json") as f:
        claude_response = json.load(f)
    
    # Call the function
    result = ResponseTransformer().claude_json_to_openai_response(claude_response)
    
    # Verify the result
    assert len(result) == 2
    
    # First item should be AgentUpdatedStreamEvent
    assert isinstance(result[0], AgentUpdatedStreamEvent)
    
    # Second item should be RunItemStreamEvent
    assert isinstance(result[1], RunItemStreamEvent)
    
    # Verify the agent details
    agent = result[0].new_agent
    assert agent.name == "mock_agent"
    assert agent.instructions == "mock description"
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], WebSearchTool)
    assert len(agent.mcp_servers) == 1
    assert agent.mcp_servers[0].name == "linear"
    assert agent.mcp_servers[0].cache_tools_list == False
    
    # Verify the run item details
    run_item = result[1]
    assert run_item.name == "test_item"
    assert run_item.item == {"content": "test content"}

def test_claude_json_to_openai_response_with_mcp():
    """Test the claude_json_to_openai_response function with system and run_item_stream_event types"""
    
    # Mock Claude response data
    # read test data from response/claude_xxx_response.json
    with open("response/claude_mcp_response.json") as f:
        claude_response = json.load(f)
    
    # Call the function
    result = ResponseTransformer().claude_json_to_openai_response(claude_response)
    
    # Verify the result
    assert len(result) == 2
    
    # First item should be AgentUpdatedStreamEvent
    assert isinstance(result[0], AgentUpdatedStreamEvent)
    
    # Second item should be RunItemStreamEvent
    assert isinstance(result[1], RunItemStreamEvent)
    
    # Verify the agent details
    agent = result[0].new_agent
    assert agent.name == "mock_agent"
    assert agent.instructions == "mock description"
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], WebSearchTool)
    assert len(agent.mcp_servers) == 1
    assert agent.mcp_servers[0].name == "linear"
    assert agent.mcp_servers[0].cache_tools_list == False
    
    # Verify the run item details
    run_item = result[1]
    assert run_item.name == "test_item"
    assert run_item.item == {"content": "test content"}

def test_claude_json_to_openai_response_empty_input():
    """Test the claude_json_to_openai_response function with empty input"""
    
    # Empty list
    result = ResponseTransformer().claude_json_to_openai_response([])
    
    # Should return a list with just the AgentUpdatedStreamEvent
    assert len(result) == 1
    assert isinstance(result[0], AgentUpdatedStreamEvent)
    
    # Verify the agent details
    agent = result[0].new_agent
    assert agent.name == "mock_agent"
    assert agent.instructions == "mock description"
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], WebSearchTool)
    assert len(agent.mcp_servers) == 0



if __name__ == "__main__":
    pytest.main([__file__])
