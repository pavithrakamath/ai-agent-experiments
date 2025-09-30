import html

import requests
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from ai_agent_experiments.config import Configuration


def search(user_query: str) -> dict[str, str]:
    # TODO: Add input validation and more comprehensive error handling
    try:
        safe_input = html.escape(user_query.strip())
        response = requests.get(f"https://api.duckduckgo.com/?q={safe_input}&format=json")
        data = response.json()
        print(data)
        return data
    except requests.exceptions.JSONDecodeError:
        return {"error": "Invalid JSON response"}


class ResearchAgent:
    def __init__(self, config:Configuration):
        self.client = AzureOpenAI(api_key=config.client_config["api_key"],
                                       azure_endpoint=config.client_config["azure_endpoint"],
                                       api_version=config.client_config["api_version"])
        self.model = config.client_config["model"]

    def analyze(self, search_result, original_query) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                ChatCompletionSystemMessageParam(
                    content="You are a research assistant that analyzes and summarizes information.", role="system"),
                ChatCompletionUserMessageParam(
                    content=f"Analyze the following search result: {search_result} and relate it to the original query: {original_query}.  Synthesize the findings into a comprehensive answer",
                    role="user")
            ],
            max_tokens=200
        )
        return response.choices[0].message.content

    def run(self, query) -> str:
        # Step 1: Agent decides it needs external data
        print(f"Agent: I need to research '{query}'")
        search_results = search(query)
        # Step 2: Agent reasons about the external data
        print("Agent: Now I'll analyze what I found...")
        analysis = self.analyze(search_results, query)
        # Step 3: Return the final answer
        return analysis


if __name__ == "__main__":
    configuration = Configuration("../config.json")
    agent = ResearchAgent(configuration)
    user_input = "What are the latest trends in AI research?"
    result = agent.run(user_input)
    print(result)
