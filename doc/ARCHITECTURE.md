# Sango Text Sim Architecture

This document provides a detailed overview of the game's modular architecture, design decisions, and module responsibilities.

## Design Philosophy

The refactoring transformed a 704-line monolithic `game.py` into a modular, maintainable codebase following these principles:

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Pure Functions**: Most logic uses pure functions for testability
3. **Immutable Data**: Dataclasses provide structure without behavior
4. **No Circular Dependencies**: Clear dependency hierarchy
5. **Test-Driven**: 99% code coverage with 153 comprehensive tests
6. **Type Safety**: Python 3.8+ type hints throughout

## Module Hierarchy

```
┌─────────────┐
│   game.py   │  ← UI Layer (adventurelib commands)
└──────┬──────┘
       │ uses
       ↓
┌──────────────────────────────────────────┐
│         Module Layer                     │
│  ┌────────┬─────────┬────────┬────────┐ │
│  │ engine │ world   │ persist│ utils  │ │
│  └────┬───┴────┬────┴────┬───┴───┬────┘ │
│       │        │         │       │      │
│       └────────┴─────────┴───────┘      │
│                   ↓                      │
│         ┌──────────────────┐            │
│         │ models, constants│            │
│         └──────────────────┘            │
└──────────────────────────────────────────┘
```

Dependencies flow downward:
- `game.py` → all modules
- `engine.py`, `world.py`, `persistence.py`, `utils.py` → `models.py`, `constants.py`
- `models.py` ← no dependencies (leaf node)
- `constants.py` ← no dependencies (leaf node)

## Module Documentation

### models.py (51 statements, 100% coverage)

**Purpose**: Define core data structures using Python dataclasses.

**Contents**:
- `Officer`: Character with stats (leadership, intelligence, politics, charisma), loyalty, energy, traits, assignments
- `City`: Settlement with resources (gold, food, troops), development levels (agri, commerce, tech, walls), defense, morale
- `Faction`: Political entity with diplomatic relations, controlled cities, and officers
- `GameState`: Global game container with all factions, cities, officers, adjacency map, time, messages

**Design Decisions**:
- Uses `@dataclass` for automatic `__init__`, `__repr__`, `__eq__`
- Fields use type hints and defaults
- `field(default_factory=dict)` for mutable defaults
- `GameState.log()` method for message tracking
- No business logic - pure data containers

**Example**:
```python
officer = Officer(
    name="關羽",
    faction="Shu",
    leadership=95,
    intelligence=75,
    politics=65,
    charisma=90,
    traits=["Brave"],
    city="Chengdu"
)
```

### constants.py (64 statements, 100% coverage)

**Purpose**: Centralized game configuration and balance parameters.

**Contents**:
- `FACTION_NAMES`: Wei (曹操), Shu (劉備), Wu (孫權)
- `TASK_TYPES`: farm, trade, research, train, fortify, recruit
- `TASK_ALIASES`: Bilingual task name mapping
- `TRAIT_BONUSES`: Task-specific trait multipliers
- Economic constants: `BASE_INCOME`, `UPKEEP_RATE`, `TAX_BONUS`, `HARVEST_BONUS`
- Combat constants: `BASE_ATTACK_MULT`, `BASE_DEFEND_MULT`, `TECH_EFFECT`
- AI constants: `AI_REST_THRESHOLD`, `DEFECTION_CHANCE`

**Design Decisions**:
- All caps for constants (PEP 8)
- Grouped by category
- Easy to tune game balance without code changes
- Bilingual support baked into aliases

**Example**:
```python
from src.constants import TRAIT_BONUSES, TASK_ALIASES

# Get bonus for Brave officer on farm task
bonus = TRAIT_BONUSES.get("Brave", {}).get("farm", 1.0)

# Resolve task name from Chinese input
task = TASK_ALIASES.get("農業")  # Returns "farm"
```

### utils.py (65 statements, 100% coverage)

**Purpose**: Helper functions for calculations, formatting, and validation.

**Key Functions**:

**Math/Validation**:
- `clamp(value, min_val, max_val)`: Constrain value to range
- `valid_city(gs, name)`: Check if city exists
- `ensure_player_city(gs, name)`: Validate player ownership
- `is_adjacent(gs, city1, city2)`: Check adjacency

**Officer Queries**:
- `officer_by_name(gs, name)`: Find officer by name
- `officers_in_city(gs, city_name, faction)`: Get officers at location

**Trait System**:
- `trait_mult(officer, task)`: Calculate trait bonus multiplier

**Task Resolution**:
- `task_key(word)`: Resolve bilingual task names

**Formatting**:
- `format_faction_overview(gs, faction_name)`: Multi-line faction status
- `format_city_status(gs, city_name)`: City details with officers
- `validate_march(gs, src, dest, size)`: Pre-validate march command

**Design Decisions**:
- Pure functions (no side effects)
- Type hints on all functions
- Comprehensive docstrings
- Bilingual support in task resolution
- Defensive programming (validate inputs)

