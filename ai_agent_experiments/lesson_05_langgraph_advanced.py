import operator
from typing import Annotated, Any, TypedDict, Type, Optional

import wikipediaapi
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import AzureChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.constants import END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from ai_agent_experiments.config import Configuration


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class LangGraphAgent:
    def __init__(self, model: AzureChatOpenAI, user_tools: list[BaseTool], system_prompt: str = ""):
        # Build the graph
        graph = StateGraph(state_schema=AgentState)
        graph.add_node("llm", self.call_llm)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()

        self.sys_prompt = system_prompt
        self.tools = {t.name: t for t in user_tools}
        self.model = model.bind_tools(user_tools)

    def exists_action(self, state: AgentState):
        last_message = state["messages"][-1]
        return len(last_message.tool_calls) > 0

    def call_llm(self, state: AgentState):
        msgs = state["messages"]
        if self.sys_prompt:
            msgs = [SystemMessage(content=self.sys_prompt)] + msgs
        llm_result = self.model.invoke(msgs)
        return {"messages": [llm_result]}

    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            results.append(ToolMessage(tool_call_id=tool_call['id'], name=tool_call['name'],
                                       content=self.tools[tool_name].invoke(tool_args)))
        return {"messages": results}


class WikiToolInput(BaseModel):
    query: str


class MyWikiTool(BaseTool):  # type: ignore[override]
    query: Optional[str] = Field(default="Pune", description="The thing that you want to look up")
    wiki: Optional[wikipediaapi.Wikipedia] = Field(description="Wikipedia API",
                                                   default=wikipediaapi.Wikipedia("test-agent", "en"))
    description: str = "Useful for when you need to answer questions about current events."
    args_schema: Type[BaseModel] = WikiToolInput
    name: str = "wiki"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _run(self, query: str) -> str:
        page = self.wiki.page(query)
        if page.exists():
            return page.summary
        else:
            return "No page found"


if __name__ == "__main__":
    config = Configuration("../config.json")
    prompt = """You are a smart research assistant. Use the search engine to look up information. \
    You are allowed to make multiple calls (either together or in sequence). \
    Only look up information when you are sure of what you want. \
    If you need to look up some information before asking a follow up question, you are allowed to do that!
    """
    llm = AzureChatOpenAI(api_key=config.azure_open_ai_config["api_key"],
                          azure_endpoint=config.azure_open_ai_config["azure_endpoint"],
                          azure_deployment=config.azure_open_ai_config["model"],
                          api_version=config.azure_open_ai_config["api_version"])

    search_tool = TavilySearch(max_results=2, topic="general")
    wikitool = MyWikiTool()
    tools = [search_tool, wikitool]
    agent = LangGraphAgent(llm, tools, prompt)
    messages = [HumanMessage(
        content="Is there any wiki article about Cricket? If so, is it a good weather to play Cricket in Pune now?")]
    result = agent.graph.invoke({"messages": messages})
    print(result['messages'][-1].content)
