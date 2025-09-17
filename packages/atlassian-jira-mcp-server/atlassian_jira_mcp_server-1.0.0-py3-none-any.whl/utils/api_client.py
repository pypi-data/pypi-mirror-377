"""
API Client module for Jira MCP Server
Handles HTTP requests to Jira Cloud API with authentication
"""

import httpx
from typing import Optional, Dict, Any, List
from .config import BASE_URL, DEFAULT_TIMEOUT
from .auth import get_auth_headers
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


async def make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    accept_type: Optional[str] = None
) -> Any:
    """
    Make authenticated request to Jira Cloud API

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path (can be full URL or relative path)
        params: Query parameters
        json_data: JSON body data
        headers: Additional headers
        accept_type: Override Accept header for specific content types

    Returns:
        Response data (dict, list, or str depending on content type)

    Raises:
        httpx.HTTPStatusError: If request fails
    """
    # Determine if endpoint is full URL or relative
    if endpoint.startswith('http'):
        url = endpoint
    else:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    auth_headers = get_auth_headers()

    # Override Accept header if specified
    if accept_type:
        auth_headers["Accept"] = accept_type

    # Merge additional headers
    if headers:
        auth_headers.update(headers)

    logger.debug(f"Making {method} request to {url}")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=auth_headers,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get("content-type", "")

            if response.status_code == 204:  # No content
                return {"success": True}
            elif content_type.startswith("text/"):
                return response.text
            else:
                # Default to JSON
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            # Try to parse error message from Jira
            try:
                error_data = e.response.json()
                error_messages = []

                # Handle Jira's error format
                if "errorMessages" in error_data:
                    error_messages.extend(error_data["errorMessages"])
                if "errors" in error_data:
                    for field, msg in error_data["errors"].items():
                        # Add specific guidance for component errors
                        if field.lower() == "components" or "component" in msg.lower():
                            error_messages.append(f"{field}: {msg}")
                            error_messages.append("Tip: Use component names like ['fe-main'] or objects like [{'id': '10398'}]")
                        # Add specific guidance for transition errors
                        elif "transition" in field.lower() or "transition" in msg.lower():
                            error_messages.append(f"{field}: {msg}")
                            error_messages.append("Tip: Use transition names like 'Closed' or IDs like '241'")
                        else:
                            error_messages.append(f"{field}: {msg}")

                if error_messages:
                    raise Exception(f"Jira API Error: {'; '.join(error_messages)}")
            except:
                pass
            raise


async def paginated_request(
    endpoint: str,
    params: Optional[Dict] = None,
    max_results: int = 50,
    limit: Optional[int] = None
) -> List[Any]:
    """
    Make paginated requests to Jira API

    Args:
        endpoint: API endpoint
        params: Query parameters
        max_results: Results per page
        limit: Maximum total results to return

    Returns:
        List of all results
    """
    if params is None:
        params = {}

    all_results = []
    start_at = 0

    while True:
        params.update({
            "startAt": start_at,
            "maxResults": max_results
        })

        response = await make_request("GET", endpoint, params=params)

        # Handle different Jira pagination formats
        if "values" in response:  # Some endpoints use 'values'
            results = response["values"]
            total = response.get("total", 0)
        elif "issues" in response:  # Search endpoint uses 'issues'
            results = response["issues"]
            total = response.get("total", 0)
        else:
            # Non-paginated response
            return response if isinstance(response, list) else [response]

        all_results.extend(results)

        # Check if we've reached the limit
        if limit and len(all_results) >= limit:
            return all_results[:limit]

        # Check if there are more results
        start_at += max_results
        if start_at >= total or not results:
            break

    return all_results