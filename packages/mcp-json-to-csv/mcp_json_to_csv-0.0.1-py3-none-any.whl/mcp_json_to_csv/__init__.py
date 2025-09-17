from mcp_json_to_csv.server import serve


def main():
    """MCP JSON to CSV conversion"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()