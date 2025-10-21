# GitHub Copilot Instructions

This repository follows strict development practices to maintain code quality and reliability.

## Critical Rules

### 🧪 Testing is Mandatory
- **Every code change requires tests**
- **Always run `python -m pytest --no-cov -v` after Python changes**
- **Always run `npm test` after JavaScript changes**
- **All 187 tests must pass before committing**
- **Maintain 96%+ code coverage**

### 🌐 Internationalization (i18n)
- **Never hardcode display text** - use translation keys
- **Update both `locales/en.json` AND `locales/zh.json`**
- **Test in both English and Chinese modes**

### 🎮 Game State Management
- **Always validate `game_started` flag before menu operations**
- **Check faction initialization before game actions**
- **Menu navigation returns empty strings (buttons handle UI)**
- **Default to first city when `current_city` is None**

### 📝 Code Quality
- Follow PEP 8 for Python
- Use ES6+ for JavaScript
- Write descriptive commit messages
- Document complex logic
- No warnings or lint errors

### 📄 Documentation Management
- **Always update `README.md`** to reflect current reality (test counts, coverage, features)
- **Always put newly generated `.md` files into `doc/` folder**
- Keep documentation in sync with code changes
- Update relevant docs when adding features

## Full Documentation

See [`COPILOT_INSTRUCTIONS.md`](../COPILOT_INSTRUCTIONS.md) for complete development guidelines, architecture patterns, and best practices.

## Before Every Commit

- [ ] All tests pass (187/187)
- [ ] Code coverage maintained (96%+)
- [ ] Both language files updated
- [ ] No lint errors
- [ ] Documentation updated (including README.md)
- [ ] New `.md` files placed in `doc/` folder
- [ ] Manual testing completed

## Quick Commands

```bash
# Run all tests
python -m pytest --no-cov -v

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest --no-cov tests/test_menu_internal_affairs.py
```

## Common Patterns

### Adding a New Feature
1. Write tests first (TDD)
2. Implement feature
3. Update translations (en.json + zh.json)
4. Run test suite
5. Manual testing in browser
6. Update documentation
7. Update README.md with new feature/test counts
8. Place new `.md` docs in `doc/` folder

### Fixing a Bug
1. Create failing test demonstrating bug
2. Fix the bug
3. Verify test passes
4. Run full test suite
5. Check for similar issues

---

**Remember:** Tests are not optional. Every change needs tests. Every commit needs passing tests.

--- 

