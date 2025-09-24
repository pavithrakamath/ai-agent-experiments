# ai-agent-experiments

## Overview

This is an experimental project designed for beginners who want to explore the realm of AI. It provides simple, hands-on
examples of building intelligent agents using popular APIs and libraries.

- **ChatBot**: A basic AI-powered assistant that answers user queries using Azure OpenAI, with a focus on politeness and
  helpfulness.
- **ResearchAgent**: Demonstrates how to combine web search (DuckDuckGo) with Azure OpenAI to analyze and summarize
  search results for any query.

## Features

- Easy-to-understand conversational AI
- Web search integration and result analysis
- Simple configuration via environment variables

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ai-agent-experiments
   ```
2. **Install dependencies:**
   ```bash
   poetry install
   ```
3. **Set up environment variables:**
   Create a `.env` file in the project root with the following keys:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_VERSION=your_api_version
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   ```

## Usage

### ChatBot Example

```python
from ai_agent_experiments.chat_bot import ChatBot

bot = ChatBot()
response = bot.run("Hello, who are you?")
print(response)
```

### ResearchAgent Example

```python
from ai_agent_experiments.research_agent import ResearchAgent, search

agent = ResearchAgent()
results = search("What is AI?")
summary = agent.analyze(results, "What is AI?")
print(summary)
```

## License

MIT

## References

. [deep learning course on rich apps with mcp](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic)

. [AI Agents with MCP](https://learning.oreilly.com/library/view/ai-agents-with/9798341639546/)

. [RAG](https://youtu.be/bmduzd1oY7U)

. [Embedding models](https://platform.openai.com/docs/guides/embeddings)

