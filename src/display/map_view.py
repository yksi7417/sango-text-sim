#
# Fixed-template map rendering for perfect alignment (demo.jsx style)
def render_strategic_map(game_state: GameState) -> str:
    """
    Render the strategic map using a fixed ASCII art template for perfect alignment.
    City names and symbols are inserted at fixed positions, matching the demo.jsx layout.
    """
    # Color helpers
    def color(faction, text):
        return get_faction_color(faction).format(text)

    # Map city/faction to display info
    city_display = {
        "luoyang":  color("Wei", "洛陽"),
        "hanzhong": color("Shu", "漢中"),
        "chengdu":  color("Shu", "成都"),
        "jianye":   color("Wu", "建業"),
        "xiangyang": color("Wei", "襄陽"),
    }

    # Template (matches demo.jsx)
    template = (
        "                              ╔═══════╗\n"
        "                              ║ 幽 州 ║ \n"
        "                              ╚═══╦═══╝\n"
        "                                  ║\n"
        "           ╔═══════╗          ╔═══╩═══╗          ╔═══════╗\n"
        "           ║ 并 州 ║──────────║ {luoyang} ║──────────║ 青 州 ║\n"
        "           ╚═══╦═══╝          ╚═══╦═══╝          ╚═══════╝\n"
        "               ║                  ║\n"
        "           ╔═══╩═══╗          ╔═══╩═══╗          ╔═══════╗\n"
        "           ║ {hanzhong} ║──────────║ {xiangyang} ║──────────║ {jianye} ║\n"
        "           ╚═══╦═══╝          ╚═══════╝          ╚═══════╝\n"
        "               ║                  \n"
        "           ╔═══╩═══╗          ╔═══════╗          ╔═══════╗\n"
        "           ║ {chengdu} ║──────────║ 荊 南 ║──────────║ 交 州 ║\n"
        "           ╚═══════╝          ╚═══════╝          ╚═══════╝\n"
    )

    # Fill in city names (fallback to plain if not present)
    map_str = template.format(
        luoyang=city_display.get("luoyang", "洛陽"),
        hanzhong=city_display.get("hanzhong", "漢中"),
        chengdu=city_display.get("chengdu", "成都"),
        jianye=city_display.get("jianye", "建業"),
        xiangyang=city_display.get("xiangyang", "襄陽"),
    )

    # Header and legend (reuse existing)
    header = i18n.t("map.title", default="=== Strategic Map ===")
    legend = create_legend(game_state)

    return f"\n{header}\n\n{map_str}\n{legend}\n"
