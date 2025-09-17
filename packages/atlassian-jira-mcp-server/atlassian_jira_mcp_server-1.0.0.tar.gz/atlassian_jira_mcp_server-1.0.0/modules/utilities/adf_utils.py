"""
ADF (Atlassian Document Format) utilities for Jira MCP Server
Provides helpers for creating and formatting rich content in Jira
"""

from typing import List, Dict, Any, Optional, Union
from adf_lib import ADF, Text, Table, Link
from adf_lib.constants.enums import HeadingLevel, TableLayout
import re
import json


def text_to_adf(text: str) -> Dict[str, Any]:
    """
    Convert plain text to ADF format

    Args:
        text: Plain text string

    Returns:
        ADF document as dict
    """
    doc = ADF()

    # Split by double newlines for paragraphs
    paragraphs = text.split('\n\n')

    for para_text in paragraphs:
        if para_text.strip():
            doc.add(Text(para_text.strip()).paragraph())

    return doc.to_dict()


def markdown_to_adf(markdown: str) -> Dict[str, Any]:
    """
    Convert basic markdown to ADF format

    Supports:
    - Headers (# ## ###)
    - Bold (**text**)
    - Italic (*text*)
    - Code (`code`)
    - Bullet lists (- item)
    - Numbered lists (1. item)
    - Code blocks (```language)
    - Links ([text](url))

    Args:
        markdown: Markdown formatted text

    Returns:
        ADF document as dict
    """
    doc = ADF()
    lines = markdown.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            if text and 1 <= level <= 6:
                heading_level = getattr(HeadingLevel, f'H{level}')
                doc.add(Text(text).heading(heading_level))
                i += 1
                continue

        # Code blocks
        if line.startswith('```'):
            language = line[3:].strip() or 'text'
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                # Use preformatted text for code blocks
                code_text = '\n'.join(code_lines)
                doc.add(Text(code_text, "code").paragraph())
            i += 1
            continue

        # Bullet lists
        if line.startswith('- ') or line.startswith('* '):
            # Collect all bullet items
            bullet_items = []
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                item_text = lines[i][2:].strip()
                bullet_items.append(item_text)
                i += 1

            # Add as a single paragraph with bullet points
            # ADF doesn't have native bullet lists in the same way, so we simulate
            for item in bullet_items:
                doc.add(Text(f"• {item}").paragraph())
            continue

        # Numbered lists
        if re.match(r'^\d+\.\s', line):
            # Collect all numbered items
            numbered_items = []
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
                item_text = re.sub(r'^\d+\.\s', '', lines[i]).strip()
                numbered_items.append(item_text)
                i += 1

            # Add as numbered items
            for idx, item in enumerate(numbered_items, 1):
                doc.add(Text(f"{idx}. {item}").paragraph())
            continue

        # Regular paragraph with inline formatting
        if line.strip():
            # Process inline markdown
            formatted_text = process_inline_markdown(line)
            doc.add(formatted_text)

        i += 1

    return doc.to_dict()


def process_inline_markdown(text: str):
    """
    Process inline markdown formatting (bold, italic, code, links)

    Args:
        text: Text with inline markdown

    Returns:
        Formatted Text object
    """
    # For simplicity, we'll handle basic formatting
    # Bold: **text** -> strong
    # Italic: *text* -> em
    # Code: `text` -> code

    marks = []

    # Check for bold
    if '**' in text:
        text = text.replace('**', '')
        marks.append("strong")

    # Check for italic (but not if it's part of bold)
    if '*' in text and '**' not in text:
        text = text.replace('*', '')
        marks.append("em")

    # Check for code
    if '`' in text:
        text = text.replace('`', '')
        marks.append("code")

    # Create text with marks
    if marks:
        return Text(text, *marks).paragraph()
    else:
        return Text(text).paragraph()


