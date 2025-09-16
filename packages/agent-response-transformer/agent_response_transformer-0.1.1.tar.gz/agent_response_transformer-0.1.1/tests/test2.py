import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    WebSearchTool,
    FunctionTool,
    FileSearchTool,
    ComputerTool,
    HostedMCPTool,
    LocalShellTool,
    ImageGenerationTool,
    CodeInterpreterTool,
)
from agents.model_settings import ModelSettings
from agents.mcp import MCPServerSse, MCPServerStdio

async def chat():
    agent = Agent(
        name="searcher",
        instructions="You are a helpful assistant.",
        tools=[WebSearchTool()]
    )

    result = Runner.run_streamed(agent, input="帮我制定一个加州3日游计划")
    async for event in result.stream_events():
        print(event, end="", flush=True)

async def main():
    async with MCPServerSse(
        name="searxng",
        params={
            "url": "https://mcp.netmind.ai/sse/988acff610a54fbc8f7eec63a121d993/time/sse",
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
    # async with MCPServerStdio(
    #     name="Filesystem Server via npx",
    #     client_session_timeout_seconds=30,
    #     params={
    #         "command": "npx",
    #         "args": ["-y", "mcp-searxng@0.6.5"],
    #         "env": {"SEARXNG_URL": "http://localhost:51673"}
    #     }
    # ) as server:
        agent = Agent(
            name="searcher",
            instructions="You are a helpful assistant.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        # result = await Runner.run(agent, "What's the weather in Tokyo?")
        # print(result.final_output)
        result = Runner.run_streamed(agent, input="what is the time in Tokyo and London")
        async for event in result.stream_events():
            print(event, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
