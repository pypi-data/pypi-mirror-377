"""
Jira MCP Server
A comprehensive MCP server for Jira Cloud integration with FastMCP
"""

import asyncio
import json
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform
from fastmcp.utilities.logging import get_logger
from utils.config import SERVER_NAME, SERVER_INSTRUCTIONS
from utils.config import JIRA_DEFAULT_PROJECT, MAX_RESULTS
from utils.api_client import make_request
from modules import tools, resources, prompts, registries
# Initialize logger
logger = get_logger(__name__)


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app):
    await resources.issue_resource_iterator(mcp)
    await registries.register_tools(mcp)
    await registries.register_resources(mcp)
    await prompts.register_prompts(mcp)
    logger.info("Dynamic issue resources registered")
    yield
    # Shutdown: Any cleanup if needed
    logger.info("Shutting down MCP server")

# Initialize FastMCP server with lifespan
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
    lifespan=lifespan,
)

# ============= Main Entry Point =============

def main():
    """Main entry point for the server"""
    # Check configuration before starting
    from utils.config import JIRA_BASE_URL, JIRA_USERNAME, JIRA_API_TOKEN

    if not JIRA_BASE_URL:
        logger.error("JIRA_BASE_URL environment variable is not set")
        logger.info("Please set: JIRA_BASE_URL=https://your-domain.atlassian.net")
        return

    if not JIRA_USERNAME:
        logger.error("JIRA_USERNAME environment variable is not set")
        logger.info("Please set: JIRA_USERNAME=your-email@domain.com")
        return

    if not JIRA_API_TOKEN:
        logger.error("JIRA_API_TOKEN environment variable is not set")
        logger.info("Please set: JIRA_API_TOKEN=your-api-token")
        logger.info("Create one at: https://id.atlassian.com/manage-profile/security/api-tokens")
        return

    logger.info(f"Starting {SERVER_NAME} server...")
    logger.info(f"Connected to: {JIRA_BASE_URL}")
    logger.info(f"Authenticated as: {JIRA_USERNAME}")

    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