"""
ASCII Map Renderer for Strategic View

This module renders the game's strategic map using ASCII/Unicode characters.
Features:
- Coordinate-based city placement from JSON data
- Faction color codes (ANSI escape sequences)
- Capital city markers (★)
- Connection lines between adjacent cities
- Scalable for different map sizes (6-40+ cities)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..models import GameState, City, Faction
from i18n import i18n
from .components import FACTION_COLORS, get_faction_color as get_faction_color_template

COLOR_RESET = "\033[0m"

# Terrain symbols
TERRAIN_SYMBOLS = {
    "plains": "○",
    "mountain": "▲",
    "coastal": "◊",
    "forest": "♣",
}


def get_faction_color(faction_name: str) -> str:
    """
    Get the ANSI color code for a faction.

    Args:
        faction_name: Name of the faction (Wei, Shu, Wu, etc.)

    Returns:
        ANSI color code string with reset code appended
    """
    # Use the centralized function from components
    return get_faction_color_template(faction_name)


def load_map_data(scenario: str = "china_208") -> Optional[Dict]:
    """
    Load map data from JSON file.

    Args:
        scenario: Scenario name (e.g., "china_208")

    Returns:
        Map data dictionary or None if file not found
    """
    data_dir = Path(__file__).parent.parent / "data" / "maps"
    map_file = data_dir / f"{scenario}.json"

    if map_file.exists():
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def render_strategic_map_old_broken(game_state: GameState) -> str:
    """
    Render the strategic map showing all cities, connections, and territories.

    The map uses coordinate-based positioning from JSON data:
    - Cities are placed at their (x, y) coordinates
    - Capital cities are marked with ★
    - Faction colors differentiate territories
    - Lines show connections between adjacent cities

    Args:
        game_state: Current game state with cities, factions, and adjacency map

    Returns:
        Multi-line ASCII string representing the strategic map
    """
    if not game_state.cities:
        return i18n.t("map.empty", default="No cities on map.")

    # Load map data to get coordinates
    map_data = load_map_data("china_208")

    # Create coordinate lookup
    city_coords: Dict[str, Tuple[int, int]] = {}
    city_terrain: Dict[str, str] = {}
    city_is_capital: Dict[str, bool] = {}

    if map_data and "cities" in map_data:
        for city_data in map_data["cities"]:
            city_id = city_data["id"]
            city_coords[city_id] = (city_data["coordinates"]["x"], city_data["coordinates"]["y"])
            city_terrain[city_id] = city_data.get("terrain", "plains")
            city_is_capital[city_id] = city_data.get("is_capital", False)

    # Handle cities not in JSON data (test cities, etc.) with fallback layout
    cities_list = list(game_state.cities.keys())
    for i, city_name in enumerate(cities_list):
        if city_name not in city_coords:
            x = (i % 4) * 3 + 1
            y = (i // 4) * 2 + 1
            city_coords[city_name] = (x, y)
            city_terrain[city_name] = "plains"
            city_is_capital[city_name] = False

    # Determine map bounds
    if city_coords:
        max_x = max(coord[0] for coord in city_coords.values()) + 2
        max_y = max(coord[1] for coord in city_coords.values()) + 2
    else:
        max_x, max_y = 10, 8

    # Create empty grid
    grid = [[" " for _ in range(max_x * 3)] for _ in range(max_y * 2)]

    # Draw connections first (so they appear under cities)
    for city_name, adjacent_list in game_state.adj.items():
        if city_name not in city_coords:
            continue
        x1, y1 = city_coords[city_name]

        for adj_city in adjacent_list:
            if adj_city not in city_coords:
                continue
            x2, y2 = city_coords[adj_city]

            # Draw simple line between cities
            # Only draw if this city is "before" the adjacent one (to avoid duplicates)
            if city_name < adj_city:
                draw_connection(grid, x1, y1, x2, y2)

    # Draw cities
    for city_name, city in game_state.cities.items():
        if city_name not in city_coords:
            continue

        x, y = city_coords[city_name]
        owner = city.owner
        terrain = city_terrain.get(city_name, "plains")
        is_capital = city_is_capital.get(city_name, False)

        # Get faction color
        color_template = get_faction_color(owner)

        # Determine symbol
        terrain_symbol = TERRAIN_SYMBOLS.get(terrain, "○")
        if is_capital:
            symbol = "★"
        else:
            symbol = terrain_symbol

        # Place colored symbol on grid
        grid_y = y * 2
        grid_x = x * 3

        if 0 <= grid_y < len(grid) and 0 <= grid_x < len(grid[0]):
            colored_symbol = color_template.format(symbol)
            grid[grid_y][grid_x] = colored_symbol

            # Place city name below symbol (abbreviated if needed)
            name_y = grid_y + 1
            abbrev = city_name[:4] if len(city_name) > 4 else city_name
            colored_name = color_template.format(abbrev)

            # Center the name under the symbol
            start_x = grid_x - len(abbrev) // 2
            for i, char in enumerate(abbrev):
                char_x = start_x + i
                if 0 <= name_y < len(grid) and 0 <= char_x < len(grid[0]):
                    grid[name_y][char_x] = color_template.format(char)

    # Convert grid to string
    lines = []
    for row in grid:
        line = "".join(row)
        lines.append(line.rstrip())

    # Add header
    header = i18n.t("map.title", default="=== Strategic Map ===")
    legend = create_legend(game_state)

    result = f"\n{header}\n\n"
    result += "\n".join(lines)
    result += f"\n\n{legend}\n"

    return result


def draw_connection(grid: List[List[str]], x1: int, y1: int, x2: int, y2: int):
    """
    Draw a simple line connection between two points on the grid.

    Args:
        grid: 2D grid of characters
        x1, y1: Start coordinate
        x2, y2: End coordinate
    """
    # Convert to grid coordinates
    grid_x1, grid_y1 = x1 * 3, y1 * 2
    grid_x2, grid_y2 = x2 * 3, y2 * 2

    # Draw simple line (can be enhanced with better pathfinding later)
    dx = 1 if grid_x2 > grid_x1 else -1 if grid_x2 < grid_x1 else 0
    dy = 1 if grid_y2 > grid_y1 else -1 if grid_y2 < grid_y1 else 0

    x, y = grid_x1 + dx, grid_y1 + dy

    while x != grid_x2 or y != grid_y2:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            if grid[y][x] == " ":
                if dx != 0 and dy == 0:
                    grid[y][x] = "─"
                elif dx == 0 and dy != 0:
                    grid[y][x] = "│"
                else:
                    grid[y][x] = "·"

        if x != grid_x2:
            x += dx
        if y != grid_y2:
            y += dy


def create_legend(game_state: GameState) -> str:
    """
    Create a legend explaining map symbols and showing faction stats.

    Args:
        game_state: Current game state

    Returns:
        Formatted legend string
    """
    legend_parts = []

    # Symbol legend
    legend_parts.append(i18n.t("map.legend.symbols", default="Symbols:"))
    legend_parts.append(f"  ★ = {i18n.t('map.legend.capital', default='Capital')}")
    legend_parts.append(f"  ○ = {i18n.t('map.legend.plains', default='Plains')}")
    legend_parts.append(f"  ▲ = {i18n.t('map.legend.mountain', default='Mountain')}")
    legend_parts.append(f"  ◊ = {i18n.t('map.legend.coastal', default='Coastal')}")
    legend_parts.append("")

    # Faction summary
    legend_parts.append(i18n.t("map.legend.factions", default="Factions:"))

    for faction_name, faction in sorted(game_state.factions.items()):
        city_count = len(faction.cities)
        color_template = get_faction_color(faction_name)
        colored_name = color_template.format(faction_name)

        cities_text = i18n.t("map.legend.cities", count=city_count, default=f"{city_count} cities")
        legend_parts.append(f"  {colored_name}: {cities_text}")

    return "\n".join(legend_parts)
