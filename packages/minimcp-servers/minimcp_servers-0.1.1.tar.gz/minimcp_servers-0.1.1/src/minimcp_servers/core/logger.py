import logging
import os
import sys


def configure_logging() -> None:
    # Configure logging globally for stdio MCP server
    log_file = os.environ.get("MCP_SERVER_LOG_FILE", "mcp_server.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(stream=sys.stderr),  # Also log to stderr
        ],
    )
