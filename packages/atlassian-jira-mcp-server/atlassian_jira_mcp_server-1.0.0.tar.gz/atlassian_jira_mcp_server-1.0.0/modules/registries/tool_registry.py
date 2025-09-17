
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


async def register_tools(mcp: FastMCP):
    # Issue Operations (9 tools)
    @mcp.tool(
        description="Get available workflow transitions for an issue",
        annotations={
            "title": "Get Issue Transitions",
            "readOnlyHint": True,
            "category": "issue"
        }
    )
    async def get_issue_transitions(issue_key: str) -> list:
        """Get available transitions for issue"""
        return await tools.get_issue_transitions(issue_key)

    # Disable - transitions are now included in get_issue by default
    get_issue_transitions.disable()


    @mcp.tool(
        description="Get single issue by key with all details including fields, comments, metadata, and available transitions",
        annotations={
            "title": "Get Issue Details",
            "readOnlyHint": True,
            "category": "issue"
        }
    )
    async def get_issue(issue_key: str, expand: str = "", include_transitions: bool = True) -> dict:
        """Get complete issue details with transitions"""
        return await tools.get_issue(issue_key, expand or None, include_transitions)


    @mcp.tool(
        description="Search issues using JQL (Jira Query Language) with pagination support",
        annotations={
            "title": "Search Issues",
            "readOnlyHint": True,
            "category": "issue"
        }
    )
    async def search_issues(
        jql: str,
        fields: list = None,
        expand: str = "",
        max_results: int = 50,
        start_at: int = 0
    ) -> dict:
        """Search for issues using JQL"""
        return await tools.search_issues(jql, fields, expand or None, max_results, start_at)


    @mcp.tool(
        description="Create a new issue in Jira with automatic ADF formatting for description",
        annotations={
            "title": "Create Issue",
            "destructiveHint": False,
            "category": "issue"
        }
    )
    async def create_issue(
        project_key: str,
        issue_type: str,
        summary: str,
        description: str = "",
        assignee: str = "",
        priority: str = "",
        labels: list = None,
        components: list = None,
        fix_versions: list = None,
        parent_key: str = "",
        custom_fields: dict = None
    ) -> dict:
        """Create a new issue"""
        return await tools.create_issue(
            project_key,
            issue_type,
            summary,
            description or None,
            assignee or None,
            priority or None,
            labels,
            components,
            fix_versions,
            parent_key or None,
            custom_fields
        )


    # Original update_issue tool
    @mcp.tool(
        description="Update an existing issue with automatic ADF formatting for description",
        annotations={
            "title": "Update Issue (Original)",
            "destructiveHint": False,
            "category": "issue"
        }
    )
    async def update_issue_original(
        issue_key: str,
        summary: str = "",
        description: str = "",
        assignee: str = "",
        priority: str = "",
        labels: list = None,
        components: list = None,
        fix_versions: list = None,
        custom_fields: dict = None,
        notify_users: bool = True
    ) -> dict:
        """Update an existing issue"""
        return await tools.update_issue(
            issue_key,
            summary or None,
            description or None,
            assignee or None,
            priority or None,
            labels,
            components,
            fix_versions,
            custom_fields,
            notify_users
        )

    # Custom handler for unified update_issue
    async def unified_update_issue(
        issue_key: str,
        summary: str = "",
        description: str = "",
        assignee: str = "",
        priority: str = "",
        labels: list = None,
        components: list = None,
        fix_versions: list = None,
        custom_fields: dict = None,
        notify_users: bool = True,
        # New parameters for unified functionality
        transition: str = "",
        resolution: str = "",
        comment: str = "",
        comment_visibility: dict = None,
        mentions: list = None,
        delete: bool = False,
        delete_subtasks: bool = False
    ):
        """Unified handler that delegates to appropriate tools based on parameters"""
        # Handle delete
        if delete:
            return await tools.delete_issue(issue_key, delete_subtasks)

        # Handle transition
        if transition:
            await tools.transition_issue(
                issue_key,
                transition,
                comment or None,
                resolution or None,
                None  # Additional fields not supported in unified version for simplicity
            )

        # Handle field updates
        has_updates = any([summary, description, assignee, priority, labels, components, fix_versions, custom_fields])
        if has_updates:
            await tools.update_issue(
                issue_key,
                summary or None,
                description or None,
                assignee or None,
                priority or None,
                labels,
                components,
                fix_versions,
                custom_fields,
                notify_users
            )

        # Handle comment (if not already added with transition)
        if comment and not transition:
            await tools.add_comment(
                issue_key,
                comment,
                comment_visibility,
                mentions
            )

        return await tools.get_issue(issue_key)

    # Create unified update_issue from the original using transform_fn
    update_issue = Tool.from_tool(
        update_issue_original,
        name="update_issue",
        description="Unified issue update - handles field updates, transitions, comments, assignment, and deletion",
        transform_fn=unified_update_issue,
        annotations={
            "title": "Update Issue",
            "destructiveHint": False,
            "category": "issue",
            "help": "Combines field updates, transitions, comments, assignment, and deletion"
        }
    )

    mcp.add_tool(update_issue)

    # Disable the original
    update_issue_original.disable()


    @mcp.tool(
        description="Delete an issue from Jira",
        annotations={
            "title": "Delete Issue",
            "destructiveHint": True,
            "category": "issue"
        }
    )
    async def delete_issue(issue_key: str, delete_subtasks: bool = False) -> dict:
        """Delete an issue"""
        return await tools.delete_issue(issue_key, delete_subtasks)

    # Disable - now handled by unified update_issue
    delete_issue.disable()


    @mcp.tool(
        description="Add a comment to an issue with automatic ADF formatting and optional mentions",
        annotations={
            "title": "Add Comment",
            "destructiveHint": False,
            "category": "issue"
        }
    )
    async def add_comment(
        issue_key: str,
        body: str,
        visibility: dict = None,
        mentions: list = None
    ) -> dict:
        """Add comment to issue"""
        return await tools.add_comment(issue_key, body, visibility, mentions)

    # Disable - now handled by unified update_issue
    add_comment.disable()


    @mcp.tool(
        description="Transition an issue to a different status in the workflow (use get_issue_transitions to find valid transition IDs)",
        annotations={
            "title": "Transition Issue",
            "destructiveHint": False,
            "category": "issue"
        }
    )
    async def transition_issue(
        issue_key: str,
        transition_id: str,
        comment: str = "",
        resolution: str = "",
        fields: dict = None
    ) -> dict:
        """Change issue status"""
        return await tools.transition_issue(
            issue_key,
            transition_id,
            comment or None,
            resolution or None,
            fields
        )

    # Disable - now handled by unified update_issue
    transition_issue.disable()


    @mcp.tool(
        description="Assign or unassign an issue to a user (supports email or account ID)",
        annotations={
            "title": "Assign Issue",
            "destructiveHint": False,
            "category": "issue"
        }
    )
    async def assign_issue(issue_key: str, assignee: str = "") -> dict:
        """Assign issue to user"""
        return await tools.assign_issue(issue_key, assignee or None)

    # Disable - now handled by unified update_issue
    assign_issue.disable()


    # Project & Metadata Tools (4 tools)
    @mcp.tool(
        description="Get project details and configuration including issue types and workflows",
        annotations={
            "title": "Get Project Details",
            "readOnlyHint": True,
            "category": "project"
        }
    )
    async def get_project(project_key: str, expand: str = "") -> dict:
        """Get project information"""
        return await tools.get_project(project_key, expand or None)


    @mcp.tool(
        description="List all accessible projects with optional filtering",
        annotations={
            "title": "List Projects",
            "readOnlyHint": True,
            "category": "project"
        }
    )
    async def list_projects(recent: int = 0, expand: str = "", project_type: str = "") -> list:
        """List all projects"""
        return await tools.list_projects(recent, expand or None, project_type or None)

    # Disable as requested
    list_projects.disable()


    @mcp.tool(
        description="Get project components available for issue assignment",
        annotations={
            "title": "Get Project Components",
            "readOnlyHint": True,
            "category": "project"
        }
    )
    async def get_project_components(project_key: str) -> list:
        """Get project components"""
        return await tools.get_project_components(project_key)

    # Disable as requested
    get_project_components.disable()


    @mcp.tool(
        description="Get available issue types for a project with their required fields",
        annotations={
            "title": "Get Project Issue Types",
            "readOnlyHint": True,
            "category": "project"
        }
    )
    async def get_project_issue_types(project_key: str) -> list:
        """Get issue types for project"""
        return await tools.get_project_issue_types(project_key)

    # Disable as requested
    get_project_issue_types.disable()


    # User & Search Tools (2 tools)
    @mcp.tool(
        description="Search for users by name or email for assignment and mentions",
        annotations={
            "title": "Search Users",
            "readOnlyHint": True,
            "category": "user"
        }
    )
    async def search_users(query: str, max_results: int = 50, include_inactive: bool = False) -> list:
        """Search for Jira users"""
        return await tools.search_users(query, max_results, include_inactive)

    # Disable as requested
    search_users.disable()


    @mcp.tool(
        description="Get current authenticated user information",
        annotations={
            "title": "Get Current User",
            "readOnlyHint": True,
            "category": "user"
        }
    )
    async def get_current_user(expand: str = "") -> dict:
        """Get current user info"""
        return await tools.get_current_user(expand or None)

    # Disable as requested
    get_current_user.disable()


    # Convenience Filter Tools (3 tools)
    @mcp.tool(
        description="Get issues assigned to the current authenticated user",
        annotations={
            "title": "Get My Issues",
            "readOnlyHint": True,
            "category": "filter"
        }
    )
    async def get_my_issues(status: str = "open", max_results: int = 50) -> dict:
        """Get my assigned issues"""
        return await tools.get_my_issues(status, max_results)

    # Disable as requested
    get_my_issues.disable()


    @mcp.tool(
        description="Get recently updated issues within specified number of days",
        annotations={
            "title": "Get Recent Issues",
            "readOnlyHint": True,
            "category": "filter"
        }
    )
    async def get_recent_issues(days: int = 7, project_key: str = "", max_results: int = 50) -> dict:
        """Get recently updated issues"""
        return await tools.get_recent_issues(days, project_key or None, max_results)

    # Disable as requested
    get_recent_issues.disable()


    @mcp.tool(
        description="Get issues filtered by specific status name",
        annotations={
            "title": "Get Issues By Status",
            "readOnlyHint": True,
            "category": "filter"
        }
    )
    async def get_issues_by_status(
        status: str,
        project_key: str = "",
        assignee: str = "",
        max_results: int = 50
    ) -> dict:
        """Get issues by status"""
        return await tools.get_issues_by_status(status, project_key or None, assignee or None, max_results)

    # Disable as requested
    get_issues_by_status.disable()

