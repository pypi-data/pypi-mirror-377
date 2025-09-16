from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Sugar MCP WebSocket Server")

# 存储活跃的WebSocket连接
active_connections = []
session_ids = {}


class DecoderType(int):
    STREAM_CONTENT = 1  # 此元素是流式输出的自然语言之一
    MESSAGE_CONTENT = 2  # 非流失输出，直接获取整段自然语言
    REASONING_CONTENT = 3  # 代表是 推理模型的 思考过程，这部分也是流式的
    TOOL_USE = 4  # 代表这一步是使用了 tool
    MCP_SERVER_USE = 5  # 代表这一步使用了 某一个 MCP
    AGENT_CALL = 6  # 代表这一步和别的 Agent 进行了单论的交互
    XYZ_AGENT_POWER = 7  # 代表使用了我们平台特有的能力
    USAGE_REPORT = 8  # 代表了这一次返回的是 这一次请求的成本
    SPECIAL_SIGNAL = 9  # 是让前端显示特殊 气泡 的信号
    WELCOME_MESSAGE = 10  # 是让前端显示 ADMIN 欢迎信息的信号
    WELCOME_QUESTIONS = 11  # 是让前端显示欢迎问题的信号
    TASK_STATUS_HISTORY = 12  # 任務執行完後通知用戶
    AGENT_TO_AGENT_CALL = (
        13  # 代理调用类型：用于处理代理初始化和配置信息，包括代理名称、参数和交互链
    )
    WELCOME_USER_MESSAGE = 14  # 是让前端显示 User 欢迎信息的信号
    TASK_TO_UPDATE_NOTIFY = 15  # 是让前端显示任务更新通知的信号
    TASK_PROVISION_INFO_NOTIFY = 16  # 是让前端显示任务补充信息通知的信号
    TASK_RESULT_NOTIFY = 17  # 是让前端显示任务结果信息


class WebsocketResponse:
    """
    heart beat
    {
        "code": 200,
        "message": "Success",
        "result": "PONG",
        "isFailed": false,
        "failedCode": null,
        "metadata": {
            "heartBeat": true
        }
    }

    text message
    {
        "code": 200,
        "message": "操作",
        "result": {},
        "isFailed": false,
        "failedCode": null,
        "metadata": {
            "agentId": 1947,
            "userMode": 1,
            "agentUpdated": false,
            "taskUpdated": false,
            "isUpdatedBy": null,
            "isFinishStream": false,
            "isChatFinished": false,
            "decoderType": 1,
            "outputMeta": {
                "content": "操作",
                "mcpServerName": null,
                "mcpToolName": null,
                "mcpToolArguments": null,
                "mcpToolResponse": null,
                "agentName": null,
                "agentArguments": null,
                "interactionChain": null,
                "toolName": null,
                "toolArguments": null,
                "toolResponse": null,
                "powerName": null,
                "powerArguments": null,
                "powerResponse": null,
                "usageReport": null,
                "signalName": null,
                "signalType": null,
                "signalData": null,
                "agentToAgentName": null,
                "agentToAgentArguments": null,
                "agentToAgentResponse": null,
                "agentToAgentInput": null,
                "agentToAgentOutput": null
            }
        },
        "createdAt": "2025-09-08T08:58:39Z"
    }
    """

    def __init__(
        self,
        code: int = 200,
        message: str = "Success",
        result: str = "PONG",
        is_failed: bool = False,
        failed_code: int = None,
        metadata: dict = None,
    ):
        self.code = code
        self.message = message
        self.result = result
        self.is_failed = is_failed
        self.failed_code = failed_code
        self.metadata = metadata or {}

    def to_json(self):
        return json.dumps(
            {
                "code": self.code,
                "message": self.message,
                "result": self.result,
                "isFailed": self.is_failed,
                "failedCode": self.failed_code,
                "metadata": self.metadata,
            }
        )


class OutputMeta:
    def __init__(
        self,
        content: str = None,
        mcpServerName: str = None,
        mcpToolName: str = None,
        mcpToolArguments: dict = None,
        mcpToolResponse: dict = None,
        agentName: str = None,
        agentArguments: dict = None,
        interactionChain: list = None,
        toolName: str = None,
        toolArguments: dict = None,
        toolResponse: dict = None,
        powerName: str = None,
        powerArguments: dict = None,
        powerResponse: dict = None,
        usageReport: dict = None,
        signalName: str = None,
        signalType: str = None,
        signalData: dict = None,
        agentToAgentName: str = None,
        agentToAgentArguments: dict = None,
        agentToAgentResponse: dict = None,
        agentToAgentInput: dict = None,
        agentToAgentOutput: dict = None,
    ):
        self.content = content
        self.mcpServerName = mcpServerName
        self.mcpToolName = mcpToolName
        self.mcpToolArguments = mcpToolArguments
        self.mcpToolResponse = mcpToolResponse
        self.agentName = agentName
        self.agentArguments = agentArguments
        self.interactionChain = interactionChain
        self.toolName = toolName
        self.toolArguments = toolArguments
        self.toolResponse = toolResponse
        self.powerName = powerName
        self.powerArguments = powerArguments
        self.powerResponse = powerResponse
        self.usageReport = usageReport
        self.signalName = signalName
        self.signalType = signalType
        self.signalData = signalData
        self.agentToAgentName = agentToAgentName
        self.agentToAgentArguments = agentToAgentArguments
        self.agentToAgentResponse = agentToAgentResponse
        self.agentToAgentInput = agentToAgentInput
        self.agentToAgentOutput = agentToAgentOutput


