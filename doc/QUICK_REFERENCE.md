# Development Quick Reference

## 🚨 CRITICAL: Run Before Every Commit

```bash
python -m pytest --no-cov -v
```

**Expected:** ✅ 187 passed, 96%+ coverage

---

## Test Commands

```bash
# Full suite (verbose)
python -m pytest --no-cov -v

# Quick run
python -m pytest --no-cov -q

# With coverage
python -m pytest --cov=src --cov-report=html

# Specific file
python -m pytest --no-cov tests/test_menu_internal_affairs.py

# JavaScript (when available)
npm test
```

---

## Golden Rules

### ✅ Always Do
- Write tests for every change
- Run full test suite before commit
- Update both `en.json` and `zh.json`
- Validate `game_started` flag
- Return `""` from menu navigation
- Use translation keys, never hardcode text
- Check faction before game operations

### ❌ Never Do
- Skip tests
- Hardcode display text
- Commit failing tests
- Return menu text from handlers
- Bypass game initialization
- Update only one language file
- Forget to test both languages

---

## File Locations

| What | Where |
|------|-------|
| Backend Logic | `src/*.py` |
| Tests | `tests/test_*.py` |
| Frontend | `templates/game.html` |
| Translations | `locales/en.json`, `locales/zh.json` |
| Web Server | `web_server.py` |
| CLI | `game.py` |

---

## Test Suite Breakdown

| Module | Tests | Purpose |
|--------|-------|---------|
| engine | 35 | Game mechanics |
| integration | 17 | System interactions |
| menu_internal_affairs | 23 | Menu system |
| models | 18 | Data structures |
| persistence | 21 | Save/load |
| utils | 33 | Helper functions |
| web_signatures | 11 | API contracts |
| world | 25 | Initialization |
| **TOTAL** | **187** | **Full suite** |

---

## Common Workflows

### 🆕 Add New Feature
1. Plan tests
2. Write failing tests (TDD)
3. Implement feature
4. Pass tests
5. Update `en.json` + `zh.json`
6. Run full suite
7. Manual browser test
8. Commit with tests

### 🐛 Fix Bug
1. Create failing test
2. Fix bug
3. Verify test passes
4. Run full suite
5. Check similar issues
6. Commit with tests

### 🔄 Refactor Code
1. Ensure tests exist
2. Run tests (baseline)
3. Refactor code
4. Run tests (verify)
5. No behavior changes
6. Commit

---

## Translation Keys Format

```
menu.<menu_name>.<key>     # Menu items
ui.<component>.<key>        # UI elements
```

**Example:**
```json
"menu.main.status": "Status",
"ui.help": "Help"
```

---

## Pre-Commit Checklist

- [ ] Tests written/updated
- [ ] `python -m pytest --no-cov -v` → 187 passed ✅
- [ ] Coverage ≥ 96%
- [ ] Both `en.json` and `zh.json` updated
- [ ] Manual browser test (English)
- [ ] Manual browser test (Chinese)
- [ ] No lint errors
- [ ] Documentation updated
- [ ] Commit message descriptive

---

## Emergency Fixes

### Tests Failing?
```bash
# See details
python -m pytest --no-cov -v

# Check specific file
python -m pytest --no-cov tests/test_[name].py -v

# Debug mode
python -m pytest --no-cov -vv -s
```

### State Issues?
- Check `game_started` flag
- Verify faction initialization
- Validate session state
- Check `current_city` default

### Translation Issues?
- Keys in both `en.json` and `zh.json`?
- Format: `menu.X.Y` or `ui.X`?
- Test language switching

---

## Key Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Tests | All pass | 187/187 ✅ |
| Coverage | ≥ 96% | 96% ✅ |
| Languages | Full i18n | EN + ZH ✅ |
| Lint Errors | Zero | 0 ✅ |

---

## Need More Info?

📖 **Full Guide:** `COPILOT_INSTRUCTIONS.md`  
📖 **Architecture:** `ARCHITECTURE.md`  
📖 **Menu System:** `MENU_SYSTEM.md`  
📖 **State Fixes:** `GAME_STATE_FIXES.md`

---

**Remember:** 🧪 Tests aren't optional. Quality over speed.
