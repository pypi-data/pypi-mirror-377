import pytest
from mcp.types import TextContent
from mcp_json_to_csv.server import JsonToCsvServer


@pytest.fixture
def json_to_csv_server():
    return JsonToCsvServer()


@pytest.mark.asyncio
async def test_json_to_csv_valid_input(json_to_csv_server):
    input_json = '[{"name": "John", "age": 30}, {"name": "Alice", "age": 25}]'
    args = {"json_input": input_json}
    result = await json_to_csv_server.json_to_csv(args)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert (result[0].text == "name,age\r\nJohn,30\r\nAlice,25\r\n"
            or result[0].text == "name,age\nJohn,30\nAlice,25\n")


@pytest.mark.asyncio
async def test_json_to_csv_empty_input(json_to_csv_server):
    input_json = '[]'
    args = {"json_input": input_json}
    result = await json_to_csv_server.json_to_csv(args)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert result[0].text.startswith("Error: Input must be a non-empty list of dictionaries")


@pytest.mark.asyncio
async def test_json_to_csv_invalid_input(json_to_csv_server):
    input_json = 'not a json'
    args = {"json_input": input_json}
    result = await json_to_csv_server.json_to_csv(args)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert result[0].text.startswith("Error: ")
