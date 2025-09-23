import asyncio

import mcp
from mcp import stdio_server
from mcp.server import Server
from mcp.types import TextContent, Tool


### IN this case, we have built a stdio MCP server using the mcp library and not FASTMCP

class HelloService:

    def __init__(self) -> None:
        self.server = Server("greet-server")

        @self.server.call_tool()
        async def say_hello(name: str, arguments: dict[str, str]) -> list[TextContent]:
            user_input = arguments["username"]
            if user_input == "":
                user_input = "world"
            return [TextContent(text=f"Hello, {user_input}!", type="text")]

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [mcp.Tool(name="say_hello", description="Say hello to someone",
                             inputSchema={
                                 "type": "object",
                                 "properties": {
                                     "username": {
                                         "type": "string",
                                         "description": "The name of the person to say hello to"
                                     }
                                 },
                                 "required": ["username"]
                             }
                             )]

    async def run(self) -> None:
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


if __name__ == "__main__":
    async def main() -> None:
        service = HelloService()
        await service.run()
        print("Server stopped.")


    asyncio.run(main())
