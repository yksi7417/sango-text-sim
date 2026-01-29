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
# ALL 785+ tests MUST pass before any commit
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

## Development Phases

| Phase | Name | Goal | Tasks |
|-------|------|------|-------|
| 1 | Extensible Foundation & Visual Enhancement | Data-driven architecture and ASCII visualization | 12 |
| 2 | Interactive Combat Systems | Duels, tactical battles, and dramatic combat | 10 |
| 3 | Deep Strategy Layer | Council system, relationships, events | 10 |
| 4 | Narrative & Polish | Historical events, achievements, turn preview | 8 |
| 5 | Full Game Scale | 40+ cities, naval, alliances, scenarios | 8 |
| 6 | Comprehensive Integration Tests | ROTK11-style deep gameplay validation based on 3KYuYun analysis | 20 |

## Phase 6: Integration Test Suite

Phase 6 adds comprehensive integration tests based on ROTK11 deep gameplay mechanics analyzed by the 3KYuYun YouTube channel. These tests validate:

### Combat System Tests (p6-01 to p6-03)
- Unit type rock-paper-scissors combat matrix
- Fire attack effectiveness across weather/terrain/naval conditions
- Duel system with ability triggers

### Officer System Tests (p6-04 to p6-05)
- Officer ability rankings and effectiveness
- Deputy general synergy mechanics

### Naval/Strategic Tests (p6-06 to p6-07)
- Naval combat superiority and water route blocking
- City defense mechanics and siege warfare

### Recruitment/Relationship Tests (p6-08 to p6-10)
- Capture and recruitment mechanics
- Sworn brotherhood bonuses
- Marriage and family system

### Economy/Tech Tests (p6-11 to p6-12)
- Technology research paths
- Building construction ROI

### Campaign/AI Tests (p6-13 to p6-14)
- Full campaign conquest validation
- AI difficulty scaling

### System Integration Tests (p6-15 to p6-20)
- Weather-season chain effects
- Supply line warfare
- Historical event triggers
- Multi-front war management
- Diplomatic alliance chains
- Complete web interface flow

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
Update i18n files if needed
```

### 3. Verify
```
python -m pytest --no-cov -v  # All tests pass
python -m pytest --cov=src    # Coverage >=96%
```

### 4. Complete
```
git add specific files
git commit with descriptive message
git push
Verify deployment at https://sango-text-sim.fly.dev/
Update task status to "passed" in tasks.json
Add notes to progress.txt
```

## Stop Signal

When ALL tasks complete, output:
```
<promise>COMPLETE</promise>
```
