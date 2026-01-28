# Game Data Schemas

This directory contains JSON data files for the Sango Text Sim game, following a data-driven architecture for easy extensibility.

## Directory Structure

```
src/data/
├── maps/           # Map and city data for different scenarios
│   └── china_208.json
├── officers/       # Officer rosters (to be added in p1-11)
└── README.md       # This file
```

## Map Schema (maps/*.json)

Map files define the game world including cities, provinces, and adjacencies.

### Structure

```json
{
  "metadata": {
    "name": "string",           // Display name of the scenario
    "scenario_id": "string",    // Unique identifier
    "year": number,             // Starting year
    "month": number,            // Starting month (1-12)
    "description": "string",    // Scenario description
    "version": "string"         // Schema version
  },
  "provinces": [
    {
      "id": "string",           // Province identifier
      "name": "string",         // Display name
      "region": "string"        // Regional grouping (central/west/south/north/east)
    }
  ],
  "cities": [
    {
      "id": "string",           // City identifier (unique)
      "province": "string",     // Province ID this city belongs to
      "terrain": "string",      // Terrain type: plains, mountain, coastal, forest, river
      "coordinates": {
        "x": number,            // X position for map rendering (0-10 scale)
        "y": number             // Y position for map rendering (0-10 scale)
      },
      "is_capital": boolean,    // Whether this is a faction capital
      "owner": "string",        // Faction name (Wei/Shu/Wu)
      "resources": {
        "gold": number,         // Gold reserves
        "food": number,         // Food reserves
        "troops": number        // Total troops stationed
      },
      "development": {
        "agriculture": number,  // Agriculture level (0-100)
        "commerce": number,     // Commerce level (0-100)
        "technology": number,   // Technology level (0-100)
        "walls": number         // Wall level (0-100)
      },
      "military": {
        "defense": number,      // Base defense rating (0-100)
        "morale": number        // Troop morale (0-100)
      },
      "adjacency": ["string"]   // Array of adjacent city IDs
    }
  ]
}
```

### Terrain Types

- **plains**: Normal terrain, balanced for all unit types
- **mountain**: High defense bonus, cavalry penalty
- **coastal**: Access to naval units and trade routes
- **forest**: Ambush bonus, fire attack bonus
- **river**: Crossing penalty for attackers

### Coordinate System

Coordinates use a 0-10 scale for both X and Y axes:
- Allows flexible positioning for map rendering
- Supports ASCII art strategic map display
- Easily scalable from 6 cities to 40+ cities

### Design Principles

1. **Extensibility**: Schema supports 6 cities (current) or 40+ cities (future)
2. **Data-driven**: Game logic loads from JSON, no hardcoded data
3. **Modularity**: Separate concerns (resources, development, military)
4. **Localization**: City IDs used for i18n key lookup
5. **Versioning**: Schema version allows future migrations

## Usage Example

```python
import json
from pathlib import Path

# Load map data
map_path = Path("src/data/maps/china_208.json")
with open(map_path, "r", encoding="utf-8") as f:
    map_data = json.load(f)

# Access cities
for city in map_data["cities"]:
    print(f"{city['id']}: {city['owner']} - {city['terrain']}")
```

## Future Extensions

### Phase 2: Combat Systems (p2-04)
- Terrain effects on combat will be added
- Each terrain type gets detailed combat modifiers

### Phase 5: Full Scale (p5-01)
- `china_208_full.json` with 40+ cities
- All 13 historical provinces
- Complete adjacency network

### Phase 5: Multiple Scenarios (p5-02)
- `china_190.json` - Anti-Dong Zhuo Coalition
- `china_200.json` - Battle of Guandu
- `china_220.json` - Three Kingdoms established

## Schema Validation

Tests verify:
- JSON is valid and loadable
- All required fields present
- Adjacency is bidirectional
- Coordinates are within valid range
- Province references are valid
