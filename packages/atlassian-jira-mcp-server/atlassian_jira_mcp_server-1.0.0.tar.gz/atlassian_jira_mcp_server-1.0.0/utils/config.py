"""
Configuration module for Jira MCP Server
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Jira Configuration - can be set via environment or .env file
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DEFAULT_PROJECT = os.getenv("JIRA_DEFAULT_PROJECT")

# Don't validate here - let the server handle missing config gracefully
# This allows the server to start and report configuration issues properly

# API Configuration
API_VERSION = "3"
BASE_URL = f"{JIRA_BASE_URL}/rest/api/{API_VERSION}"
DEFAULT_TIMEOUT = 30.0
MAX_RESULTS = 50  # Default pagination limit

# Server Configuration
SERVER_NAME = "jira_mcp"
SERVER_INSTRUCTIONS = """A comprehensive Jira Cloud MCP server for issue management, project operations, and search capabilities with rich ADF formatting support"""