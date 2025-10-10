import json
from typing import List

from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionMessageParam, ChatCompletionToolMessageParam

from ai_agent_experiments.config import Configuration
from ai_agent_experiments.mcp_stdio_client import McpStdioClient


class ChatBot:
    def __init__(self, config: Configuration):

        self.client = AsyncAzureOpenAI(api_key=config.azure_open_ai_config["api_key"],
                                       azure_endpoint=config.azure_open_ai_config["azure_endpoint"],
                                       api_version=config.azure_open_ai_config["api_version"])
        self.model = config.azure_open_ai_config["model"]
        self.system_message = "You are a helpful assistant. Your name is Bot. Be Polite in your answers. The way to exit any conversation with you is to type `exit`."
        self.messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=self.system_message, role="system")]

        self.mcp_client = McpStdioClient("research-server", "poetry",
                                         ["run", "python", "-m", "tools.research_server"])

    async def run(self, query) -> str:
        # TODO: Add input validation and error handling for production use
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
                    # McpStdioClient returns a normalized string; append directly as a tool message
                    self.messages.append(
                        ChatCompletionToolMessageParam(role="tool", content=result, tool_call_id=tool_call.id))

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=await self.mcp_client.get_available_tools()
                )
            else:
                continues = False
        # Return the final assistant message content
        final_message = response.choices[0].message
        return final_message.content or ""
