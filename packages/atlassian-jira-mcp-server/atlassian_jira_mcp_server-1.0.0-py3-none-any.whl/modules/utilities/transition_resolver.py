"""
Transition Resolution Utility for Jira MCP Server
Handles flexible transition input formats and auto-resolution from names to IDs
"""

from typing import Optional, Dict, Any, Union
from utils.api_client import make_request
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)

# Cache for transition mappings to avoid repeated API calls
_transition_cache = {}

async def get_issue_transitions_map(issue_key: str) -> Dict[str, str]:
    """
    Get transition name to ID mapping for an issue.

    Args:
        issue_key: Issue key (e.g., PROJ-123)

    Returns:
        Dictionary mapping transition names to IDs
    """
    # Check cache first
    if issue_key in _transition_cache:
        return _transition_cache[issue_key]

    try:
        # Fetch issue transitions
        response = await make_request("GET", f"issue/{issue_key}/transitions")
        transitions = response.get("transitions", [])

        # Create name -> id mapping
        transition_map = {}
        for transition in transitions:
            if 'name' in transition and 'id' in transition:
                # Store both exact name and lowercase for flexible matching
                name = transition['name']
                transition_id = transition['id']
                transition_map[name] = transition_id
                transition_map[name.lower()] = transition_id

        # Cache the mapping
        _transition_cache[issue_key] = transition_map
        logger.debug(f"Cached {len(transitions)} transitions for issue {issue_key}")

        return transition_map
    except Exception as e:
        logger.error(f"Failed to fetch transitions for issue {issue_key}: {e}")
        return {}

async def resolve_transition_id(
    transition: Union[str, int],
    issue_key: str
) -> str:
    """
    Resolve transition from name or ID to valid transition ID.

    Accepts:
    - Transition names: "Closed", "In Progress", "Code Review"
    - Transition IDs: "241", 241
    - Case-insensitive names: "closed", "CLOSED"

    Args:
        transition: Transition name or ID
        issue_key: Issue key for transition lookup

    Returns:
        Transition ID as string

    Raises:
        ValueError: If transition cannot be resolved
    """
    if not transition:
        raise ValueError("Transition cannot be empty")

    # Convert to string for consistent handling
    transition_str = str(transition)

    # Get transition name -> ID mapping
    transition_map = await get_issue_transitions_map(issue_key)

    # If it's already a valid transition ID, return it
    if transition_str in [tid for tid in transition_map.values()]:
        logger.debug(f"Transition '{transition_str}' is already a valid ID")
        return transition_str

    # Try exact name match first
    if transition_str in transition_map:
        resolved_id = transition_map[transition_str]
        logger.debug(f"Resolved transition '{transition_str}' to ID {resolved_id}")
        return resolved_id

    # Try case-insensitive match
    if transition_str.lower() in transition_map:
        resolved_id = transition_map[transition_str.lower()]
        logger.debug(f"Resolved transition '{transition_str}' (case-insensitive) to ID {resolved_id}")
        return resolved_id

    # Check if it's a numeric ID that exists
    try:
        # See if it's a numeric string that matches an existing ID
        for name, tid in transition_map.items():
            if tid == transition_str:
                logger.debug(f"Transition '{transition_str}' is a valid numeric ID")
                return transition_str
    except (ValueError, TypeError):
        pass

    # If we get here, the transition couldn't be resolved
    error_msg = format_transition_error(transition_str, transition_map, issue_key)
    raise ValueError(error_msg)

def format_transition_error(
    invalid_transition: str,
    available_transitions: Dict[str, str],
    issue_key: str
) -> str:
    """
    Format a helpful error message for unresolved transitions.

    Args:
        invalid_transition: Transition that couldn't be resolved
        available_transitions: Map of available transition names to IDs
        issue_key: Issue key

    Returns:
        Formatted error message
    """
    error_msg = f"Transition '{invalid_transition}' not found for issue {issue_key}."

    if available_transitions:
        # Get unique transitions (remove lowercase duplicates for display)
        unique_transitions = {}
        for name, trans_id in available_transitions.items():
            # Only keep the original case version
            if name.lower() != name:  # This is the original case version
                unique_transitions[name] = trans_id

        if unique_transitions:
            error_msg += "\n\nAvailable transitions:"
            for name, trans_id in sorted(unique_transitions.items()):
                error_msg += f"\n  - {name} (ID: {trans_id})"
        else:
            error_msg += "\n\nNo transitions available for this issue."
    else:
        error_msg += f"\n\nCould not fetch transitions for issue {issue_key}."

    error_msg += "\n\nAccepted transition formats:"
    error_msg += '\n  - Transition name: "Closed", "In Progress"'
    error_msg += '\n  - Transition ID: "241", 301'
    error_msg += '\n  - Case-insensitive: "closed", "CLOSED"'

    return error_msg

async def get_transition_details(issue_key: str) -> Dict[str, Any]:
    """
    Get detailed transition information for an issue.

    Args:
        issue_key: Issue key

    Returns:
        Dictionary with transition details including names, IDs, and target statuses
    """
    try:
        response = await make_request("GET", f"issue/{issue_key}/transitions")
        transitions = response.get("transitions", [])

        # Format transitions with additional details
        formatted_transitions = []
        for transition in transitions:
            formatted_transitions.append({
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

        return {
            "issue_key": issue_key,
            "transitions": formatted_transitions,
            "transition_count": len(formatted_transitions)
        }

    except Exception as e:
        logger.error(f"Failed to get transition details for {issue_key}: {e}")
        return {
            "issue_key": issue_key,
            "transitions": [],
            "transition_count": 0,
            "error": str(e)
        }

def clear_transition_cache(issue_key: Optional[str] = None):
    """
    Clear transition cache for a specific issue or all issues.

    Args:
        issue_key: Issue key to clear, or None to clear all
    """
    global _transition_cache
    if issue_key:
        _transition_cache.pop(issue_key, None)
        logger.debug(f"Cleared transition cache for issue {issue_key}")
    else:
        _transition_cache.clear()
        logger.debug("Cleared all transition cache")