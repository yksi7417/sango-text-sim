# Copilot Instructions for Sango Text Sim

## Core Development Principles

### Test-Driven Development (TDD)
**Every code change MUST include corresponding tests.**

1. **Before Making Changes:**
   - Identify which tests will be affected
   - Plan what new tests are needed

2. **For Each Code Change:**
   - ✅ Add or update unit tests in `tests/` directory
   - ✅ Add or update integration tests when changing system interactions
   - ✅ Ensure tests cover both success and failure cases
   - ✅ Test edge cases and boundary conditions

3. **After Making Changes:**
   - **ALWAYS run the full test suite:**
     ```bash
     python -m pytest --no-cov -v
     ```
   - **Fix any failing tests before proceeding**
   - **Maintain or improve code coverage (currently 96%)**

### Testing Requirements by Change Type

#### Backend Python Changes
- **REQUIRED:** Run pytest test suite
  ```bash
  python -m pytest --no-cov -v
  ```
- Write tests in appropriate test file:
  - `test_models.py` - Data models and classes
  - `test_engine.py` - Game mechanics and logic
  - `test_world.py` - World initialization
  - `test_utils.py` - Utility functions
  - `test_persistence.py` - Save/load functionality
  - `test_integration.py` - Multi-system interactions
  - `test_menu_*.py` - Menu system functionality
  - `test_web_signatures.py` - Web API contracts

#### Frontend JavaScript Changes
- **REQUIRED:** Run Jest test suite (when available)
  ```bash
  npm test
  ```
- Test user interactions and state management
- Verify translation/i18n functionality

#### Full-Stack Changes
- **REQUIRED:** Run both test suites
- Add integration tests covering frontend-backend interaction
- Test API contracts and data flow

### Code Quality Standards

#### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum function complexity: Keep functions focused and single-purpose
- Document complex logic with clear comments
- Use descriptive variable and function names

#### JavaScript Code
- Use ES6+ modern JavaScript syntax
- Prefer `const` over `let`, avoid `var`
- Use meaningful variable names
- Keep functions pure when possible
- Document non-obvious behavior

### Architecture Patterns

#### Game State Management
- **Session State:** Use `session_states` dictionary for menu navigation and UI state
- **Game State:** Use `game_states` dictionary for game data (factions, cities, officers)
- **Always validate:** Check `game_started` flag and faction existence before menu operations
- **State consistency:** Ensure backend and frontend state stay synchronized

#### Menu System
- Menu navigation must return empty strings (buttons handle UI)
- Always validate game initialization for non-pregame menus
- Use translation keys from `locales/*.json`, never hardcode text
- Default to first city when `current_city` is None

#### Internationalization (i18n)
- **Never hardcode display text** - always use translation keys
- Add keys to both `locales/en.json` and `locales/zh.json`
- Use `i18n.t(key, **params)` for backend translations
- Use `t(key, lang)` for frontend translations
- Test both English and Chinese language modes

### File Organization

```
src/              # Core game logic (Python)
  ├── models.py   # Data models (GameState, City, Officer, Faction)
  ├── engine.py   # Game mechanics (battles, economy, AI)
  ├── world.py    # World initialization
  ├── utils.py    # Helper functions
  └── persistence.py  # Save/load functionality

tests/            # Test suite (pytest)
  ├── conftest.py       # Shared test fixtures
  ├── test_*.py         # Test modules

templates/        # Frontend (HTML/JavaScript)
  └── game.html   # Single-page web interface

locales/          # Translations
  ├── en.json     # English
  └── zh.json     # Chinese

web_server.py     # Flask web server
i18n.py          # Translation system
game.py          # CLI interface
```

### Commit Guidelines

#### Before Committing
1. ✅ All tests pass (187/187)
2. ✅ Code coverage maintained or improved
3. ✅ No lint errors or warnings
4. ✅ Documentation updated if needed
5. ✅ Translation files updated for UI changes

#### Commit Message Format
```
<type>: <short summary>

<detailed description if needed>

Tests: <what tests were added/modified>
Coverage: <coverage percentage>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `docs:` Documentation changes
- `style:` Code style/formatting
- `chore:` Maintenance tasks

**Example:**
```
feat: Add default city selection for internal affairs

When current_city is None, automatically default to the first city
of the player's faction. This improves UX by eliminating the need
to manually select a city every time.

