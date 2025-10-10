import json
import os
from dataclasses import dataclass, field
from typing import Optional, Union

from dotenv import load_dotenv


@dataclass
class StdioMCPConfig:
    """Configuration for any MCP server using the stdio transport."""

    command: str
    """The executable to run to start the server."""

    args: list[str] = field(default_factory=list)
    """Command line arguments to pass to the executable."""

    env: dict[str, str] | None = None
    """The environment to use when spawning the process."""

    cwd: Optional[str] | None = None
    """The working directory to use when spawning the process."""


@dataclass
class StreamableMCPConfig:
    """Configuration for an MCP server using the SSE transport."""
    url: str
    """The URL of the SSE server."""
    headers: dict[str, str] | None = None
    """Additional headers to send to the SSE server."""


def _load_config(path) -> dict[str, Union[StdioMCPConfig, StreamableMCPConfig]]:
    with open(path, "r") as config_file:
        try:
            config_data = json.load(config_file)
            if "mcpServers" not in config_data and config_data["mcpServers"] is None:
                return {}
            else:
                try:
                    configs = {
                        name: _create_mcp_config(srv_config)
                        for name, srv_config in config_data["mcpServers"].items()
                    }
                    if None in configs.values():
                        raise ValueError("Invalid configuration found.")
                    return configs
                except (TypeError, ValueError) as e:
                    print(f"Error loading configuration from {path}: {e}")
                    return {}
        except json.JSONDecodeError:
            print(f"Error parsing MCP configuration named {path}")
            return {}


def _create_mcp_config(server: dict) -> StdioMCPConfig | StreamableMCPConfig | None:
    if "command" in server and server["command"] is not None:
        if "cwd" not in server:
            server["cwd"] = "."
        return StdioMCPConfig(**server)
    elif "url" in server and server["url"] is not None:
        return StreamableMCPConfig(**server)
    else:
        print("no command or url")
        return None


class Configuration:
    def __init__(self, path: str):
        load_dotenv()
        self._mcp_config = _load_config(path)
        self.azure_open_ai_config = {
            "api_key":  str.strip(str(os.getenv("AZURE_OPENAI_API_KEY", ""))),
            "azure_endpoint": str.strip(str(os.getenv("AZURE_OPENAI_ENDPOINT", ""))),
            "api_version" : str.strip(str(os.getenv("AZURE_OPENAI_API_VERSION","" ))),
            "model": str.strip(str(os.getenv("AZURE_OPENAI_DEPLOYMENT",""))),
            "inference_endpoint": str.strip(str(os.getenv("AZURE_INFERENCE_ENDPOINT", ""))),

        }
        self.faiss_server_config = {
            "path": str.strip(str(os.getenv("FAISS_EMBEDDINGS_SAVE_PATH", ""))),
            "dimension": os.getenv("FAISS_EMBEDDINGS_DIMENSION", 1536),
            "chunk_size": os.getenv("FAISS_CHUNK_SIZE", 1000),
            "chunk_overlap": os.getenv("FAISS_CHUNK_OVERLAP", 100),
            "embedding_metric": os.getenv("FAISS_EMBEDDING_METRIC", "cosine"),
        }
        self.anthropic_config = {
            "api_key": str.strip(str(os.getenv("ANTHROPIC_API_KEY", ""))),
        }



    def get_config(self, server_name: str) -> StdioMCPConfig | StreamableMCPConfig:
        return self._mcp_config[server_name]


if __name__ == "__main__":
    config = Configuration("../config.json")
