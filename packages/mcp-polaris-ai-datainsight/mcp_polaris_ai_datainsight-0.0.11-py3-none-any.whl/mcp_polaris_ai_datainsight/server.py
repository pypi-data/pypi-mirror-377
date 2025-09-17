import logging
import sys
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
try:
    from .tools.datainsight_tool import call_datainsight_api
    from .tools.file_list_tool import list_files_in_directories
except ImportError:
    from mcp_polaris_ai_datainsight.tools.datainsight_tool import call_datainsight_api
    from mcp_polaris_ai_datainsight.tools.file_list_tool import list_files_in_directories

os.environ["PYTHONUTF8"] = "1"  # Enable UTF-8 mode for Python
logger = logging.getLogger(__name__)

# Parse command line arguments for allowed directories
allowed_directories = []
if len(sys.argv) > 1:
    allowed_directories = [Path(arg) for arg in sys.argv[1:]]

mcp = FastMCP("polaris-ai-datainsight", dependencies=["polaris_ai_datainsight"])

mcp.add_tool(
    fn=call_datainsight_api,
    name="extract_content_from_document",
    description="""
    Extract the contents of a document into a structured JSON format.
    `file_path` specifies the absolute path to the input document.
    Only works within allowed directories.
    """,
)

mcp.add_tool(
    fn=lambda: list_files_in_directories(allowed_directories),
    name="list_files_in_allowed_directories",
    description=
    """
    List all files in the allowed directories that were specified as command line arguments.
    Returns a list of absolute file paths for all files found in the allowed directories.
    """
)

def run():
    logger.info("Starting MCP server...")
    logger.info(f"Allowed directories: {allowed_directories}")
    mcp.run()


if __name__ == "__main__":
    run()
