import asyncio

from ai_agent_experiments.chat_bot import ChatBot
from ai_agent_experiments.config import Configuration


async def main() -> None:
    config = Configuration("./config.json")
    agent = ChatBot(config)
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