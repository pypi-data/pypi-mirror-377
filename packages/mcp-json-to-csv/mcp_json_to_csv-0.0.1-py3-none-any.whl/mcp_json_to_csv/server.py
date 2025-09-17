import json
import io
import csv

from enum import Enum
from typing import List
from pydantic import BaseModel

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

server = Server("json-to-csv")

class JsonToCsvTools(str, Enum):
    JSON_TO_CSV = "json-to-csv"

class JsonToCsvArgsSchema(BaseModel):
    json_input: str


class JsonToCsvServer:
    def __init__(self):
        pass

    async def json_to_csv(self, args: dict) -> str:
        try:
            parsed = JsonToCsvArgsSchema(**args)
            json_data = json.loads(parsed.json_input)

            if not json_data or not isinstance(json_data[0], dict):
                raise ValueError("Input must be a non-empty list of dictionaries")

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=json_data[0].keys())
            writer.writeheader()
            writer.writerows(json_data)

            csv_str = output.getvalue()
            return [types.TextContent(type="text", text=csv_str)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        finally:
            if 'output' in locals():
                output.close()


json_to_csv_server = JsonToCsvServer()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name=JsonToCsvTools.JSON_TO_CSV.value,
            description="""
            Converts JSON string with list of dictionaries to CSV string.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "json_input": {
                        "type": "string",
                        "description": "JSON string to convert.",
                    }
                },
                "required": ["json_input"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    try:
        match name:
            case JsonToCsvTools.JSON_TO_CSV.value:
                result = await json_to_csv_server.json_to_csv(arguments)
            case _:
                raise ValueError(f"Unknown tool: {name}")

        return result
    except Exception as e:
        raise ValueError(f"Error processing json-to-csv query: {str(e)}")


async def serve():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        options = server.create_initialization_options()
        await server.run(read_stream, write_stream, options)