class Metadata:
    def __init__(
        self,
        agentId: int = None,
        userMode: int = None,
        agentUpdated: bool = False,
        taskUpdated: bool = False,
        isUpdatedBy: str = None,
        isFinishStream: bool = False,
        isChatFinished: bool = False,
        decoderType: DecoderType = DecoderType.STREAM_CONTENT,
        outputMeta: OutputMeta = None,
    ):
        self.agentId = agentId
        self.userMode = userMode
        self.agentUpdated = agentUpdated
        self.taskUpdated = taskUpdated
        self.isUpdatedBy = isUpdatedBy
        self.isFinishStream = isFinishStream
        self.isChatFinished = isChatFinished
        self.decoderType = decoderType
        self.outputMeta = outputMeta or OutputMeta()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 从WebSocket头部获取数据
    socket_key = websocket.headers.get("sec-websocket-key", "")

    active_connections.append(websocket)
    try:
        while True:
            # 等待客户端发送消息
            data = await websocket.receive_text()
            # 处理接收到的消息
            await handle_message(data, socket_key, websocket)
            # # 发送响应给客户端
            # await websocket.send_text(response)
    except WebSocketDisconnect:
        # 当连接断开时，从活跃连接列表中移除
        active_connections.remove(websocket)
        print(f"WebSocket连接已断开: {websocket.client_host}")


async def handle_message(message: str, socket_key: str, websocket: WebSocket) -> str:
    """
    处理接收到的WebSocket消息
    """
    try:
        # 尝试解析JSON消息
        data = json.loads(message)

        # 根据消息类型处理
        if "heart_beat" in data:
            # 处理heartbeat
            return WebsocketResponse(
                result="PONG", metadata={"heartBeat": True}
            ).to_json()
        else:
            # 处理chat message
            # {"message":"搜一下5090显卡的价格","user_timezone":"Asia/Shanghai","agentId":1947,"userMode":1}
            xyz_request_message = data.get("message")

            # 把message传给claude code
            import subprocess
            import uuid

            # 生成一个唯一的会话ID
            session_id = str(uuid.uuid4())
            session_ids[socket_key] = session_id

            # 构建claude命令
            claude_command = ["claude"]

            if socket_key in session_ids:
                claude_command += ["--session-id", session_ids[socket_key]]

            claude_command += [
                "-p",
                xyz_request_message,
                "--permission-mode",
                "bypassPermissions",
                "--output-format",
                "stream-json",
                "--verbose",
            ]

            try:
                # 执行claude命令
                result = subprocess.run(
                    claude_command, capture_output=True, text=True, check=True
                )

                logger.info(claude_command, result)
                # 返回claude的输出
                await websocket.send_text(
                    WebsocketResponse(
                        result="claude_response",
                        metadata={
                            "message": message,
                            "claude_output": result.stdout,
                            "claude_error": result.stderr,
                        },
                    ).to_json()
                )

            except subprocess.CalledProcessError as e:
                # 如果命令执行出错，返回错误信息
                await websocket.send_text(
                    WebsocketResponse(
                        code=500,
                        message="Claude command failed",
                        result="error",
                        is_failed=True,
                        metadata={
                            "message": message,
                            "error": str(e),
                            "stderr": e.stderr,
                        },
                    ).to_json()
                )
            except Exception as e:
                # 处理其他异常
                await websocket.send_text(
                    WebsocketResponse(
                        code=500,
                        message="Error processing message",
                        result="error",
                        is_failed=True,
                        metadata={"message": message, "error": str(e)},
                    ).to_json()
                )
    except json.JSONDecodeError:
        # 如果不是JSON，直接回显
        await websocket.send_text(
            WebsocketResponse(result="echo", metadata={"message": message}).to_json()
        )


# 添加一个用于测试的异步任务
@app.get("/broadcast")
async def broadcast_message(message: str = "Hello from broadcast!"):
    """
    向所有连接的WebSocket客户端广播消息
    """
    tasks = []
    for connection in active_connections:
        tasks.append(
            connection.send_text(json.dumps({"type": "broadcast", "message": message}))
        )

    await asyncio.gather(*tasks)
    return JSONResponse(
        content={"message": f"Broadcasted message to {len(active_connections)} clients"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
