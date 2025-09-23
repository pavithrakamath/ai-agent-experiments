import asyncio
import json
import os
from typing import List

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionMessageParam, ChatCompletionToolMessageParam

from ai_agent_experiments.mcp_stdio_client import McpStdioClient


class ChatBot:
    def __init__(self):
        load_dotenv()
        self.client = AsyncAzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                       azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                       api_version=os.getenv("AZURE_OPENAI_API_VERSION"))
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.system_message = "You are a helpful assistant. Your name is Bot. Be Polite in your answers. The way to exit any conversation with you is to type `exit`."
        self.messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=self.system_message, role="system")]

        self.mcp_client = McpStdioClient("greeter-server", "python",
                                         ["/Users/pk/work/ai-agent-experiments/tools/research-mcp-server.py"])

    async def run(self, query) -> str:
        self.messages.append(ChatCompletionUserMessageParam(content=query, role="user"))
        response = await  self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=await self.mcp_client.get_available_tools(),
        )
        continues = True
        while continues:
            message = response.choices[0].message
            if message.tool_calls:
                self.messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=message.content,
                                                                         tool_calls=message.tool_calls))

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    result = await self.mcp_client.use_tool(tool_name, tool_args)
                    # McpStdioClient returns a normalized string; append directly as tool message
                    self.messages.append(
                        ChatCompletionToolMessageParam(role="tool", content=result, tool_call_id=tool_call.id))

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.mcp_client._tools if self.mcp_client._tools else None,
                )
            else:
                continues = False
        # Return the final assistant message content
        final_message = response.choices[0].message
        return final_message.content or ""


async def main() -> None:
    agent = ChatBot()
    try:
        await agent.mcp_client.connect()
        prompt = "\033[95mI am Bot! I am here to chat with you! When you have had enough of me just type in `exit`. so what's on your mind?\n>>"
        while True:
            try:
                user_input = await asyncio.to_thread(input, prompt)
            except EOFError:
                # Treat EOF (e.g., Ctrl+D) as an exit signal
                print("Exiting...")
                break

            if user_input == "exit":
                print("Exiting...")
                break
            else:
                result = await agent.run(user_input)
                print(f"\033[95mBot:: {result}")
                prompt = "\033[92mWhat next >>"
    except KeyboardInterrupt:
        print("Interrupted. Shutting down...")
    finally:
        # Ensure we always disconnect the MCP client to avoid hanging subprocesses
        await agent.mcp_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
