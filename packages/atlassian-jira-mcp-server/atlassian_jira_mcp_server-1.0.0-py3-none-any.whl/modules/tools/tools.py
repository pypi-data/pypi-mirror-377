"""
Tool definitions for Jira MCP Server
Contains all 18 tool functions for interacting with Jira Cloud API
"""

from typing import Optional, List, Dict, Any, Literal
from utils.api_client import make_request, paginated_request
from utils.config import JIRA_DEFAULT_PROJECT, MAX_RESULTS
from modules.utilities import convert_to_adf, create_comment as create_adf_comment, format_issue_for_llm, resolve_components, resolve_transition_id
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


# ============= Issue Operations (9 tools) =============

async def get_issue_transitions(issue_key: str) -> List[Dict[str, Any]]:
    """
    Get available transitions for an issue

    Args:
        issue_key: Issue key (e.g., PROJ-123)

    Returns:
        List of available transitions with id, name, and target status
    """
    response = await make_request("GET", f"issue/{issue_key}/transitions")

    # Format transitions for easier use
    transitions = []
    for transition in response.get("transitions", []):
        transitions.append({
            "id": transition.get("id"),
            "name": transition.get("name"),
            "to": {
                "id": transition.get("to", {}).get("id"),
                "name": transition.get("to", {}).get("name"),
                "statusCategory": transition.get("to", {}).get("statusCategory", {}).get("name")
            } if "to" in transition else None,
            "hasScreen": transition.get("hasScreen", False),
            "isGlobal": transition.get("isGlobal", False),
            "isInitial": transition.get("isInitial", False),
            "isConditional": transition.get("isConditional", False)
        })

    return transitions


async def get_issue(issue_key: str, expand: Optional[str] = None, include_transitions: bool = True) -> Dict[str, Any]:
    """
    Get single issue by key with all details

    Args:
        issue_key: Issue key (e.g., PROJ-123)
        expand: Optional fields to expand (changelog, renderedFields, transitions)
        include_transitions: Whether to automatically fetch and include available transitions

    Returns:
        Formatted issue data with both 'content' (text) and 'data' (structured)
    """
    logger.info(f"Fetching issue {issue_key} with expand={expand} and include_transitions={include_transitions}")
    params = {}
    if expand:
        params["expand"] = expand

    issue = await make_request("GET", f"issue/{issue_key}", params=params)

    # Get available transitions automatically unless already expanded or disabled
    transitions_to_use = None

    # Check if transitions were included in the expand and are valid (not null)
    # Note: if "transitions" not in expand, the key won't exist in the response at all
    if "transitions" in issue and issue["transitions"] is not None:
        # Transitions were already fetched via expand parameter
        transitions_to_use = issue["transitions"]
    elif include_transitions:
        # Need to fetch transitions separately
        try:
            transitions_to_use = await get_issue_transitions(issue_key)
        except Exception as e:
            logger.debug(f"Could not fetch transitions for {issue_key}: {e}")
            transitions_to_use = []
    else:
        # Transitions disabled
        transitions_to_use = []

    # Format the response for better readability
    result = {
        "key": issue.get("key"),
        "id": issue.get("id"),
        "self": issue.get("self"),
        "fields": issue.get("fields", {}),
        "expand": issue.get("expand", ""),
        "changelog": issue.get("changelog") if "changelog" in issue else None
    }

    # Add transitions to result
    result["transitions"] = transitions_to_use
    logger.info(f"Found {len(transitions_to_use)} transitions for issue {issue_key}")

    # Format for LLM consumption
    return format_issue_for_llm(result)


async def search_issues(
    jql: str,
    fields: Optional[List[str]] = None,
    expand: Optional[str] = None,
    max_results: int = 50,
    start_at: int = 0
) -> Dict[str, Any]:
    """
    Search issues using JQL (Jira Query Language)

    Args:
        jql: JQL query string
        fields: List of fields to return
        expand: Fields to expand
        max_results: Maximum results to return
        start_at: Starting index for pagination

    Returns:
        Formatted search results with both 'content' (text) and 'data' (structured)
    """
    params = {
        "jql": jql,
        "maxResults": max_results,
        "startAt": start_at
    }

    # Always request fields to get full issue data (required for new /search/jql endpoint)
    if fields:
        params["fields"] = ",".join(fields)
    else:
        # Default to all fields if none specified
        params["fields"] = "*all"

    if expand:
        params["expand"] = expand

    response = await make_request("GET", "search/jql", params=params)

    # Format each issue for LLM consumption
    formatted_issues = []
    for issue in response.get("issues", []):
        formatted_issues.append(format_issue_for_llm(issue))

    # The new /search/jql endpoint doesn't return total, startAt, maxResults
    # It uses nextPageToken for pagination instead
    issues_count = len(formatted_issues)
    total_text = f"{issues_count}+" if response.get("nextPageToken") else str(issues_count)

    # Build simple text summary
    lines = [f"Found {total_text} issues (showing {issues_count}):"]
    for fi in formatted_issues:
        lines.append(f"\n{fi['content']}")

    return {
        "content": "\n".join(lines),
        "data": {
            "total": issues_count,  # Can't get exact total from new API
            "startAt": start_at,
            "maxResults": max_results,
            "issues": [fi["data"] for fi in formatted_issues],
            "nextPageToken": response.get("nextPageToken"),
            "isLast": response.get("isLast", True)
        }
    }


