
# Sango Text Sim — A Three Kingdoms Strategy Game (EN/中文)

A bilingual text-based strategy game set in the Three Kingdoms era, featuring officer management, city development, diplomacy, and turn-based gameplay.

## Features

- **Bilingual Support**: Play in English or Chinese (中文)
- **Officer System**: Recruit and manage legendary officers with unique stats and traits
- **City Management**: Develop cities through farming, trade, research, training, and fortification
- **Turn-Based Strategy**: AI opponents, seasonal events, and victory conditions
- **Save/Load**: Persist your game progress to JSON files
- **Trait System**: Officers have special abilities that boost specific tasks
- **Loyalty System**: Manage officer loyalty to prevent defections

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

```
sango-text-sim/
├── src/                    # Source code modules
│   ├── models.py          # Data models (Officer, City, Faction, GameState)
│   ├── constants.py       # Game constants and configuration
│   ├── utils.py           # Helper functions and formatting
│   ├── engine.py          # Core game mechanics (battles, economy, AI)
│   ├── world.py           # World initialization and data
│   └── persistence.py     # Save/load functionality
├── tests/                  # Comprehensive test suite (153 tests, 99% coverage)
│   ├── test_models.py
│   ├── test_utils.py
│   ├── test_engine.py
│   ├── test_world.py
│   ├── test_persistence.py
│   └── test_integration.py
├── locales/               # I18n translations
│   ├── en.json
│   └── zh.json
├── game.py                # Main game loop and adventurelib interface
└── i18n.py                # Internationalization support

468 total statements | 99% test coverage | 153 passing tests
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed module documentation.

## Installation

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

Start the game:
```bash
python game.py
```

### Example Commands (English)
```
help                          # List all commands
choose Shu                    # Choose Liu Bei's faction
status Chengdu                # View city status
officers                      # List all officers
assign 關羽 to farm at Chengdu  # Assign officer to task
march from Chengdu to Hanzhong with 1000  # Attack adjacent city
reward 關羽 with 200           # Increase loyalty with gold
turn                          # End turn and process AI
save                          # Save game
load                          # Load game
```

### Example Commands (Chinese)
```
幫助
選擇 蜀
狀態 Chengdu
武將
指派 關羽 至 農業 於 Chengdu
行軍 從 Chengdu 至 Hanzhong 以 1000
賞賜 關羽 以 200
結束
保存
讀取
```

## Officer Traits

- **Brave 勇猛**: +8% attacking power
- **Strict 嚴整**: +10% train effectiveness
- **Benevolent 仁德**: +10% farm effectiveness
- **Charismatic 魅力**: +10% recruit effectiveness
- **Scholar 學士**: +10% research effectiveness
- **Engineer 工師**: +10% defense, +10% fortify effectiveness
- **Merchant 商賈**: +10% trade effectiveness

## Loyalty System

- Officers start with **60-90** loyalty
- Successful assignments: **+1** loyalty
- Overworked (energy ≤ 10): **-2** loyalty
- Battle victory: **+2** loyalty
- Battle defeat: **-1** loyalty
- Officers below **35 loyalty**: **10% monthly defection chance**
- Use `reward` command to increase loyalty (costs gold)

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_engine.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v
```

**Test Statistics**:
- Total Tests: 153
- Coverage: 99%
- Test Files: 6
- Unit Tests: 136
- Integration Tests: 17

## Development

### Project Structure

- **models.py**: Dataclasses for game entities (immutable core data)
- **constants.py**: Game balance parameters and configuration
- **utils.py**: Pure functions for calculations and formatting
- **engine.py**: Game mechanics (battles, economy, AI, turn processing)
- **world.py**: World generation and initialization data
- **persistence.py**: JSON serialization for save/load
- **game.py**: User interface layer (adventurelib commands)

### Adding New Features

1. Define data models in `models.py`
2. Add constants to `constants.py`
3. Implement logic in appropriate module (engine, world, etc.)
4. Write unit tests achieving >80% coverage
5. Add integration tests for end-to-end flows
6. Update `game.py` commands as needed
7. Add i18n translations to `locales/*.json`

### Code Quality

- Follows Python 3.8+ type hints
- Comprehensive docstrings on all functions
- Test-driven development (TDD) approach
- Modular design with clear separation of concerns
- No circular dependencies between modules

## Game Mechanics

### Cities
Each city has:
- **Resources**: Gold, Food, Troops
- **Development**: Agriculture, Commerce, Technology, Walls
- **Stats**: Defense, Morale

### Officers
Each officer has:
- **Stats**: Leadership, Intelligence, Politics, Charisma
- **Status**: Energy (0-100), Loyalty (0-100)
- **Traits**: Special abilities
- **Assignment**: Current task and location

### Tasks
- **Farm 農業**: Increase food production (Politics-based)
- **Trade 貿易**: Increase gold income (Charisma-based)
- **Research 研究**: Improve technology (Intelligence-based)
- **Train 訓練**: Recruit troops (Leadership-based)
- **Fortify 防禦**: Strengthen defenses (Leadership-based)
- **Recruit 募兵**: Create new officers (Charisma-based)

### Victory Conditions
- **Win**: Control all cities
- **Lose**: Lose all cities

## Requirements

- Python 3.8+
- adventurelib 1.2.1
- pytest 5.4.3
- pytest-cov 5.0.0

## License

See [LICENSE](LICENSE) file.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Maintain or improve code coverage
6. Submit a pull request

---

**Note**: This refactoring transformed a 704-line monolithic script into a modular, well-tested codebase with 99% coverage and 153 passing tests.
