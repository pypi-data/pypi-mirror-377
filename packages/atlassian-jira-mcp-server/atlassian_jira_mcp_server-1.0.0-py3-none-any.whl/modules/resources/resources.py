"""
Resource definitions for Jira MCP Server
Contains all 8 resource functions for accessing common Jira data
"""

import json
from utils.api_client import make_request
from utils.config import JIRA_DEFAULT_PROJECT, MAX_RESULTS
from modules import tools
from fastmcp.utilities.logging import get_logger
logger = get_logger(__name__)

# Resource function implementations

async def get_active_users() -> str:
    """Get active Atlassian users for assignment and mentions"""
    try:
        # Search for all active users
        response = await make_request("GET", "users/search", params={
            "maxResults": 100
        })

        # Filter for active Atlassian accounts only
        active_users = [
            {
                "displayName": user.get("displayName"),
                "accountId": user.get("accountId")
            }
            for user in response
            if user.get("active", False) and user.get("accountType") == "atlassian"
        ]

        data = {
            "users": active_users,
            "count": len(active_users)
        }

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def get_jira_current_user_info() -> str:
    """Current authenticated user information"""
    try:
        user = await tools.get_current_user(expand="groups,applicationRoles")
        return json.dumps(user, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_my_issues() -> str:
    """Issues assigned to current user"""
    try:
        issues = await tools.get_my_issues(status="open", max_results=50)
        return json.dumps(issues, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_recent_issues() -> str:
    """Recently updated issues (last 7 days)"""
    try:
        issues = await tools.get_recent_issues(days=7, max_results=50)
        return json.dumps(issues, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_projects_list() -> str:
    """List of all accessible projects"""
    try:
        projects = await tools.list_projects(expand="description,lead")

        # Format for easier consumption
        formatted = []
        for project in projects:
            formatted.append({
                "key": project.get("key"),
                "name": project.get("name"),
                "description": project.get("description", ""),
                "projectTypeKey": project.get("projectTypeKey"),
                "lead": project.get("lead", {}).get("displayName") if "lead" in project else None,
                "avatarUrls": project.get("avatarUrls", {}),
                "id": project.get("id")
            })

        data = {
            "projects": formatted,
            "count": len(formatted)
        }

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_metadata_issue_types() -> str:
    """All available issue types with their schemas"""
    try:
        # Get issue types from all projects
        projects = await tools.list_projects()
        issue_types_map = {}

        for project in projects[:10]:  # Limit to first 10 projects to avoid too many requests
            try:
                issue_types = await tools.get_project_issue_types(project["key"])
                for issue_type in issue_types:
                    type_id = issue_type.get("id")
                    if type_id not in issue_types_map:
                        issue_types_map[type_id] = {
                            "id": type_id,
                            "name": issue_type.get("name"),
                            "description": issue_type.get("description", ""),
                            "iconUrl": issue_type.get("iconUrl"),
                            "subtask": issue_type.get("subtask", False),
                            "hierarchyLevel": issue_type.get("hierarchyLevel", 0),
                            "projects": []
                        }
                    issue_types_map[type_id]["projects"].append(project["key"])
            except:
                continue

        data = {
            "issueTypes": list(issue_types_map.values()),
            "count": len(issue_types_map)
        }

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_metadata_priorities() -> str:
    """Available priority levels"""
    try:
        priorities = await make_request("GET", "priority")

        # Format priority data
        formatted = []
        for priority in priorities:
            formatted.append({
                "id": priority.get("id"),
                "name": priority.get("name"),
                "description": priority.get("description", ""),
                "iconUrl": priority.get("iconUrl"),
                "statusColor": priority.get("statusColor")
            })

        data = {
            "priorities": formatted,
            "count": len(formatted),
            "default": next((p for p in formatted if p.get("name") == "Medium"), formatted[0] if formatted else None)
        }

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_metadata_statuses() -> str:
    """Available statuses and status categories"""
    try:
        statuses = await make_request("GET", "status")

        # Group by category
        categories = {}
        for status in statuses:
            category = status.get("statusCategory", {}).get("name", "Unknown")
            if category not in categories:
                categories[category] = {
                    "name": category,
                    "key": status.get("statusCategory", {}).get("key"),
                    "colorName": status.get("statusCategory", {}).get("colorName"),
                    "statuses": []
                }
            categories[category]["statuses"].append({
                "id": status.get("id"),
                "name": status.get("name"),
                "description": status.get("description", ""),
                "iconUrl": status.get("iconUrl")
            })

        data = {
            "categories": categories,
            "allStatuses": statuses,
            "count": len(statuses)
        }

        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def get_jira_adf_examples() -> str:
    """ADF formatting examples and patterns"""
    content = """# Jira ADF (Atlassian Document Format) Examples

## Overview
The Jira MCP Server automatically converts plain text and markdown to ADF format.
You can use these formats in description and comment fields.

## Plain Text
Simply provide plain text, and it will be converted to properly formatted ADF paragraphs.

Example:
```
This is a simple description.

This is a second paragraph.
```

## Markdown Support

### Headers
```markdown
# Header 1
## Header 2
### Header 3
```

### Text Formatting
```markdown
**Bold text**
*Italic text*
`inline code`
```

### Lists
```markdown
Bullet list:
- Item 1
- Item 2
- Item 3

Numbered list:
1. First item
2. Second item
3. Third item
```

### Code Blocks
```markdown
```python
def hello_world():
    print("Hello, World!")
```
```

### Links
```markdown
[Link text](https://example.com)
```

## Structured Issue Descriptions

Use the create_issue tool with structured content:

```python
await create_issue(
    project_key="PROJ",
    issue_type="Story",
    summary="Implement user authentication",
    description=\"\"\"
## Overview
Implement OAuth 2.0 authentication for the application.

## Acceptance Criteria
- Users can sign in with Google
- Users can sign in with GitHub
- Session management is secure
- Refresh tokens are properly handled

## Technical Details
Use the Auth0 SDK for implementation.
\"\"\"
)
```

## Comments with Mentions

When adding comments, you can mention users:

```python
await add_comment(
    issue_key="PROJ-123",
    body="The implementation is complete. Please review.",
    mentions=["accountId1", "accountId2"]
)
```

## Common Patterns

### Bug Report Template
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Browser: Chrome 120
- OS: macOS 14.0
```

### User Story Template
```markdown
## Story
As a [type of user]
I want [goal]
So that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
Implementation details here
```

## JQL Query Examples

### Common Searches
- My open issues: `assignee = currentUser() AND statusCategory != Done`
- Recent updates: `updated >= -7d ORDER BY updated DESC`
- High priority bugs: `priority = High AND issuetype = Bug`
- Sprint backlog: `sprint in openSprints() AND project = PROJ`
- Unassigned issues: `assignee is EMPTY`

### Advanced JQL
- Issues with comments: `comment ~ "search text"`
- Created this week: `created >= startOfWeek()`
- Due this month: `due <= endOfMonth()`
- Has attachments: `attachments is not EMPTY`
- Labeled issues: `labels in (backend, frontend)`

## Tips

1. **Rich Formatting**: The server automatically handles ADF conversion, so you can focus on content.

2. **Mentions**: Use account IDs (not usernames) for mentions to work properly.

3. **Custom Fields**: Pass custom fields as a dictionary in the `custom_fields` parameter.

4. **Transitions**: Issues automatically include available transitions:
   ```python
   # Get issue with transitions included automatically
   issue = await get_issue("PROJ-123")
   # Access transitions and summary
   transitions = issue["transitions"]
   summary = issue["transitions_summary"]

   # Or get transitions separately
   transitions = await get_issue_transitions("PROJ-123")
   ```

5. **Bulk Operations**: Use JQL searches to find issues, then iterate to update:
   ```python
   results = await search_issues("project = PROJ AND status = 'To Do'")
   for issue in results["issues"]:
       await transition_issue(issue["key"], transition_id="21")
   ```
"""

    return content

async def issue_resource_iterator(mcp):
    logger.info("Fetching recent issues for resource registration...")

    # Build bounded JQL query - include time restriction to satisfy new API requirements
    if JIRA_DEFAULT_PROJECT:
        jql_query = f"project = {JIRA_DEFAULT_PROJECT} AND updated >= -30d ORDER BY updated DESC"
    else:
        # If no default project, use a time-bounded query
        jql_query = "updated >= -7d ORDER BY updated DESC"
    issues_tool = await tools.search_issues(
        jql=jql_query,
        max_results=MAX_RESULTS or 50,
        start_at=0
    )
    issues = issues_tool.get("data", {}).get("issues", [])


    for issue in issues[:MAX_RESULTS]:  # Limit to MAX_RESULTS issues for resource registration
        issue_key = issue["key"]
        logger.info(f"Registered resource for issue {issue_key}")

        def create_issue_reader(key):
            @mcp.resource(f"jira://my-issues/{key}", mime_type="text/plain", name=f"{key} Issue", description=f"Details of Jira issue {key}")
            async def read_jira_issue() -> dict:
                """Reads content from a specific Jira issue and returns it asynchronously."""
                issue = await tools.get_issue(key)
                return issue
            return read_jira_issue

        create_issue_reader(issue_key)

