from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters, stdio_client


class McpStdioClient:
    """
    Multi-Control Protocol (MCP) client for managing connections and tool operations.
    Provides an interface for establishing connections, listing available tools,
    executing specific tools, and managing disconnections.
    """

    def __init__(self, name:str, command: str, server_args: list[str], env_vars: dict[str, str]=None) -> None:
        self.name = name
        self.command = command
        self.server_args = server_args
        self.env_vars = env_vars

        self._session:ClientSession = None
        self._connected:bool = False
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
            stdio_connection= await self._exit_stack.enter_async_context(stdio_client(server_parameters))
            self.read, self.write = stdio_connection

            self._session = await self._exit_stack.enter_async_context(ClientSession(read_stream=self.read, write_stream=self.write))

            await self._session.initialize()
            self._connected = True


async def get_available_tools(self) -> list[Any]:
    """
    Retrieves a list of available tools from the connected MCP server.

    Returns:
        list: List of available tool names and their descriptions

    Raises:
        ConnectionError: If not connected to the server
    """
    pass


async def use_tool(self, tool_name: str, tool_args: dict) -> str:
    """
    Executes a specified tool with provided arguments.

    Args:
        tool_name (str): Name of the tool to execute
        tool_args (dict): Arguments required for tool execution

    Returns:
        str: Result of tool execution

    Raises:
        ValueError: If tool_name is invalid or tool_args are incorrect
        ConnectionError: If not connected to the server
    """
    pass


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
