# Claude Code Autonomous Instructions

> Instructions for Claude Code when operating in autonomous loop mode.

## Project: Sango Text Sim

Bilingual (English/Chinese) text-based Three Kingdoms strategy game.

**Vision**: Transform into an addictive ROTK-like experience through ASCII maps, narrative battles, officer conversations, and strategic depth. See `.ai/VISION.md` for full details.

## Operational Mode

You are running in **autonomous loop mode**. Each iteration:

1. Read `tasks.json` to find the highest-priority pending task (lowest priority number)
2. Check `depends_on` - skip if dependencies not yet passed
3. Implement the task following all quality standards
4. Run tests to verify: `python -m pytest --no-cov -v`
5. If tests pass: commit and push changes
6. Verify deployment at https://sango-text-sim.fly.dev/ - play game briefly
7. If deployment works: update task status to "passed"
8. Log learnings to `progress.txt`
9. If ALL tasks have `"status": "passed"`, output: `<promise>COMPLETE</promise>`

## Critical Rules

### Testing (MANDATORY)
```bash
# ALL 201+ tests MUST pass before any commit
python -m pytest --no-cov -v

# Maintain 96%+ coverage
python -m pytest --cov=src --cov-report=term-missing
```

### Internationalization (MANDATORY)
- NEVER hardcode display text in Python code
- Update BOTH `locales/en.json` AND `locales/zh.json`
- Use `i18n.t("key.subkey", param=value)` pattern

### Code Quality
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write tests FIRST (TDD approach)
- Keep changes minimal and focused

## Task Structure

Tasks in `tasks.json`:
```json
{
  "id": "p1-01",          // Phase 1, Task 1
  "phase": 1,             // Development phase
  "priority": 1,          // Lower = higher priority
  "title": "Short title",
  "description": "What to build",
  "acceptance_criteria": ["List", "of", "requirements"],
  "depends_on": ["p1-00"], // Must complete first
  "status": "pending"     // pending | in_progress | passed | blocked
}
```

## Per-Iteration Workflow

### 1. Select Task
```
Read tasks.json
Find lowest priority number with status="pending"
Check depends_on - all must be "passed"
Update status to "in_progress"
```

### 2. Implement
```
Read relevant source files
Write tests first (tests/test_*.py)
Implement minimal solution
Update both locale files if UI text added
```

### 3. Verify
```bash
python -m pytest --no-cov -v
# Must see: "X passed in Ys"
# Zero failures allowed
```

### 4. Complete
```bash
# Stage and commit
git add <specific files>
git commit -m "feat: <description>

Implements task <id>
- <change 1>
- <change 2>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### 5. Deploy & Verify (MANDATORY)
After commit is pushed:
1. Wait for GitHub Actions to complete deployment
2. Visit https://sango-text-sim.fly.dev/
3. Play the game briefly to verify the feature works
4. Only mark task as "passed" after live verification succeeds

**Deployment Pipeline:**
- Commits auto-push to GitHub
- GitHub Actions triggers deployment to Fly.dev
- Live site: https://sango-text-sim.fly.dev/

### 6. Update Status
In `tasks.json`, change task status to "passed"

### 7. Log Progress
Append to `progress.txt`:
```
[TIMESTAMP] [ITER-N] [PASS] Completed <task-id>: <brief summary>
```

## File Organization

```
src/                 - Core game logic
  models.py          - Data classes (Officer, City, Faction, GameState)
  engine.py          - Game mechanics (end_turn, attack, etc.)
  constants.py       - Game balance numbers
  utils.py           - Helper functions
  world.py           - Initial game data
  persistence.py     - Save/load

tests/               - Test suite (mirrors src/)
  test_*.py          - One test file per module

locales/             - Translations
  en.json            - English strings
  zh.json            - Chinese strings

templates/           - Web interface
  game.html          - Main template

.ai/                 - Automation config
  tasks.json         - Task tracking
  progress.txt       - Iteration log
  VISION.md          - Feature roadmap
  QUICKSTART.md      - Usage guide
```

## New Module Pattern

When creating a new module (e.g., `src/map_renderer.py`):

1. Create test file first: `tests/test_map_renderer.py`
2. Write failing tests
3. Create source file: `src/map_renderer.py`
4. Make tests pass
5. Add i18n keys to both locale files
6. Verify coverage: `python -m pytest --cov=src/map_renderer`

## Common Gotchas

- **game_started flag**: Check `game_state.game_started` before operations
- **Locale keys**: Must exist in BOTH en.json and zh.json
- **Type hints**: Use `Optional[T]` for nullable parameters
- **Test isolation**: Each test should work independently

## Token Optimization

- Use `haiku` for simple tasks (formatting, small fixes)
- Use `sonnet` for standard development
- Reserve `opus` for complex architectural decisions
- Read only necessary files, not entire codebase
- Use grep/glob for targeted searches

## Stop Condition

When ALL tasks in tasks.json have `"status": "passed"`:

```
<promise>COMPLETE</promise>
```

This signals the loop to stop.
