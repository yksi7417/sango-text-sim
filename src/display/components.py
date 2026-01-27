"""
Reusable ASCII UI Components

This module provides common UI components for consistent rendering across
the display layer:
- Progress bars with customizable width
- Boxes with titles and content
- Tables with headers and rows
- Separators in various styles
- Faction color codes (ANSI escape sequences)
"""

from typing import List, Optional
from i18n import i18n


# ANSI color codes for faction differentiation
FACTION_COLORS = {
    "Wei": "\033[34m",      # Blue
    "Shu": "\033[32m",      # Green
    "Wu": "\033[31m",       # Red
    "Neutral": "\033[90m",  # Gray
}
COLOR_RESET = "\033[0m"


def render_progress_bar(value: int, max_value: int = 100, width: int = 10) -> str:
    """
    Render a progress bar using block characters.

    Args:
        value: Current value (0-max_value)
        max_value: Maximum value for the bar
        width: Width of the bar in characters

    Returns:
        Progress bar string like "████░░░░░░"

    Examples:
        >>> render_progress_bar(50, 100, 10)
        '█████░░░░░'
        >>> render_progress_bar(100, 100, 10)
        '██████████'
        >>> render_progress_bar(0, 100, 10)
        '░░░░░░░░░░'
    """
    if max_value == 0:
        return "░" * width

    filled = int((value / max_value) * width)
    # Ensure we don't exceed bounds
    filled = max(0, min(filled, width))
    empty = width - filled

    return "█" * filled + "░" * empty


def get_faction_color(faction_name: str) -> str:
    """
    Get the ANSI color code template for a faction.

    Args:
        faction_name: Name of the faction (Wei, Shu, Wu, etc.)

    Returns:
        ANSI color code string with placeholder and reset code

    Examples:
        >>> color = get_faction_color("Wei")
        >>> color.format("Text")  # Returns colored text
    """
    color = FACTION_COLORS.get(faction_name, FACTION_COLORS["Neutral"])
    return color + "{}" + COLOR_RESET


def render_box(content: str, title: str = "", width: int = 60) -> str:
    """
    Render content inside a box with optional title.

    Args:
        content: Multi-line or single-line content to display
        title: Optional title for the box
        width: Width of the box in characters

    Returns:
        Multi-line string with content wrapped in a box

    Examples:
        >>> print(render_box("Hello World", "Greeting", 20))
        ╔══ Greeting ═══════╗
        ║ Hello World       ║
        ╚═══════════════════╝
    """
    lines = []

    # Top border with title
    if title:
        title_part = f"═══ {title} "
        remaining = width - len(title_part) - 2
        top_border = "╔" + title_part + "═" * remaining + "╗"
    else:
        top_border = "╔" + "═" * (width - 2) + "╗"

    lines.append(top_border)

    # Content lines
    content_lines = content.split("\n")
    for line in content_lines:
        # Pad or truncate to fit width
        content_width = width - 4  # Account for "║ " and " ║"
        padded_line = line[:content_width].ljust(content_width)
        lines.append(f"║ {padded_line} ║")

    # Bottom border
    bottom_border = "╚" + "═" * (width - 2) + "╝"
    lines.append(bottom_border)

    return "\n".join(lines)


def render_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Render a table with headers and rows.

    Args:
        headers: List of column headers
        rows: List of row data (each row is a list of cell values)

    Returns:
        Multi-line string with formatted table

    Examples:
        >>> headers = ["Name", "Value"]
        >>> rows = [["Item 1", "100"], ["Item 2", "200"]]
        >>> print(render_table(headers, rows))
        ┌────────┬───────┐
        │ Name   │ Value │
        ├────────┼───────┤
        │ Item 1 │ 100   │
        │ Item 2 │ 200   │
        └────────┴───────┘
    """
    if not headers:
        return ""

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    lines = []

    # Top border
    top_parts = ["┌"] + [("─" * (w + 2)) for w in col_widths]
    lines.append("┬".join(top_parts) + "┐")

    # Headers
    header_cells = [f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))]
    lines.append("│" + "│".join(header_cells) + "│")

    # Header separator
    sep_parts = ["├"] + [("─" * (w + 2)) for w in col_widths]
    lines.append("┼".join(sep_parts) + "┤")

    # Data rows
    for row in rows:
        row_cells = []
        for i in range(len(headers)):
            cell_value = str(row[i]) if i < len(row) else ""
            row_cells.append(f" {cell_value.ljust(col_widths[i])} ")
        lines.append("│" + "│".join(row_cells) + "│")

    # Bottom border
    bottom_parts = ["└"] + [("─" * (w + 2)) for w in col_widths]
    lines.append("┴".join(bottom_parts) + "┘")

    return "\n".join(lines)


def render_separator(width: int, style: str = "single") -> str:
    """
    Render a horizontal separator line.

    Args:
        width: Width of the separator in characters
        style: Style of separator ("single", "double", "heavy", "dotted")

    Returns:
        Separator string

    Examples:
        >>> render_separator(10, "single")
        '──────────'
        >>> render_separator(10, "double")
        '══════════'
    """
    styles = {
        "single": "─",
        "double": "═",
        "heavy": "━",
        "dotted": "·"
    }

    char = styles.get(style, "─")
    return char * width
