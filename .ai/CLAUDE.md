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

# CLAUDE.md (reset)

Welcome to the sango-text-sim project! This file has been reset for a new project start.

## Instructions

1. Review tasks.json for the current roadmap and tasks.
2. Begin with foundational tasks in Phase 1.
3. Update this file with learnings, design notes, and key decisions as you progress.

---

_This file will be updated as the project advances._