async def create_issue(
    project_key: str,
    issue_type: str,
    summary: str,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    components: Optional[List[str]] = None,
    fix_versions: Optional[List[str]] = None,
    parent_key: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new issue in Jira

    Args:
        project_key: Project key
        issue_type: Issue type name (Epic, Story, Task, Bug, etc.)
        summary: Issue summary/title
        description: Issue description (supports plain text, markdown, or ADF)
        assignee: Assignee account ID or email
        priority: Priority name
        labels: List of labels
        components: List of component names or IDs
        fix_versions: List of version names or IDs
        parent_key: Parent issue key for subtasks
        custom_fields: Dictionary of custom field IDs and values

    Returns:
        Created issue data
    """
    # Build issue fields
    fields = {
        "project": {"key": project_key},
        "issuetype": {"name": issue_type},
        "summary": summary
    }

    # Add description with ADF conversion
    if description:
        fields["description"] = convert_to_adf(description)

    # Add optional fields
    if assignee:
        # If email provided, need to look up account ID
        if "@" in assignee:
            users = await search_users(assignee)
            if users and len(users) > 0:
                assignee = users[0]["accountId"]
        fields["assignee"] = {"accountId": assignee}

    if priority:
        fields["priority"] = {"name": priority}

    if labels:
        fields["labels"] = labels

    if components:
        try:
            resolved_components = await resolve_components(components, project_key)
            if resolved_components:
                fields["components"] = resolved_components
        except ValueError as e:
            # Re-raise with more context
            raise ValueError(f"Component resolution failed: {e}")
        except Exception as e:
            # Fallback to old behavior if resolution fails for other reasons
            logger.warning(f"Component resolution failed, using fallback: {e}")
            fields["components"] = [{"name": c} if isinstance(c, str) else c for c in components]

    if fix_versions:
        fields["fixVersions"] = [{"name": v} if isinstance(v, str) else v for v in fix_versions]

    if parent_key:
        fields["parent"] = {"key": parent_key}

    # Add custom fields
    if custom_fields:
        fields.update(custom_fields)

    # Create the issue
    response = await make_request("POST", "issue", json_data={"fields": fields})

    # Return created issue details
    return await get_issue(response["key"])


async def update_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    components: Optional[List[str]] = None,
    fix_versions: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    notify_users: bool = True
) -> Dict[str, Any]:
    """
    Update an existing issue

    Args:
        issue_key: Issue key to update
        summary: New summary
        description: New description (supports plain text, markdown, or ADF)
        assignee: New assignee account ID or email
        priority: New priority
        labels: New labels (replaces existing)
        components: New components (replaces existing)
        fix_versions: New fix versions (replaces existing)
        custom_fields: Custom field updates
        notify_users: Whether to send notifications

    Returns:
        Updated issue data
    """
    fields = {}

    # Build update fields
    if summary is not None:
        fields["summary"] = summary

    if description is not None:
        fields["description"] = convert_to_adf(description)

    if assignee is not None:
        # Handle email to account ID conversion
        if "@" in assignee:
            users = await search_users(assignee)
            if users and len(users) > 0:
                assignee = users[0]["accountId"]
        fields["assignee"] = {"accountId": assignee} if assignee else None

    if priority is not None:
        fields["priority"] = {"name": priority}

    if labels is not None:
        fields["labels"] = labels

    if components is not None:
        try:
            resolved_components = await resolve_components(components, issue_key.split('-')[0])
            if resolved_components:
                fields["components"] = resolved_components
        except ValueError as e:
            # Re-raise with more context
            raise ValueError(f"Component resolution failed: {e}")
        except Exception as e:
            # Fallback to old behavior if resolution fails for other reasons
            logger.warning(f"Component resolution failed, using fallback: {e}")
            fields["components"] = [{"name": c} if isinstance(c, str) else c for c in components]

    if fix_versions is not None:
        fields["fixVersions"] = [{"name": v} if isinstance(v, str) else v for v in fix_versions]

    # Add custom fields
    if custom_fields:
        fields.update(custom_fields)

    # Update the issue
    params = {"notifyUsers": str(notify_users).lower()}
    await make_request("PUT", f"issue/{issue_key}", json_data={"fields": fields}, params=params)

    # Return updated issue
    return await get_issue(issue_key)


async def delete_issue(issue_key: str, delete_subtasks: bool = False) -> Dict[str, Any]:
    """
    Delete an issue

    Args:
        issue_key: Issue key to delete
        delete_subtasks: Whether to delete subtasks

    Returns:
        Success confirmation
    """
    params = {"deleteSubtasks": str(delete_subtasks).lower()}
    await make_request("DELETE", f"issue/{issue_key}", params=params)
    return {"success": True, "message": f"Issue {issue_key} deleted successfully"}


async def add_comment(
    issue_key: str,
    body: str,
    visibility: Optional[Dict[str, str]] = None,
    mentions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Add a comment to an issue

    Args:
        issue_key: Issue key
        body: Comment text (supports plain text, markdown, or ADF)
        visibility: Optional visibility restrictions (type: role/group, value: name)
        mentions: List of user account IDs to mention

    Returns:
        Created comment data
    """
    # Format comment with ADF
    if mentions:
        comment_body = create_adf_comment(body, mentions=mentions)
    else:
        comment_body = convert_to_adf(body)

    comment_data = {"body": comment_body}

    # Add visibility if specified
    if visibility:
        comment_data["visibility"] = visibility

    return await make_request("POST", f"issue/{issue_key}/comment", json_data=comment_data)


async def transition_issue(
    issue_key: str,
    transition_id: str,
    comment: Optional[str] = None,
    resolution: Optional[str] = None,
    fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transition an issue to a different status

    Args:
        issue_key: Issue key
        transition_id: Transition ID or name (e.g., "241" or "Closed")
        comment: Optional comment to add with transition
        resolution: Resolution name (for transitions to Done/Resolved)
        fields: Additional fields to update during transition

    Returns:
        Updated issue data
    """
    # Resolve transition name to ID if needed
    try:
        resolved_transition_id = await resolve_transition_id(transition_id, issue_key)
        logger.debug(f"Resolved transition '{transition_id}' to ID {resolved_transition_id}")
    except ValueError as e:
        # Re-raise with more context
        raise ValueError(f"Transition resolution failed: {e}")
    except Exception as e:
        # Fallback to original behavior if resolution fails for other reasons
        logger.warning(f"Transition resolution failed, using original value: {e}")
        resolved_transition_id = transition_id

    transition_data = {"transition": {"id": resolved_transition_id}}

    # Add optional fields
    if fields or resolution:
        transition_fields = fields or {}
        if resolution:
            transition_fields["resolution"] = {"name": resolution}
        transition_data["fields"] = transition_fields

    # Add comment if provided
    if comment:
        transition_data["update"] = {
            "comment": [{
                "add": {
                    "body": convert_to_adf(comment)
                }
            }]
        }

    await make_request("POST", f"issue/{issue_key}/transitions", json_data=transition_data)

    # Return updated issue
    return await get_issue(issue_key)


async def assign_issue(issue_key: str, assignee: Optional[str] = None) -> Dict[str, Any]:
    """
    Assign or unassign an issue

    Args:
        issue_key: Issue key
        assignee: Account ID, email, or None to unassign

    Returns:
        Updated issue data
    """
    # Handle email to account ID conversion
    if assignee and "@" in assignee:
        users = await search_users(assignee)
        if users and len(users) > 0:
            assignee = users[0]["accountId"]

    assign_data = {"accountId": assignee} if assignee else None

    await make_request("PUT", f"issue/{issue_key}/assignee", json_data=assign_data)

    return await get_issue(issue_key)


# ============= Project & Metadata (4 tools) =============

async def get_project(project_key: str, expand: Optional[str] = None) -> Dict[str, Any]:
    """
    Get project details and configuration

    Args:
        project_key: Project key
        expand: Fields to expand (description, lead, url, projectKeys)

    Returns:
        Project information
    """
    params = {}
    if expand:
        params["expand"] = expand

    return await make_request("GET", f"project/{project_key}", params=params)


async def list_projects(
    recent: int = 0,
    expand: Optional[str] = None,
    project_type: Optional[Literal["business", "software", "service_desk"]] = None
) -> List[Dict[str, Any]]:
    """
    List all accessible projects

    Args:
        recent: Number of recent projects (0 for all)
        expand: Fields to expand
        project_type: Filter by project type

    Returns:
        List of projects
    """
    params = {}
    if recent > 0:
        params["recent"] = recent
    if expand:
        params["expand"] = expand
    if project_type:
        params["typeKey"] = f"software" if project_type == "software" else project_type

    return await make_request("GET", "project", params=params)


async def get_project_components(project_key: str) -> List[Dict[str, Any]]:
    """
    Get project components for selection

    Args:
        project_key: Project key

    Returns:
        List of components with details
    """
    return await make_request("GET", f"project/{project_key}/components")


async def get_project_issue_types(project_key: str) -> List[Dict[str, Any]]:
    """
    Get available issue types for a project

    Args:
        project_key: Project key

    Returns:
        List of issue types with required fields
    """
    project = await get_project(project_key)
    return project.get("issueTypes", [])


# ============= User & Search (2 tools) =============

async def search_users(
    query: str,
    max_results: int = 50,
    include_inactive: bool = False
) -> List[Dict[str, Any]]:
    """
    Search for users (for assignment, mentions, etc.)

    Args:
        query: Search query (name, email, etc.)
        max_results: Maximum results
        include_inactive: Include inactive users

    Returns:
        List of matching users
    """
    params = {
        "query": query,
        "maxResults": max_results,
        "includeInactive": include_inactive
    }

    users = await make_request("GET", "user/search", params=params)

    # Format user data
    return [{
        "accountId": user.get("accountId"),
        "emailAddress": user.get("emailAddress"),
        "displayName": user.get("displayName"),
        "active": user.get("active"),
        "avatarUrls": user.get("avatarUrls", {})
    } for user in users]


async def get_current_user(expand: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current authenticated user information

    Args:
        expand: Fields to expand (groups, applicationRoles)

    Returns:
        Current user details
    """
    params = {}
    if expand:
        params["expand"] = expand

    return await make_request("GET", "myself", params=params)


# ============= Convenience Filters (3 tools) =============

async def get_my_issues(
    status: Optional[Literal["open", "in_progress", "done", "all"]] = "open",
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Get issues assigned to current user

    Args:
        status: Filter by status category
        max_results: Maximum results

    Returns:
        Issues assigned to current user
    """
    # Build JQL based on status
    jql_parts = ["assignee = currentUser()"]

    if status == "open":
        jql_parts.append("statusCategory != Done")
    elif status == "in_progress":
        jql_parts.append("statusCategory = 'In Progress'")
    elif status == "done":
        jql_parts.append("statusCategory = Done")
    # 'all' doesn't add status filter

    jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"

    return await search_issues(jql, max_results=max_results)


async def get_recent_issues(
    days: int = 7,
    project_key: Optional[str] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Get recently updated issues

    Args:
        days: Number of days to look back
        project_key: Optional project filter
        max_results: Maximum results

    Returns:
        Recently updated issues
    """
    jql_parts = [f"updated >= -{days}d"]

    if project_key:
        jql_parts.append(f"project = {project_key}")
    elif JIRA_DEFAULT_PROJECT:
        jql_parts.append(f"project = {JIRA_DEFAULT_PROJECT}")

    jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"

    return await search_issues(jql, max_results=max_results)


async def get_issues_by_status(
    status: str,
    project_key: Optional[str] = None,
    assignee: Optional[str] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Get issues filtered by specific status

    Args:
        status: Status name (e.g., "To Do", "In Progress", "Done")
        project_key: Optional project filter
        assignee: Optional assignee filter (email or account ID)
        max_results: Maximum results

    Returns:
        Issues matching the status filter
    """
    jql_parts = [f'status = "{status}"']

    if project_key:
        jql_parts.append(f"project = {project_key}")
    elif JIRA_DEFAULT_PROJECT:
        jql_parts.append(f"project = {JIRA_DEFAULT_PROJECT}")

    if assignee:
        # Handle email
        if "@" in assignee:
            users = await search_users(assignee)
            if users and len(users) > 0:
                assignee = users[0]["accountId"]
        jql_parts.append(f'assignee = "{assignee}"')

    jql = " AND ".join(jql_parts) + " ORDER BY priority DESC, created DESC"

    return await search_issues(jql, max_results=max_results)
