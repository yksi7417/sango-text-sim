# Claude Code Instructions

> This file provides instructions for Claude Code when operating in autonomous loop mode (Ralph methodology).

## Identity & Context

You are working on **sango-text-sim**, a bilingual (English/Chinese) text-based Three Kingdoms strategy game built with Python/Flask.

## Operational Mode

You are running in **autonomous loop mode**. Each iteration:
1. Read `tasks.json` to find the highest-priority incomplete task
2. Implement the task following all quality standards
3. Run tests to verify
4. Commit changes with descriptive message
5. Update `tasks.json` and `progress.txt`
6. Output `<promise>COMPLETE</promise>` when ALL tasks pass

## Critical Rules

### Testing (Non-Negotiable)
- **ALL 200+ tests MUST pass** before any commit
- Run: `python -m pytest --no-cov -v`
- Maintain 96%+ code coverage
- Write tests FIRST (TDD approach)

### Internationalization (Non-Negotiable)
- NEVER hardcode display text
- Update BOTH `locales/en.json` AND `locales/zh.json`
- Test both language modes

### Code Quality
- Follow PEP 8
- Use type hints where appropriate
- No lint errors
- Keep changes minimal and focused

## Task Sizing Guidelines

Each task should be completable in ONE context window. Good examples:
- "Add validation for officer energy before assignment"
- "Create test for battle resolution edge case"
- "Add Chinese translation for new menu option"

Bad examples (too large):
- "Refactor entire combat system"
- "Add multiplayer support"

## File Organization

```
src/           - Core game logic (models, engine, utils)
tests/         - Test files (must mirror src/ structure)
templates/     - Web interface templates
locales/       - Translation files (en.json, zh.json)
doc/           - Documentation
.ai/           - AI automation files (you are here)
```

## Before Each Commit

- [ ] All tests pass (200+)
- [ ] Coverage maintained (96%+)
- [ ] Both language files updated if UI text changed
- [ ] No lint errors
- [ ] Changes are minimal and focused

## Memory Architecture

Fresh context each iteration. Persistence through:
- **Git history** - All committed changes
- **progress.txt** - Learnings and gotchas discovered
- **tasks.json** - Task status tracking

## Token Optimization

- Use `haiku` model for simple tasks (formatting, simple tests)
- Use `sonnet` model for standard development
- Reserve `opus` for complex architectural decisions
- Prefer targeted file reads over full codebase scans
- Use grep/glob for specific searches, not exploration

## Stop Condition

Output exactly: `<promise>COMPLETE</promise>`

This signals the loop to stop when:
- All tasks in `tasks.json` have `"status": "passed"`
- All tests pass
- No pending work remains
