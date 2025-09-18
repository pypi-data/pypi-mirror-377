"""MCP AI Hub Server - Unified AI provider access via LiteLM."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .ai_client import AIClient
from .config import AIHubConfig

# Configure logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

# Global instances
ai_client: AIClient | None = None


async def initialize_client(config_path: Path | None = None) -> None:
    """Initialize the AI client with configuration."""
    global ai_client
    try:
        config = AIHubConfig.load_config(config_path)
        ai_client = AIClient(config)
        logger.info(f"Loaded configuration with {len(config.model_list)} models")
        for model in config.list_available_models():
            logger.info(f"Available model: {model}")
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        raise


def create_mcp_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("ai-hub", host=host, port=port)

    @mcp.tool()
    async def chat(model: str, inputs: str | list[dict[str, Any]]) -> str:
        """Chat with specified AI model.

        Args:
            model: Model name from configuration (e.g., 'gpt-4', 'claude-sonnet-4')
            inputs: Chat input (string or OpenAI-format messages)

        Returns:
            AI model response as string
        """
        global ai_client

        if ai_client is None:
            raise RuntimeError("AI client not initialized")

        try:
            response = ai_client.chat(model, inputs)
            return response
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise

    @mcp.tool()
    async def list_models() -> list[str]:
        """List all available AI models.

        Returns:
            List of available model names
        """
        global ai_client

        if ai_client is None:
            raise RuntimeError("AI client not initialized")

        return ai_client.list_models()

    @mcp.tool()
    async def get_model_info(model: str) -> dict[str, Any]:
        """Get information about a specific model.

        Args:
            model: Model name to get info for

        Returns:
            Dictionary with model information
        """
        global ai_client

        if ai_client is None:
            raise RuntimeError("AI client not initialized")

        return ai_client.get_model_info(model)

    return mcp


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI options."""
    parser = argparse.ArgumentParser(
        description="MCP AI Hub Server - Unified AI provider access via LiteLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport Types:
  stdio         Standard input/output (default for MCP clients)
  sse           Server-Sent Events (requires --host and --port)
  http          HTTP transport (requires --host and --port)

Examples:
  %(prog)s                           # Run with stdio transport
  %(prog)s --transport sse           # Run with SSE on default host/port
  %(prog)s --transport http --port 8080  # Run HTTP on port 8080
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport type to use (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to for sse/http transports (default: localhost)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port to bind to for sse/http transports (default: 3001)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file (default: ~/.ai_hub.yaml)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser


def main() -> None:
    """Main entry point for the MCP server."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Initialize the AI client synchronously
    async def init_client() -> None:
        await initialize_client(args.config)

    try:
        # Initialize the AI client
        asyncio.run(init_client())

        # Create MCP server with host/port configuration
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the MCP server with appropriate transport
        if args.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            mcp.run("stdio")
        elif args.transport == "sse":
            logger.info(
                f"Starting MCP server with SSE transport on {args.host}:{args.port}"
            )
            mcp.run("sse")
        elif args.transport == "http":
            logger.info(
                f"Starting MCP server with streamable-http transport on {args.host}:{args.port}"
            )
            mcp.run("streamable-http")

    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
