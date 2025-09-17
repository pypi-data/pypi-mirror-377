from utils.api_client import make_request
from modules import tools
async def retrieve_issue_and_prepare_to_handle_task(issue_key: str) -> str:
    """Generates a prompt to retrieve a Jira issue, create a markdown document with issue details and task list, and prepare to handle the task."""    
    issue = tools.get_issue(issue_key)

    return f"Retrieve the issue {issue_key} from Jira using the following details:\n{issue}\n\nCreate a markdown document that includes the issue details and a task list for handling the issue.\n\nCheckout to a new branch for this issue (e.g. feature/{issue_key} or bugfix/{issue_key}).\n\nPrepare to handle the task as per the issue requirements."


async def register_prompts(mcp):
    @mcp.prompt
    async def retrieve_issue_and_prepare_to_handle_task(issue_key: str) -> str:
        """Generates a prompt to retrieve a Jira issue, create a markdown document with issue details and task list, and prepare to handle the task."""
        return await retrieve_issue_and_prepare_to_handle_task(issue_key)
