import asyncio
from contextlib import AsyncExitStack
from typing import Any, List

from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import CallToolResult
from openai.types.chat import ChatCompletionFunctionToolParam


class McpStdioClient:
    """
    Multi-Control Protocol (MCP) client for managing connections and tool operations.
    Provides an interface for establishing connections, listing available tools,
    executing specific tools, and managing disconnections.
    """

    def __init__(self, name: str, command: str, server_args: list[str], env_vars: dict[str, str] = None) -> None:
        """
        Initializes the MCP client with server connection parameters.
        """
        self.available_tools: List[Any] = []
        self.name = name
        self.command = command
        self.server_args = server_args
        self.env_vars = env_vars

        self._session: ClientSession = None
        self._connected: bool = False
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self) -> None:
        """
        Establishes asynchronous connection to the MCP server.

         Returns:
            None

        Raises:
            ConnectionError: If unable to establish connection with the server
        """
        if self._connected:
            raise RuntimeError("Already connected to the server.")
        else:
            server_parameters = StdioServerParameters(
                command=self.command,
                args=self.server_args,
                env=self.env_vars if self.env_vars else None
            )
            # when calling async functions, we need to use async context managers to simplify
            # the code (remember the old way of writing try and close resources in finally)
            # you add things in the LIFO stack of async context managers using enter_async_context
            try:
                stdio_connection = await self._exit_stack.enter_async_context(stdio_client(server_parameters))
                read, write = stdio_connection

                self._session = await self._exit_stack.enter_async_context(
                    ClientSession(read_stream=read, write_stream=write))

                await self._session.initialize()
                response = await self._session.list_tools()
                tools = response.tools
                print(f"Connected to server {self.name} with tools:", {t.name for t in tools})
                for tool in tools:
                    # Convert MCP tool to OpenAI tool format
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    self.available_tools.append(openai_tool)
                self._connected = True
            except Exception as e:
                raise ConnectionError(f"Failed to connect to server: {str(e)}")

    async  def get_available_tools(self) -> List[Any]:
        """
        Retrieves the cached list of available tools from the connected MCP server.

        Returns:
            list: List of available tool names and their descriptions
        """
        return self.available_tools


    async def use_tool(self, tool_name: str, tool_args: dict) -> str:
        """
        Executes a specified tool with provided arguments and returns a normalized string.

        Args:
            tool_name (str): Name of the tool to execute
            tool_args (dict): Arguments required for tool execution

        Returns:
            str: Normalized textual result of tool execution suitable for OpenAI tool messages

        Raises:
            ValueError: If tool_name is invalid or tool_args are incorrect
            ConnectionError: If not connected to the server
        """
        if not self._connected or self._session is None:
            raise ConnectionError("Not connected to the server. Call connect() before using tools.")
        # Call the MCP tool and normalize its result to a plain string
        result = await self._session.call_tool(name=tool_name, arguments=tool_args)

        tool_content = None
        try:
            content_items = getattr(result, "content", None)
            if isinstance(content_items, list) and content_items:
                parts = []
                for item in content_items:
                    if isinstance(item, dict):
                        if item.get("type") == "text" and "text" in item:
                            parts.append(item["text"])
                        elif item.get("type") == "json" and "json" in item:
                            import json as _json
                            parts.append(_json.dumps(item["json"], indent=2))
                    else:
                        t = getattr(item, "type", None)
                        if t == "text" and hasattr(item, "text"):
                            parts.append(item.text)
                        elif t == "json" and hasattr(item, "json"):
                            import json as _json
                            parts.append(_json.dumps(item.json, indent=2))
                if parts:
                    tool_content = "\n".join(parts)
            if tool_content is None:
                tool_content = getattr(result, "result", None) or getattr(result, "output", None)
            if tool_content is None:
                tool_content = str(result)
        except Exception:
            tool_content = str(result)

        return tool_content

    async def disconnect(self) -> None:
        """
        Closes connection with the MCP server.

        Returns:
            None
        """
        if self._connected:
            await self._exit_stack.aclose()
            self._connected = False
            self._session = None
