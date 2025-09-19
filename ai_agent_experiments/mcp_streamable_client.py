from contextlib import AsyncExitStack
from typing import Callable

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPStreamableClient:
    def __init__(self, name: str, server_url: str) -> None:
        self.name = name
        self.server_url = server_url
        self._session: ClientSession = None
        self._connected: bool = False
        self._exit_stack = AsyncExitStack()
        self._get_session_id: Callable[[], str] = None

    async def connect(self, headers:dict[str, str]|None) -> None:
        if self._connected:
            raise RuntimeError("Already connected to the server.")
        else:
            server_connection = await self._exit_stack.enter_async_context(streamablehttp_client(self.server_url, headers))
            self.read, self.write, self._get_session_id = server_connection
            self._session =await self._exit_stack.enter_async_context(ClientSession(read_stream=self.read, write_stream=self.write))
            await self._session.initialize()
            self._connected = True


    async def disconnect(self):
        if self._connected:
            await self._exit_stack.aclose()
            self._connected = False
            self._session = None

    async def use_tool(self, tool_name, tool_args):
        pass

    async def list_tools(self):
        pass
