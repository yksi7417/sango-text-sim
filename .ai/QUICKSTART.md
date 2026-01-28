# Quick Start Guide - Autonomous Development

## Overview

This project uses an autonomous development loop where Claude Code works through tasks iteratively, maintaining progress across sessions through git commits and status files.

## Running the Autonomous Loop

### Option 1: PowerShell Loop Script (Recommended)

```powershell
# From project root
.\.ai\loop.ps1

# With options
.\.ai\loop.ps1 -MaxIterations 50 -Model opus -DelaySeconds 10
```

This runs continuous iterations until all tasks complete or max iterations reached.

### Option 2: Single Iteration (Manual)

```powershell
# Run one iteration manually
claude --model opus --dangerously-skip-permissions

# Then say:
# "Continue autonomous development. Read .ai/tasks.json and work on the highest priority pending task."
```

### Option 3: Interactive Development

```powershell
claude

# Then work interactively, asking Claude to:
# 1. Read tasks.json and pick a task
# 2. Implement it
# 3. Run tests
# 4. Update task status
```

## Task Workflow

Each task follows this lifecycle:

```
pending → in_progress → passed
                     → blocked (if issues found)
```

### Task Structure

Tasks in `tasks.json` have:
- **id**: Unique identifier (e.g., "p1-01" = Phase 1, Task 1)
- **phase**: Development phase (1-4)
- **priority**: Execution order (lower = higher priority)
- **title**: What to build
- **description**: Detailed requirements
- **acceptance_criteria**: Definition of done
- **depends_on**: Prerequisite tasks
- **status**: Current state

### Completing a Task

1. Set status to "in_progress"
2. Implement the feature
3. Write tests (TDD!)
4. Run `python -m pytest --no-cov -v`
5. If passing, set status to "passed"
6. Git commit with descriptive message
7. Update progress.txt with learnings

## Phase Overview

| Phase | Focus | Tasks |
|-------|-------|-------|
| 1 | Core Experience | ASCII map, turn reports, dialogue, battle narratives |
| 2 | Strategic Depth | Unit types, relationships, events, tech tree |
| 3 | Narrative | Historical events, legendary officers, achievements |
| 4 | Advanced | Naval, siege, alliance, scenarios |

## Commands Reference

```bash
# Run tests (required before any commit)
python -m pytest --no-cov -v

# Run with coverage
python -m pytest --cov=src --cov-report=term-missing

# Play the game (CLI)
python game.py

# Run web server
python web_server.py
```

## Stop Conditions

The autonomous loop stops when:
1. All tasks in tasks.json have `"status": "passed"`
2. Claude outputs `<promise>COMPLETE</promise>`
3. Max iterations reached
4. User presses Ctrl+C

## Monitoring Progress

Check these files:
- `.ai/tasks.json` - Current task statuses
- `.ai/progress.txt` - Iteration log and learnings
- `.ai/loop.log` - Loop execution history
- `git log --oneline` - Committed changes

## Troubleshooting

### Tests failing
- Check error messages carefully
- Don't skip tests - fix the issue
- Ensure both locale files updated for UI changes

### Task too large
- Break into smaller sub-tasks
- Add new tasks with `depends_on` linking

### Stuck on a task
- Mark as "blocked" with notes
- Move to next priority task
- Come back later with fresh context

## Best Practices

1. **One task per iteration** - Focus on completing one thing well
2. **Tests first** - Write test, then implementation
3. **Small commits** - Commit after each meaningful change
4. **Log learnings** - Document gotchas in progress.txt
5. **Keep moving** - If stuck, move on and return later
