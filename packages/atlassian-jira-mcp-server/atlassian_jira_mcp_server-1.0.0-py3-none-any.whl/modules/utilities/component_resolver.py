"""
Component Resolution Utility for Jira MCP Server
Handles flexible component input formats and auto-resolution
"""

from typing import Optional, List, Dict, Any, Union
from utils.api_client import make_request
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)

# Cache for component mappings to avoid repeated API calls
_component_cache = {}

async def get_project_components_map(project_key: str) -> Dict[str, str]:
    """
    Get component name to ID mapping for a project.

    Args:
        project_key: Project key

    Returns:
        Dictionary mapping component names to IDs
    """
    # Check cache first
    if project_key in _component_cache:
        return _component_cache[project_key]

    try:
        # Fetch project components
        components = await make_request("GET", f"project/{project_key}/components")

        # Create name -> id mapping
        component_map = {}
        for comp in components:
            if 'name' in comp and 'id' in comp:
                component_map[comp['name']] = comp['id']

        # Cache the mapping
        _component_cache[project_key] = component_map
        logger.debug(f"Cached {len(component_map)} components for project {project_key}")

        return component_map
    except Exception as e:
        logger.error(f"Failed to fetch components for project {project_key}: {e}")
        return {}

async def resolve_components(
    components: Optional[List[Union[str, Dict[str, Any]]]],
    project_key: str
) -> Optional[List[Dict[str, str]]]:
    """
    Resolve components from various input formats to Jira API format.

    Accepts:
    - String array: ["fe-main", "ui-kit"]
    - Object array: [{"id": "10398"}, {"name": "component"}]
    - Mixed formats: ["fe-main", {"id": "10365"}]

    Args:
        components: Component input in various formats
        project_key: Project key for component lookup

    Returns:
        List of component objects in Jira API format [{"id": "..."}]

    Raises:
        ValueError: If components cannot be resolved
    """
    if not components:
        return None

    # Get component name -> ID mapping
    component_map = await get_project_components_map(project_key)

    resolved = []
    unresolved = []

    for comp in components:
        if isinstance(comp, str):
            # String input - try to resolve name to ID
            if comp in component_map:
                resolved.append({"id": component_map[comp]})
                logger.debug(f"Resolved component '{comp}' to ID {component_map[comp]}")
            else:
                # String doesn't match any known component name
                # Could be an ID, but we should validate it exists
                # For now, mark as unresolved to trigger better error message
                unresolved.append(comp)
        elif isinstance(comp, dict):
            if 'id' in comp:
                # Already in correct format
                resolved.append({"id": comp['id']})
                logger.debug(f"Using component ID {comp['id']}")
            elif 'name' in comp:
                # Has name, needs ID resolution
                name = comp['name']
                if name in component_map:
                    resolved.append({"id": component_map[name]})
                    logger.debug(f"Resolved component name '{name}' to ID {component_map[name]}")
                else:
                    unresolved.append(name)
            else:
                logger.warning(f"Invalid component object format: {comp}")
                unresolved.append(str(comp))
        else:
            logger.warning(f"Invalid component type: {type(comp).__name__}")
            unresolved.append(str(comp))

    # If we have unresolved components, create a helpful error
    if unresolved:
        error_msg = format_component_error(unresolved, component_map, project_key)
        raise ValueError(error_msg)

    return resolved if resolved else None

def format_component_error(
    unresolved_components: List[str],
    available_components: Dict[str, str],
    project_key: str
) -> str:
    """
    Format a helpful error message for unresolved components.

    Args:
        unresolved_components: List of components that couldn't be resolved
        available_components: Map of available component names to IDs
        project_key: Project key

    Returns:
        Formatted error message
    """
    if len(unresolved_components) == 1:
        error_msg = f"Component '{unresolved_components[0]}' not found in project {project_key}."
    else:
        components_str = "', '".join(unresolved_components)
        error_msg = f"Components '{components_str}' not found in project {project_key}."

    if available_components:
        error_msg += "\n\nAvailable components:"
        for name, comp_id in sorted(available_components.items()):
            error_msg += f"\n  - {name} (ID: {comp_id})"
    else:
        error_msg += f"\n\nNo components found in project {project_key}."

    error_msg += "\n\nAccepted component formats:"
    error_msg += '\n  - String array: ["fe-main", "ui-kit"]'
    error_msg += '\n  - Object array: [{"id": "10398"}]'
    error_msg += '\n  - Mixed: ["fe-main", {"id": "10365"}]'

    return error_msg

def clear_component_cache(project_key: Optional[str] = None):
    """
    Clear component cache for a specific project or all projects.

    Args:
        project_key: Project key to clear, or None to clear all
    """
    global _component_cache
    if project_key:
        _component_cache.pop(project_key, None)
        logger.debug(f"Cleared component cache for project {project_key}")
    else:
        _component_cache.clear()
        logger.debug("Cleared all component cache")