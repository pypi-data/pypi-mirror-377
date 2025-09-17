"""
Authentication module for Jira MCP Server
Handles Basic Authentication for Jira Cloud API
"""

from base64 import b64encode
from typing import Dict
from .config import JIRA_USERNAME, JIRA_API_TOKEN


def get_auth_headers() -> Dict[str, str]:
    """
    Generate Basic Auth headers for Jira Cloud API

    Returns:
        Dict containing Authorization and Content-Type headers

    Raises:
        ValueError: If required environment variables are not set
    """
    if not JIRA_USERNAME or not JIRA_API_TOKEN:
        raise ValueError(
            "Missing Jira configuration. Please set JIRA_USERNAME and JIRA_API_TOKEN environment variables"
        )

    credentials = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
    encoded = b64encode(credentials.encode()).decode('ascii')

    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }