import json
from dataclasses import dataclass, field
from typing import Optional, Union


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
    """Configuration for a MCP server using the SSE transport."""
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
        except json.JSONDecodeError as e:
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


class MCPConfig:
    def __init__(self, path: str):
        self._config = _load_config(path)

    def get_config(self, server_name: str) -> StdioMCPConfig | StreamableMCPConfig:
        return self._config[server_name]


if __name__ == "__main__":
    config = MCPConfig("../config.json")
