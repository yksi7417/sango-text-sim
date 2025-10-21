# Sango Text Sim - Refactoring Plan

## Current State
- Single large file: `game.py` (~704 lines)
- All logic mixed together: models, game engine, commands, utilities
- No tests
- Hard to maintain and extend

## Target Architecture

### Directory Structure
```
sango-text-sim/
├── src/
│   ├── __init__.py
│   ├── models.py          # Data models (Officer, City, Faction, GameState)
│   ├── constants.py       # Game constants (TASKS, TASK_SYNONYMS, ALIASES)
│   ├── engine.py          # Core game mechanics (battle, economy, assignments)
│   ├── world.py           # World initialization (init_world, add_officer)
│   ├── ai.py              # AI behavior (ai_turn, try_defections)
│   ├── utils.py           # Helper functions (clamp, validations, queries)
│   └── persistence.py     # Save/load game state
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_models.py     # Test data models
│   ├── test_engine.py     # Test game mechanics
│   ├── test_utils.py      # Test utilities
│   ├── test_ai.py         # Test AI behavior
│   ├── test_world.py      # Test world initialization
│   └── test_integration.py # End-to-end tests
├── locales/
│   ├── en.json
│   └── zh.json
├── game.py                # Main entry point with adventurelib commands
├── i18n.py                # Internationalization
├── requirements.txt       # Dependencies
├── pytest.ini             # Pytest configuration
└── README.md              # Documentation

```

## Module Breakdown

### 1. **src/models.py** (~100 lines)
**Purpose**: Pure data models with no game logic dependencies

**Contents**:
- `Officer` dataclass (name, stats, loyalty, energy, traits, assignments)
- `City` dataclass (resources, military, development stats)
- `Faction` dataclass (relations, cities, officers)
- `GameState` dataclass (global state container with log method)

**Testing Strategy**:
- Test dataclass initialization
- Test default values
- Test GameState.log() method
- Test serialization/deserialization with asdict()

---

### 2. **src/constants.py** (~30 lines)
**Purpose**: Centralized game constants

**Contents**:
- `TASKS` list
- `TASK_SYNONYMS` dictionary (English + Chinese synonyms)
- `ALIASES` dictionary (keyword translations)
- Default game settings (starting year, month, etc.)

**Testing Strategy**:
- Test constant values exist
- Test task synonym lookups
- Minimal testing needed (mostly data)

---

### 3. **src/engine.py** (~200 lines)
**Purpose**: Core game mechanics and business logic

**Contents**:
- **Combat**: `battle()`, `tech_attack_bonus()`, `transfer_city()`
- **Assignments**: `assignment_effect()`, `process_assignments()`, `trait_mult()`
- **Economy**: `monthly_economy()`
- **Turn Management**: `end_turn()`, `check_victory()`

**Key Dependencies**: models, utils, constants
**State Management**: Accepts GameState as parameter (dependency injection)

**Testing Strategy**:
- Test battle outcomes with various scenarios
- Test tech bonuses and trait effects
- Test assignment effects (farm, trade, research, etc.)
- Test economy calculations (income, upkeep, starvation)
- Test victory/defeat conditions
- Mock random for deterministic tests

---

### 4. **src/world.py** (~100 lines)
**Purpose**: Game initialization and world building

**Contents**:
- `init_world(game_state, player_choice)` - Initialize cities, factions, officers
- `add_officer(game_state, officer)` - Add officer to game
- City data templates
- Officer data templates
- Adjacency map

**Testing Strategy**:
- Test world initialization
- Test different faction choices
- Test officer assignment to factions
- Verify city count and ownership
- Test adjacency relationships

---

### 5. **src/ai.py** (~80 lines)
**Purpose**: AI opponent behavior

**Contents**:
- `ai_turn(game_state, faction_name)` - AI decision making
- `try_defections(game_state)` - Loyalty-based defection logic

**Testing Strategy**:
- Test AI task assignments
- Test AI attack decisions
- Test defection logic (low loyalty scenarios)
- Mock random for predictable AI behavior
- Test AI respects energy constraints

---

### 6. **src/utils.py** (~100 lines)
**Purpose**: Helper functions and queries

**Contents**:
- Math: `clamp(v, lo, hi)`
- Validation: `valid_city()`, `ensure_player_city()`, `is_adjacent()`
- Queries: `officer_by_name()`, `officers_in_city()`, `task_key()`
- Display: `print_status()` (returns formatted strings instead of using say())

