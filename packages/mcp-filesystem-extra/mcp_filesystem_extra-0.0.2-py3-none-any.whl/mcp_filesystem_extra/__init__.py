from mcp_filesystem_extra.server import serve


def main():
    """MCP Filesystem Extra"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()