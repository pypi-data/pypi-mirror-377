# JSON to CSV Converter

---

A Model Context Protocol (MCP) server implementation for a simple tool that converts JSON arrays of objects to CSV format.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green)

---

# Table of Contents

1. [Description](#description)
2. [Usage](#usage)
3. [Avaliable Tools](#available-tools)
    - [json-to-csv](#json-to-csv)
9. [License](#license)

---

## Description

This tool provides a service that takes a JSON string containing an array of objects (dictionaries) and converts it to a CSV string. The first object's keys are used as the CSV header.

## Usage

This tool is designed to work as an MCP (Model Control Protocol) server. You can configure it in your project:

```json
{
    "mcpServers": {
        "json-to-csv": {
            "command": "uvx",
            "args": [
                "--index-url",
                "python_package_index_url",
                "--from",
                "mcp-json-to-csv",
                "json-to-csv"
                
            ]
        }
    }
}
```

## Available Tools

### `json-to-csv`

Converts a JSON array of objects to CSV format.

**Input Schema:**

```json
{
    "json_input": "JSON string to convert"
}
```

**Example Input:**

```json
{
    "json_input": "[{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25}]"
}
```

**Example Output:**

```csv
name,age
John,30
Jane,25
```

## Requirements

- Python 3.10+
- uv (https://docs.astral.sh/uv/getting-started/installation/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

 ---

For more information or support, please open an issue on the project repository.