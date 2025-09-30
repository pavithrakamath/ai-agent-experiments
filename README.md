# AI Agent Experiments

A beginner-friendly starter template for building AI agents with Azure OpenAI. This repository demonstrates various AI agent patterns and architectures using modern Python libraries.

## Why This Repository?

Learning AI agent development can be overwhelming with complex frameworks and abstract concepts. This repository takes a different approach:

- **Read the code first** - Each file is designed to be simple and educational
- **Progressive complexity** - Start with basic Azure OpenAI, then move to LangChain
- **Real examples** - Working code you can run and modify immediately
- **No magic** - Everything is transparent and easy to understand

Perfect for developers who want to understand how AI agents actually work under the hood.

## Features

- Multiple AI agent architectures and patterns
- Tool calling and external API integration
- Web search and research capabilities
- RAG (Retrieval Augmented Generation) examples
- MCP (Model Context Protocol) integration
- Async/await support for better performance
- Easy setup with Poetry dependency management

## Quick Start

### Prerequisites

- Python 3.12+ 
- Azure OpenAI service access
- Poetry (for dependency management)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-agent-experiments.git
   cd ai-agent-experiments
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your Azure OpenAI credentials
   ```

4. **Configure your Azure OpenAI settings in `.env`:**
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   ```

## Getting Started

The best way to learn is by reading the code! Each file is designed to be simple and educational:

### Start Here - Read These Files (in order of complexity):

1. **`ai_agent_experiments/faiss_store.py`** - FAISS vector store for RAG implementation
2. **`rag.ipynb`** - RAG (Retrieval Augmented Generation) Jupyter notebook
3. **`ai_agent_experiments/mcp_stdio_client.py`** - MCP stdio client implementation
4. **`ai_agent_experiments/mcp_streamable_client.py`** - MCP streamable client implementation
5. **`lesson_01_basic_azure_openai.py`** - Basic Azure OpenAI (no LangChain)
6. **`lesson_02_react_pattern.py`** - ReAct pattern implementation (reasoning + acting)
7. **`lesson_03_langchain_basics.py`** - LangChain basics with Azure OpenAI
8. **`lesson_04_tool_calling_mcp.py`** - Conversational AI with tool calling and MCP
9. **`lesson_05_langgraph_advanced.py`** - Advanced agent workflows with LangGraph
10. **`main.py`** - Interactive chat interface

### Explore Foundation First:

```bash
# Start with RAG implementation (Jupyter notebook)
jupyter notebook rag.ipynb

# Explore the MCP infrastructure
# Read ai_agent_experiments/mcp_stdio_client.py
# Read ai_agent_experiments/mcp_streamable_client.py

# FAISS vector store (utility module)
# Read ai_agent_experiments/faiss_store.py to understand vector storage

# References and examples
jupyter notebook references/references.ipynb
```

### Then Try the Lessons:

```bash
# Basic Azure OpenAI
poetry run python lesson_01_basic_azure_openai.py

# ReAct pattern
poetry run python lesson_02_react_pattern.py

# LangChain basics
poetry run python lesson_03_langchain_basics.py

# Tool calling with MCP
poetry run python lesson_04_tool_calling_mcp.py

# Advanced LangGraph workflows
poetry run python lesson_05_langgraph_advanced.py

# Interactive chat with tool calling
poetry run python main.py
```

**Pro Tip**: Open each `.py` file in your editor and read through the code. The comments and structure are designed to teach you how AI agents work!

## Configuration

The project uses a simple configuration system:

- **Environment Variables**: Set in `.env` file (see `.env.template`)
- **MCP Servers**: Configured in `config.json`
- **Azure OpenAI**: All settings via environment variables

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you're running from the project root and have installed dependencies with `poetry install`

2. **Azure OpenAI connection issues**: Verify your `.env` file has the correct Azure OpenAI credentials

3. **MCP connection errors**: Ensure the research server is properly configured in `config.json`

4. **Import errors**: Make sure you're using Python 3.12+ and have activated the Poetry environment

### Getting Help

- Check the [Issues](https://github.com/yourusername/ai-agent-experiments/issues) page
- Review the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Explore the [LangChain documentation](https://python.langchain.com/)

## Learning Resources

- [Deep Learning Course on MCP](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic)
- [AI Agents with MCP](https://learning.oreilly.com/library/view/ai-agents-with/9798341639546/)
- [RAG Tutorial](https://youtu.be/bmduzd1oY7U)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Azure OpenAI team for the excellent API
- LangChain team for the amazing framework
- Anthropic for MCP protocol
- All the open-source contributors who made this possible