**Example**:
```python
from src import utils

# Validate march before executing
error = utils.validate_march(gs, "Chengdu", "Hanzhong", 1000)
if error:
    print(error)
else:
    # Proceed with march
    pass

# Calculate effective bonus
officer = gs.officers["關羽"]
multiplier = utils.trait_mult(officer, "farm")  # 1.1 if Benevolent
```

### engine.py (208 statements, 97% coverage)

**Purpose**: Core game mechanics and turn processing.

**Key Functions**:

**Combat**:
- `tech_attack_bonus(gs, faction)`: Calculate technology bonus
- `battle(gs, attacker, defender, atk_size)`: Resolve combat (returns success, casualties)
- `transfer_city(gs, new_owner, city)`: Change city ownership

**Economy**:
- `assignment_effect(gs, officer, city)`: Apply officer task effects
- `process_assignments(gs)`: Process all pending assignments
- `monthly_economy(gs)`: Income, upkeep, seasonal events

**AI**:
- `ai_turn(gs, faction)`: AI decision-making (assign tasks, launch attacks)
- `try_defections(gs)`: Check for low-loyalty defections

**Turn Management**:
- `end_turn(gs)`: Advance time, process events, recover energy
- `check_victory(gs)`: Detect win/lose conditions

**Design Decisions**:
- Stateful functions (modify GameState in-place)
- Complex battle formula considering stats, morale, tech, traits
- AI uses randomness for variety (weighted by stats)
- Seasonal events (January tax, July harvest)
- Energy recovery for idle officers
- Defection risk for low loyalty (<35)

**Example**:
```python
from src import engine

# Execute battle
attacker = gs.cities["Chengdu"]
defender = gs.cities["Hanzhong"]
success, casualties = engine.battle(gs, attacker, defender, 2000)

if success:
    engine.transfer_city(gs, attacker.owner, defender)
    print(f"Victory! Lost {casualties} troops")
else:
    print(f"Defeat! Lost {casualties} troops")

# Process turn
engine.end_turn(gs)
if engine.check_victory(gs):
    print("Game Over!")
```

### world.py (40 statements, 100% coverage)

**Purpose**: World generation and initialization data.

**Constants**:
- `CITY_DATA`: 6 cities (Xuchang, Luoyang, Chengdu, Hanzhong, Jianye, Wuchang) with starting resources
- `OFFICER_DATA`: 7 legendary officers (劉備, 關羽, 張飛, 曹操, 張遼, 孫權, 周瑜) with historical stats
- `ADJACENCY_MAP`: City connections defining valid march targets

**Key Functions**:
- `add_officer(gs, officer)`: Register officer in game state
- `init_world(gs, player_choice, seed)`: Initialize complete game world

**Design Decisions**:
- Reproducible randomization via seed parameter
- Historical accuracy in officer stats (關羽 has high leadership)
- Balanced starting positions (each faction gets 2 cities)
- Symmetric adjacency (if A→B then B→A)
- Player chooses faction (Wei/Shu/Wu) or defaults to Shu

**Data Validation Tests**:
- All cities have positive resources
- All officers have stats in 40-100 range
- Adjacency is symmetric and connected
- No self-loops in adjacency

**Example**:
```python
from src import world
from src.models import GameState

gs = GameState()
world.init_world(gs, player_choice="Shu", seed=42)

# Now gs has:
# - 6 cities with resources
# - 3 factions (Wei, Shu, Wu)
# - 7 officers assigned to factions
# - Adjacency map
# - Player controlling Shu
```

### persistence.py (39 statements, 100% coverage)

**Purpose**: Save and load game state to JSON files.

**Key Functions**:
- `save_game(gs, filepath)`: Serialize GameState to JSON (returns bool)
- `load_game(gs, filepath)`: Deserialize JSON to GameState (returns error string or None)
- `get_default_save_path()`: Returns "savegame.json"

**Design Decisions**:
- Uses `dataclasses.asdict()` for automatic serialization
- UTF-8 encoding for Chinese character support
- Pretty-printed JSON (`indent=2`, `ensure_ascii=False`)
- Comprehensive error handling (IOError, JSONDecodeError, KeyError)
- Clears game messages on load (fresh log)
- Returns error strings for user-friendly messages

**Serialization Details**:
- Nested dataclasses automatically converted
- Dictionaries and lists preserved
- Type reconstruction on load (City, Officer, Faction objects)

**Example**:
```python
from src import persistence
from src.models import GameState

gs = GameState()
# ... play game ...

# Save
if persistence.save_game(gs, "my_save.json"):
    print("Saved successfully")
else:
    print("Save failed")

# Load
gs2 = GameState()
error = persistence.load_game(gs2, "my_save.json")
if error:
    print(f"Load failed: {error}")
else:
    print("Loaded successfully")
    # Continue playing with gs2
```

### game.py (~380 lines, not tested directly)

**Purpose**: User interface layer using adventurelib for text adventure commands.

**Structure**:
- Global `STATE = GameState()` instance
- Wrapper functions calling module functions
- 30+ `@when()` command decorators
- Bilingual command support