Tests: Updated test_internal_menu_requires_current_city
Coverage: 96%
```

### Error Handling

#### Backend
- Always validate user input
- Return descriptive error messages
- Use try-except for file operations and external calls
- Log errors appropriately

#### Frontend
- Handle network failures gracefully
- Show user-friendly error messages
- Don't expose technical details to users
- Validate data before sending to backend

### Performance Considerations

- **Session Management:** Store session data efficiently
- **State Calculations:** Cache computed values when appropriate
- **API Responses:** Only send necessary data
- **Frontend Updates:** Minimize DOM manipulations

### Security Best Practices

- Never commit secrets or API keys
- Validate all user input on backend
- Use environment variables for configuration
- Sanitize data before displaying in browser

### Documentation Requirements

#### Code Documentation
- Document complex algorithms
- Explain non-obvious design decisions
- Add docstrings to all functions and classes
- Keep comments up-to-date with code changes

#### Project Documentation
- Update `README.md` for user-facing changes
- Update architecture docs for structural changes
- Create new doc files for major features
- Keep `REFACTORING_PLAN.md` current
- **Always update `README.md` to reflect current reality** (test counts, coverage, features)
- **Always place newly generated `.md` files into `doc/` folder**

### Specific Project Rules

#### 1. Menu System
- Navigation commands return `""` (empty string)
- Buttons handle all UI rendering
- Menu state stored in `session_states`
- Always validate game initialization

#### 2. Translation System
- Load translations client-side (don't use API endpoints)
- Translation keys format: `menu.<menu>.<key>` or `ui.<component>`
- Support both English and Chinese
- Test language switching functionality

#### 3. Game State Persistence
- Game state must persist across button clicks
- Use `game_started` flag to track initialization
- Calculate `game_started` from actual game state, not just session flag
- Force pregame menu if game not initialized

#### 4. City Management
- Default to first faction city when `current_city` is None
- Validate city ownership before operations
- Update city in session state after selection

### When Adding New Features

1. **Plan First:**
   - Identify affected components
   - Plan API changes if needed
   - Design test cases

2. **Implement with Tests:**
   - Write failing tests first (TDD approach)
   - Implement feature
   - Make tests pass
   - Add integration tests

3. **Validate:**
   - Run full test suite
   - Test manually in browser
   - Test both languages
   - Check edge cases

4. **Document:**
   - Update relevant documentation
   - Add code comments
   - Update translation files

### When Fixing Bugs

1. **Reproduce:**
   - Create a failing test that demonstrates the bug
   - Understand root cause

2. **Fix:**
   - Implement fix
   - Verify test passes
   - Check for similar issues elsewhere

3. **Prevent Regression:**
   - Ensure test coverage
   - Run full test suite
   - Consider additional edge cases

### Debugging Checklist

When investigating issues:
- [ ] Check browser console for JavaScript errors
- [ ] Check backend logs for Python exceptions
- [ ] Verify API request/response in Network tab
- [ ] Confirm translation keys exist in both language files
- [ ] Validate game state and session state
- [ ] Check if game_started flag is set correctly
- [ ] Verify faction is properly initialized
- [ ] Test in both English and Chinese modes

### Common Pitfalls to Avoid

❌ **Don't:**
- Hardcode display text (use translation keys)
- Skip tests "temporarily"
- Commit code that fails tests
- Return menu text from navigation handlers
- Bypass game initialization checks
- Forget to update both language files
- Use menu output for web interface rendering

✅ **Do:**
- Use translation system consistently
- Write tests for every change
- Validate game state before operations
- Return empty strings from menu navigation
- Check game_started flag
- Update all affected language files
- Use buttons for web interface rendering
- Update README.md to reflect current reality
- Place new .md files in doc/ folder

### Questions to Ask Before Pushing

1. Did I run the full test suite?
2. Do all 187 tests pass?
3. Did I add/update tests for my changes?
4. Are both language files updated?
5. Is the code coverage maintained?
6. Did I test manually in the browser?
7. Did I update relevant documentation?
8. Did I update README.md with current metrics?
9. Did I place new .md files in doc/ folder?
10. Is the commit message descriptive?

---

## Quick Reference

### Run Tests
```bash
# Full test suite with verbose output
python -m pytest --no-cov -v

# Quick test (no verbose)
python -m pytest --no-cov -q

# Specific test file
python -m pytest --no-cov tests/test_menu_internal_affairs.py

# With coverage report
python -m pytest --cov=src --cov-report=html
```

### Test Expectations
- **Total Tests:** 187
- **Target Coverage:** 96%+
- **Test Categories:**
  - Engine: 35 tests
  - Integration: 17 tests
  - Menu/Internal Affairs: 23 tests
  - Models: 18 tests
  - Persistence: 21 tests
  - Utils: 33 tests
  - Web Signatures: 11 tests
  - World: 25 tests

### Key Files to Check
- `web_server.py` - Backend API and session management
- `templates/game.html` - Frontend UI and JavaScript
- `locales/en.json` & `locales/zh.json` - All UI text
- `src/world.py` - Game initialization
- `tests/test_*.py` - Test suite

---

**Remember:** Quality over speed. A well-tested, documented change is better than a quick, fragile one.
