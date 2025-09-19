import anyio

import minimcp_servers.modules.math as math
from minimcp_servers.core.builder import stdio_server_from_module
from minimcp_servers.core.logger import configure_logging

configure_logging()

stdio_server = stdio_server_from_module(math)


def main():
    anyio.run(stdio_server)


if __name__ == "__main__":
    main()
