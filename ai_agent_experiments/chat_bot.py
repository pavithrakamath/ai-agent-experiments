import os
from typing import List

import openai
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionMessageParam


class ChatBot:
    def __init__(self):
        load_dotenv()
        self.client = openai.AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                         azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                         api_version=os.getenv("AZURE_OPENAI_API_VERSION"))
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.system_message = "You are a helpful assistant. Your name is Bot. Be Polite in your answers."
        self.messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=self.system_message, role="system")]

    def run(self, query) -> str:
        self.messages.append(ChatCompletionUserMessageParam(content=query, role="user"))
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        self.messages.append(
            ChatCompletionAssistantMessageParam(content=response.choices[0].message.content, role="assistant"))
        return response.choices[0].message.content


if __name__ == "__main__":
    agent = ChatBot()
    print("\033[91m")
    user_input = input("I am Bot! I am here to chat with you! When you have had enough of me just type in `exit`. so what's on your mind?\n")
    while True:

        if user_input == "exit":
            print("Exiting...")
            break
        else:
            result = agent.run(user_input)
            print(f"Bot:: {result}\n")
            user_input = input("what next>>")