**Key Commands**:
- `help/幫助`: List commands
- `choose/選擇 FACTION`: Select player faction
- `status/狀態 CITY`: View city details
- `officers/武將`: List all officers
- `assign/指派 OFFICER to TASK at CITY`: Assign work
- `march/行軍 from CITY to DEST with SIZE`: Attack
- `reward/賞賜 OFFICER with AMOUNT`: Increase loyalty
- `turn/結束`: End turn (AI processes)
- `save/保存`: Save game
- `load/讀取`: Load game

**Design Decisions**:
- Thin wrapper over module functions
- Uses `i18n.t()` for all user-facing text
- Input validation before calling modules
- User-friendly error messages
- Delegates all logic to modules

**Example**:
```python
@when("status CITY")
@when("狀態 CITY")
def status_cmd(city):
    msg = utils.format_city_status(STATE, city)
    say(msg)

@when("turn")
@when("結束")
def turn_cmd():
    engine.end_turn(STATE)
    if engine.check_victory(STATE):
        say("Game Over!")
```

## Testing Strategy

### Unit Tests (136 tests)

Each module has dedicated unit tests:
- **test_models.py** (18 tests): Dataclass construction, defaults, serialization
- **test_utils.py** (37 tests): Pure function correctness
- **test_engine.py** (35 tests): Game mechanics isolated
- **test_world.py** (25 tests): World generation and data validation
- **test_persistence.py** (21 tests): Save/load correctness, error handling

### Integration Tests (17 tests)

End-to-end flows in **test_integration.py**:
- Full game initialization
- Complete turn cycles
- Battle and city transfer
- Officer assignment workflows
- Save/load/resume game
- Victory condition triggers
- AI behavior
- Multi-turn progression

### Coverage Strategy

- **Target**: >80% per module, >90% overall
- **Achieved**: 99% overall coverage
- **Missing**: Error branches, rare edge cases (6 statements)
- **Tools**: pytest, pytest-cov

### Test Fixtures

- `pytest.fixture` for GameState setup
- `tmp_path` for file I/O tests
- Deterministic randomization via seeds

## Data Flow

### Typical Turn Flow

```
Player Command (game.py)
    ↓
Validate Input (utils.py)
    ↓
Execute Action (engine.py)
    ↓
Modify GameState (models.py)
    ↓
Format Output (utils.py)
    ↓
Display to Player (game.py + i18n)
```

### Turn End Flow

```
end_turn() called
    ↓
1. process_assignments() → Apply officer tasks
    ↓
2. monthly_economy() → Income, upkeep, starvation
    ↓
3. ai_turn() for each AI faction → Assign tasks, attack
    ↓
4. try_defections() → Check loyalty defections
    ↓
5. Advance month/year
    ↓
6. Recover idle officer energy
    ↓
7. check_victory() → Win/lose detection
```

### Save/Load Flow

```
Save:
GameState (in-memory)
    ↓ asdict()
Dict[str, Any]
    ↓ json.dumps()
JSON string
    ↓ file.write()
savegame.json (disk)

Load:
savegame.json (disk)
    ↓ file.read()
JSON string
    ↓ json.loads()
Dict[str, Any]
    ↓ reconstruct objects
GameState (in-memory)
```

## Performance Considerations

- **Complexity**: O(officers + cities) per turn
- **Memory**: ~1MB for typical game state
- **Disk**: ~50KB JSON save file
- **Startup**: <0.5s to load and initialize

## Future Improvements

### Potential Enhancements

1. **More Factions**: Add Han, Dong Zhuo, Yuan Shao
2. **More Cities**: Expand map to 15-20 cities
3. **Diplomacy**: Alliances, trade agreements, marriages
4. **Events**: Random historical events affecting game
5. **Campaign Mode**: Scripted scenarios from history
6. **Multiplayer**: Hot-seat or network play
7. **Graphics**: Terminal UI with rich/textual
8. **AI**: More sophisticated decision-making

### Extensibility

The modular architecture makes additions straightforward:

- **New Traits**: Add to `constants.TRAIT_BONUSES`
- **New Tasks**: Add to `constants.TASK_TYPES`, implement in `engine.assignment_effect()`
- **New Commands**: Add `@when()` decorator in `game.py`, call module functions
- **New Resources**: Extend `City` dataclass, update economy functions
- **New Victory Conditions**: Modify `engine.check_victory()`

### Maintenance Guidelines

1. **Keep modules focused**: Don't let modules grow beyond 300 lines
2. **Test first**: Write tests before implementing features
3. **Document functions**: Comprehensive docstrings with examples
4. **Type hints**: Use for all function signatures
5. **No circular imports**: Maintain dependency hierarchy
6. **Pure when possible**: Prefer pure functions over stateful

## Conclusion

The refactored architecture achieves:
- ✅ Modularity (6 focused modules)
- ✅ Testability (153 tests, 99% coverage)
- ✅ Maintainability (clear responsibilities)
- ✅ Extensibility (easy to add features)
- ✅ Type Safety (comprehensive hints)
- ✅ Documentation (docstrings + this file)

This design supports long-term development while keeping the codebase understandable and maintainable.
