# mcp-polaris-ai-datainsight

[Polaris AI DataInsight](https://datainsight.polarisoffice.com/) is an API service that easily converts documents in various formats into structured data (such as JSON).

This tool supports the extraction of text, images, and other elements from various document formats (e.g. .docx, .pptx, .xlsx, .hwp, .hwpx).

For more details, please refer to the [documentation](https://datainsight.polarisoffice.com/documentation/overview).

## Features

### 1. Extract content from document
Extract text, images, and other elements from various document formats.
- Supported document formats : docx, xlsx, pptx, hwpx, hwp
- Supported elements types : text, table, image, chart, shape, header, footer, caption
- Images in the document are stored on local storage, and the corresponding image paths are included in the JSON output.
- Tables are represented in JSON format, as illustrated in [this example](examples/example_tool_output.json).

### 2. List files in allowed directories
List the files in the directory path set in the `POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR` environment variable (in the case of Docker, the path mounted to `/app/readable`).
- Used to retrieve file paths to be passed as arguments to the "Extract content from document" Tool.

## Installation and Setup

### Prerequisites

To use this server, follow these steps:
1. Generate an API key.
    - Refer to [this guide](https://datainsight.polarisoffice.com/documentation/quickstart) to generate an API key.

2. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).
3. Create a **writable** directory for storing extraction-result resources(e.g. images in files), and set its path in the `POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR` environment variable. 

After that, choose one of the installation methods below and start the server.

### Method 1: Manual Configuration

If you prefer a manual setup, add the following configuration to your IDE's MCP config file:

```json
{
  "mcpServers": {
    "datainsight": {
      "command": "uvx",
      "args": [
        "--no-cache", 
        "mcp-polaris-ai-datainsight@latest",
        "/abs/path/to/input-docs-1",
        "/abs/path/to/input-docs-2",
        "/abs/path/to/input-docs-3"
      ],
      "env": {
        "POLARIS_AI_DATA_INSIGHT_API_KEY": "your-api-key",
        "POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR": "/abs/path/to/output/assets"
      }
    }
  }
}
```

### Method 2: Docker Container

1. Clone repository
    ```sh
    git clone --branch main https://github.com/PolarisOffice/PolarisAIDataInsight.git
    ```
    If you want to clone only `mcp-polaris-ai-datainsight` directory:
    ```sh
    # Git Version >= 2.25
    git clone --filter=blob:none --sparse --branch main https://github.com/PolarisOffice/PolarisAIDataInsight.git
    ```
    ```sh
    cd PolarisAIDataInsight
    ```
    ```sh
    git sparse-checkout set mcp-polaris-ai-datainsight
    ```
2. Build Docker image:
    ```sh
    cd mcp-polaris-ai-datainsight

    docker build --no-cache -t mcp-polaris-ai-datainsight .
    ```
3. Use this MCP Server config:
    Note: All readable files must be mounted to `/app/readable` by default.
    ```json
    {
      "mcpServers": {
        "datainsight": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "-e", "POLARIS_AI_DATA_INSIGHT_API_KEY=your-api-key",
            "--mount", "type=bind,src=/abs/path/to/input-docs-1,dst=/app/readable/dir_1,ro",
            "--mount", "type=bind,src=/abs/path/to/input-docs-2,dst=/app/readable/dir_2,ro",
            "mcp-polaris-ai-datainsight"
          ]
        }
      }
    }
    ```

### Method 3: Clone git repository 

[!] Important: `uv` and `poetry` must be pre-installed.

1. Clone git repository
2. Install python dependencies in virtual environment
    ```sh
    cd mcp-polaris-ai-datainsight
    ```
    ```sh
    uv venv .venv

    # Linux
    source .venv/bin/activate
    # Windows
    .venv\bin\activate

    
    poetry install --no-root
    ```
3. Set API Key and Resources Directory as environment values and Run server
    ```sh
    # Linux
    export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    export POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR="/abs/path/to/output/assets"
    # Windows
    set POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    set POLARIS_AI_DATA_INSIGHT_RESOURCES_DIR="/abs/path/to/output/assets"
    ```
    ```sh
    python -m mcp_polaris_ai_datainsight.server /abs/path/to/input-docs-1 /abs/path/to/input-docs-1 ...
    ```

## Output

- Refer to [this example](examples/example_tool_output.json) for a sample output.
- Alternatively, you can test our API using the [playground](https://datainsight.polarisoffice.com/playground/doc-extract).