def create_issue_description(
    overview: str,
    acceptance_criteria: Optional[List[str]] = None,
    technical_details: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a well-formatted issue description with sections

    Args:
        overview: Main description text
        acceptance_criteria: List of acceptance criteria
        technical_details: Optional technical details section
        notes: Optional notes section

    Returns:
        ADF formatted description
    """
    doc = ADF()

    # Overview
    if overview:
        doc.add(Text(overview).paragraph())

    # Acceptance Criteria
    if acceptance_criteria:
        doc.add(Text("Acceptance Criteria").heading(HeadingLevel.H3))
        for criterion in acceptance_criteria:
            doc.add(Text(f"• {criterion}").paragraph())

    # Technical Details
    if technical_details:
        doc.add(Text("Technical Details").heading(HeadingLevel.H3))
        doc.add(Text(technical_details).paragraph())

    # Notes
    if notes:
        doc.add(Text("Notes").heading(HeadingLevel.H3))
        doc.add(Text(notes).paragraph())

    return doc.to_dict()


def create_comment(
    text: str,
    mentions: Optional[List[str]] = None,
    code_snippet: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a formatted comment with optional mentions and code

    Args:
        text: Comment text
        mentions: List of user account IDs to mention
        code_snippet: Dict with 'code' and optional 'language' keys

    Returns:
        ADF formatted comment
    """
    doc = ADF()

    # Add mentions at the beginning if provided
    if mentions:
        mention_text = " ".join([f"@{account_id}" for account_id in mentions])
        doc.add(Text(mention_text + " ").paragraph())

    # Main comment text
    doc.add(Text(text).paragraph())

    # Add code snippet if provided
    if code_snippet:
        code = code_snippet.get('code', '')
        if code:
            doc.add(Text(code, "code").paragraph())

    return doc.to_dict()


def create_table(headers: List[str], rows: List[List[str]], width: int = 100) -> Dict[str, Any]:
    """
    Create an ADF table

    Args:
        headers: List of header texts
        rows: List of row data (each row is a list of cell texts)
        width: Table width percentage (default 100)

    Returns:
        ADF table as dict
    """
    table = Table(
        width=width,
        is_number_column_enabled=False,
        layout=TableLayout.DEFAULT
    )

    # Add header row
    header_cells = []
    for header in headers:
        header_cells.append(table.header([Text(header, "strong").paragraph()]))
    table.add_row(header_cells)

    # Add data rows
    for row_data in rows:
        row_cells = []
        for cell_text in row_data:
            row_cells.append(table.cell([Text(cell_text).paragraph()]))
        table.add_row(row_cells)

    # Create a document with the table
    doc = ADF()
    # Tables need to be added as their dict representation
    return table.to_dict()


def create_link(text: str, url: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a paragraph with a link

    Args:
        text: Link text
        url: Link URL
        title: Optional link title

    Returns:
        ADF paragraph with link
    """
    doc = ADF()
    link = Link(href=url, title=title or text)
    doc.add(Text(text, link.to_mark()).paragraph())
    return doc.to_dict()


def is_adf_format(content: Any) -> bool:
    """
    Check if content is already in ADF format

    Args:
        content: Content to check

    Returns:
        True if content appears to be ADF formatted
    """
    if not isinstance(content, dict):
        return False

    # Check for ADF structure markers
    return (
        content.get('type') == 'doc' and
        'version' in content and
        'content' in content
    )


def convert_to_adf(content: Union[str, Dict]) -> Dict[str, Any]:
    """
    Smart conversion to ADF format

    Args:
        content: String (plain/markdown) or dict (potentially ADF)

    Returns:
        ADF formatted content
    """
    # Already ADF
    if is_adf_format(content):
        return content

    # Convert string
    if isinstance(content, str):
        # Try to detect markdown
        if any(marker in content for marker in ['#', '**', '```', '[', '- ', '1. ']):
            return markdown_to_adf(content)
        else:
            return text_to_adf(content)

    # Unknown format, convert to string and process
    return text_to_adf(str(content))


def adf_to_markdown(adf_content: Dict[str, Any]) -> str:
    """
    Convert ADF content to readable markdown format

    Args:
        adf_content: ADF document dict

    Returns:
        Markdown formatted string
    """
    if not isinstance(adf_content, dict):
        return str(adf_content)

    # Handle different content types
    content_type = adf_content.get('type', '')

    if content_type == 'doc':
        # Process document content
        markdown_parts = []
        for node in adf_content.get('content', []):
            markdown_parts.append(adf_to_markdown(node))
        return '\n'.join(markdown_parts)

    elif content_type == 'paragraph':
        # Process paragraph content
        text_parts = []
        for node in adf_content.get('content', []):
            text_parts.append(adf_to_markdown(node))
        return ''.join(text_parts) + '\n'

    elif content_type == 'text':
        # Process text with marks
        text = adf_content.get('text', '')
        marks = adf_content.get('marks', [])

        for mark in marks:
            mark_type = mark.get('type', '')
            if mark_type == 'strong':
                text = f"**{text}**"
            elif mark_type == 'em':
                text = f"*{text}*"
            elif mark_type == 'code':
                text = f"`{text}`"
            elif mark_type == 'link':
                href = mark.get('attrs', {}).get('href', '')
                text = f"[{text}]({href})"

        return text

    elif content_type == 'heading':
        # Process headings
        level = adf_content.get('attrs', {}).get('level', 1)
        text_parts = []
        for node in adf_content.get('content', []):
            text_parts.append(adf_to_markdown(node))
        heading_text = ''.join(text_parts)
        return f"{'#' * level} {heading_text}\n"

    elif content_type == 'bulletList':
        # Process bullet lists
        items = []
        for node in adf_content.get('content', []):
            items.append(adf_to_markdown(node))
        return '\n'.join(items)

    elif content_type == 'listItem':
        # Process list items
        text_parts = []
        for node in adf_content.get('content', []):
            text_parts.append(adf_to_markdown(node))
        return f"- {''.join(text_parts)}"

    elif content_type == 'orderedList':
        # Process numbered lists
        items = []
        for idx, node in enumerate(adf_content.get('content', []), 1):
            item_text = adf_to_markdown(node)
            # Replace list item marker with number
            if item_text.startswith('- '):
                item_text = f"{idx}. {item_text[2:]}"
            items.append(item_text)
        return '\n'.join(items)

    elif content_type == 'codeBlock':
        # Process code blocks
        language = adf_content.get('attrs', {}).get('language', '')
        text_parts = []
        for node in adf_content.get('content', []):
            text_parts.append(adf_to_markdown(node))
        code_text = ''.join(text_parts)
        return f"```{language}\n{code_text}\n```\n"

    elif content_type == 'table':
        # Process tables (simplified)
        return "[Table]\n"

    elif content_type == 'blockquote':
        # Process blockquotes
        text_parts = []
        for node in adf_content.get('content', []):
            text_parts.append(adf_to_markdown(node))
        quote_text = ''.join(text_parts)
        return '> ' + quote_text.replace('\n', '\n> ') + '\n'

    else:
        # Unknown type, try to process content if exists
        if 'content' in adf_content:
            parts = []
            for node in adf_content['content']:
                parts.append(adf_to_markdown(node))
            return ''.join(parts)
        elif 'text' in adf_content:
            return adf_content['text']
        else:
            return ''


def format_issue_for_llm(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format issue response optimized for LLM consumption
    Returns both simple text content and structured data

    Args:
        issue: Raw issue data from Jira API

    Returns:
        Dict with 'content' (simple text) and 'data' (structured key info)
    """
    fields = issue.get('fields', {})

    # Build simple text content
    lines = []
    lines.append(f"{issue.get('key')}: {fields.get('summary', '')}")
    lines.append(f"Status: {fields.get('status', {}).get('name', 'Unknown')}")
    lines.append(f"Type: {fields.get('issuetype', {}).get('name', 'Unknown')}")
    lines.append(f"Priority: {fields.get('priority', {}).get('name', 'None')}")

    assignee = fields.get('assignee')
    lines.append(f"Assignee: {assignee.get('displayName') if assignee else 'Unassigned'}")

    # Description (simplified)
    description = fields.get('description')
    if description:
        if isinstance(description, dict) and description.get('type') == 'doc':
            desc_text = adf_to_markdown(description).strip()
            if desc_text:
                lines.append(f"\nDescription:\n{desc_text[:500]}{'...' if len(desc_text) > 500 else ''}")
        elif description:
            lines.append(f"\nDescription:\n{str(description)[:500]}{'...' if len(str(description)) > 500 else ''}")

    # Transitions (if present)
    if 'transitions' in issue and issue['transitions']:
        trans_names = [t.get('name') for t in issue['transitions']]
        lines.append(f"\nAvailable transitions: {', '.join(trans_names)}")

    # Build structured data (minimal)
    data = {
        'key': issue.get('key'),
        'id': issue.get('id'),
        'summary': fields.get('summary'),
        'status': fields.get('status', {}).get('name'),
        'type': fields.get('issuetype', {}).get('name'),
        'priority': fields.get('priority', {}).get('name'),
        'assignee': assignee.get('displayName') if assignee else None,
        'assignee_id': assignee.get('accountId') if assignee else None,
        'created': fields.get('created'),
        'updated': fields.get('updated'),
        'labels': fields.get('labels', []),
        'project': fields.get('project', {}).get('key'),
        'url': issue.get('self')
    }

    # Add transitions if present
    if 'transitions' in issue:
        data['transitions'] = [{
            'id': t.get('id'),
            'name': t.get('name'),
            'to': t.get('to', {}).get('name')
        } for t in issue['transitions']]

    return {
        'content': '\n'.join(lines),
        'data': data
    }