**Testing Strategy**:
- Test clamp with edge cases (below min, above max, in range)
- Test city validation (exists, doesn't exist)
- Test adjacency checks
- Test officer queries
- Test task synonym resolution

---

### 7. **src/persistence.py** (~50 lines)
**Purpose**: Save/load game state

**Contents**:
- `save_game(game_state, filepath)` - Serialize to JSON
- `load_game(filepath)` - Deserialize from JSON
- Helper functions for JSON conversion

**Testing Strategy**:
- Test save creates valid JSON file
- Test load restores game state correctly
- Test missing file handling
- Test corrupted save handling
- Use temporary files in tests

---

### 8. **game.py** (~250 lines - reduced from 704)
**Purpose**: Main entry point with adventurelib command interface

**Contents**:
- Global STATE instance
- All @when decorated command functions
- Command handlers import and call functions from modules
- `main()` function

**Key Changes**:
- Import from modules: `from src.models import GameState, Officer, City`
- Pass STATE to functions: `engine.battle(STATE, attacker, defender, troops)`
- Keep adventurelib integration isolated here

---

## Refactoring Steps

### Phase 1: Setup (30 min)
1. Create `src/` and `tests/` directories
2. Create `__init__.py` files
3. Update `requirements.txt` with pytest dependencies
4. Create `pytest.ini` configuration
5. Create `tests/conftest.py` with shared fixtures

### Phase 2: Extract Models (20 min)
1. Create `src/models.py` with all dataclasses
2. Update imports in `game.py`
3. Write `tests/test_models.py`
4. Run tests to verify

### Phase 3: Extract Constants (10 min)
1. Create `src/constants.py`
2. Update imports in `game.py`
3. Minimal testing needed

### Phase 4: Extract Utilities (30 min)
1. Create `src/utils.py`
2. Move utility functions
3. Update function signatures to accept `game_state` parameter
4. Update imports in `game.py`
5. Write `tests/test_utils.py`
6. Run tests

### Phase 5: Extract Engine (45 min)
1. Create `src/engine.py`
2. Move core game mechanics
3. Refactor to accept `game_state` parameter (remove global STATE dependency)
4. Update calls in `game.py`
5. Write `tests/test_engine.py` with comprehensive battle/economy tests
6. Run tests

### Phase 6: Extract World (20 min)
1. Create `src/world.py`
2. Move initialization functions
3. Update imports in `game.py`
4. Write `tests/test_world.py`
5. Run tests

### Phase 7: Extract AI (25 min)
1. Create `src/ai.py`
2. Move AI functions
3. Update calls in `game.py`
4. Write `tests/test_ai.py`
5. Run tests

### Phase 8: Extract Persistence (20 min)
1. Create `src/persistence.py`
2. Move save/load functions
3. Update command handlers in `game.py`
4. Write `tests/test_persistence.py`
5. Run tests

### Phase 9: Integration Tests (30 min)
1. Create `tests/test_integration.py`
2. Test full game flows (turn progression, battles, victory)
3. Test command sequences
4. Run full test suite

### Phase 10: Documentation (20 min)
1. Update `README.md` with new structure
2. Add architecture diagram
3. Document testing commands
4. Add module docstrings

**Total Estimated Time**: ~4 hours

## Benefits

### Code Quality
- **Separation of Concerns**: Each module has single responsibility
- **Testability**: Pure functions without global state dependencies
- **Maintainability**: Smaller, focused files easier to understand
- **Reusability**: Core logic can be used in different interfaces (GUI, web, etc.)

### Testing
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test complete game flows
- **Coverage**: Aim for >80% code coverage
- **Regression Prevention**: Catch bugs before they reach users

### Development
- **Parallel Work**: Multiple developers can work on different modules
- **Refactoring Safety**: Tests catch breaking changes
- **Feature Addition**: Clear where to add new functionality
- **Bug Fixing**: Easier to locate and fix issues

## Testing Strategy

### Test Fixtures (conftest.py)
```python
@pytest.fixture
def empty_game_state():
    """Clean GameState for testing"""
    return GameState()

@pytest.fixture
def populated_game_state():
    """GameState with cities, factions, officers"""
    state = GameState()
    init_world(state, "Shu")
    return state

@pytest.fixture
def test_officer():
    """Sample officer for testing"""
    return Officer("TestOfficer", "Shu", 80, 70, 60, 75)

@pytest.fixture
def test_city():
    """Sample city for testing"""
    return City("TestCity", "Shu", gold=500, food=800, troops=300)
```

### Test Categories
1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test module interactions
3. **Smoke Tests**: Basic functionality works
4. **Edge Cases**: Boundary conditions, error handling
5. **Regression Tests**: Verify bug fixes stay fixed

### Coverage Goals
- **Critical Paths**: 100% (battle, economy, turn progression)
- **Business Logic**: >90% (assignments, AI, loyalty)
- **Utilities**: >85%
- **Overall**: >80%

## Migration Safety

### Backward Compatibility
- Keep `game.py` as main entry point
- Preserve adventurelib command interface
- Maintain save file format compatibility

### Testing During Migration
- Run game after each phase to ensure it still works
- Keep existing functionality while refactoring
- Use Git branches for each phase

### Rollback Strategy
- Each phase is a separate commit
- Tag working versions
- Can revert individual changes if needed

## Future Enhancements

After refactoring, easier to add:
- Web interface (Flask/FastAPI)
- Graphical UI (PyQt, Tkinter)
- Multiplayer support
- Additional factions and scenarios
- Mod support (JSON-based data files)
- Performance optimizations
- Save file versioning

## Commands to Run

```powershell
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_engine.py -v

# Run tests matching pattern
pytest -k "battle" -v

# Run with detailed output
pytest -vv

# Watch mode (install pytest-watch)
ptw
```

## Questions to Consider

1. **State Management**: Keep global STATE or pass it around?
   - **Recommendation**: Pass as parameter for testability, keep global in game.py for commands

2. **say() function**: Mock in tests or refactor?
   - **Recommendation**: Have utils return strings, game.py calls say()

3. **Random**: Mock in tests or use seeds?
   - **Recommendation**: Both - use seeds for integration, mocks for unit tests

4. **i18n**: Keep separate or integrate?
   - **Recommendation**: Keep separate, import where needed

5. **adventurelib dependency**: Isolate or spread?
   - **Recommendation**: Keep in game.py only, modules are adventurelib-free

## Success Criteria

✅ All tests passing
✅ Game plays exactly as before refactoring
✅ Code coverage >80%
✅ Each module <250 lines
✅ No circular dependencies
✅ All functions have docstrings
✅ README updated
✅ Can run pytest without errors

---

**Author**: GitHub Copilot
**Date**: 2025-10-18
**Version**: 1.0
