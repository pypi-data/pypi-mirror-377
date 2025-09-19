import inspect
import logging
import sys
from collections.abc import Awaitable, Callable
from types import ModuleType

from minimcp import MiniMCP, stdio_transport

logger = logging.getLogger(__name__)


def mcp_from_module(module: ModuleType) -> MiniMCP:
    """
    Create a MiniMCP server from a Python module by automatically registering
    all public callable functions as tools.

    Args:
        module: The Python module to expose as MCP tools

    Returns:
        MiniMCP server instance with all module functions registered as tools
    """

    name = module.__name__
    version = getattr(module, "__version__", sys.version)
    instructions = module.__doc__ or f"MCP server for {module.__name__}"

    mcp = MiniMCP(name, version=version, instructions=instructions)

    # Get all public callable functions from the module
    functions = []
    for attr_name in dir(module):
        # Skip private/dunder methods
        if attr_name.startswith("_"):
            continue

        attr = getattr(module, attr_name)

        # Check if it's a callable function (regular function or builtin function)
        if callable(attr) and (inspect.isfunction(attr) or inspect.isbuiltin(attr)):
            functions.append((attr_name, attr))

    # Register each function as a tool
    registered_count = 0
    for func_name, func in functions:
        try:
            mcp.tool.add(func)
            registered_count += 1
            logger.debug("Registered function '%s' as tool", func_name)
        except Exception as e:  # noqa: PERF203
            logger.warning("Failed to register function '%s': %s", func_name, str(e))

    logger.info("Registered %d functions from module '%s' as MCP tools", registered_count, module.__name__)

    return mcp


def stdio_server_from_module(module: ModuleType) -> Callable[[], Awaitable[None]]:
    """
    Create a function that starts a MiniMCP server over stdio.

    Args:
        module: The Python module to expose as MCP tools

    Returns:
        A function that starts the MiniMCP server over stdio
    """

    mcp = mcp_from_module(module)

    async def stdio_server():
        logger.info("MiniMCP: Started %s server, listening for messages...", mcp.name)
        try:
            await stdio_transport(mcp.handle)
        except KeyboardInterrupt:
            logger.info("%s server shutting down gracefully...", mcp.name)

    return stdio_server
