
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
from modules import tools, resources, prompts
# Initialize logger
logger = get_logger(__name__)


async def register_resources(mcp: FastMCP):
    # ============= Register Resources =============

    @mcp.resource(
        "jira://active-users",
        name="Active Users",
        description="Active Atlassian users for assignment and mentions"
    )
    async def active_users() -> str:
        """Active Atlassian users for assignment and mentions"""
        return await resources.get_active_users()


    @mcp.resource(
        "jira://current-user/info",
        name="Current User Info",
        description="Current authenticated user information"
    )
    async def current_user() -> str:
        """Current authenticated user information"""
        return await resources.get_jira_current_user_info()


    @mcp.resource(
        "jira://my-issues",
        name="My Issues",
        description="Issues assigned to current user"
    )
    async def my_issues() -> str:
        """Issues assigned to current user"""
        return await resources.get_jira_my_issues()


    @mcp.resource(
        "jira://recent-issues",
        name="Recent Issues",
        description="Recently updated issues (last 7 days)"
    )
    async def recent_issues() -> str:
        """Recently updated issues (last 7 days)"""
        return await resources.get_jira_recent_issues()


    @mcp.resource(
        "jira://projects/list",
        name="Projects List",
        description="List of all accessible projects"
    )
    async def projects_list() -> str:
        """List of all accessible projects"""
        return await resources.get_jira_projects_list()


    @mcp.resource(
        "jira://metadata/issue-types",
        name="Issue Types",
        description="All available issue types with their schemas"
    )
    async def issue_types() -> str:
        """All available issue types with their schemas"""
        return await resources.get_jira_metadata_issue_types()


    @mcp.resource(
        "jira://metadata/priorities",
        name="Priorities",
        description="Available priority levels"
    )
    async def priorities() -> str:
        """Available priority levels"""
        return await resources.get_jira_metadata_priorities()


    @mcp.resource(
        "jira://metadata/statuses",
        name="Statuses",
        description="Available statuses and status categories"
    )
    async def statuses() -> str:
        """Available statuses and status categories"""
        return await resources.get_jira_metadata_statuses()


    @mcp.resource(
        "jira://adf-examples",
        name="ADF Examples",
        description="ADF formatting examples and patterns"
    )
    async def adf_examples() -> str:
        """ADF formatting examples and patterns"""
        return await resources.get_jira_adf_examples()
