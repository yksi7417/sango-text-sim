# AI-Assisted Development Setup

This folder contains all files for running Claude Code in autonomous loop mode (Ralph methodology).

## Quick Start

```powershell
# Run the autonomous loop
.\.ai\loop.ps1

# With custom settings
.\.ai\loop.ps1 -MaxIterations 50 -Model opus -DelaySeconds 10
```

## File Structure

```
.ai/
├── README.md                      # This file
├── CLAUDE.md                      # Instructions for Claude Code
├── BEST_PRACTICES.md              # AI development best practices
├── ACCEPTANCE_CRITERIA_TEMPLATE.md # Template for writing tasks
├── tasks.json                     # Task tracking (PRD equivalent)
├── progress.txt                   # Append-only iteration log
├── loop.ps1                       # PowerShell automation script
└── loop.log                       # Loop execution log (auto-generated)
```

## How It Works

1. **loop.ps1** spawns Claude Code with fresh context each iteration
2. Claude reads **CLAUDE.md** for instructions
3. Claude selects highest-priority task from **tasks.json**
4. Claude implements, tests, and commits
5. Progress logged to **progress.txt**
6. Loop continues until all tasks complete or max iterations

## Adding Tasks

Edit `tasks.json` to add new tasks:

```json
{
  "id": "task-001",
  "priority": 1,
  "title": "Add energy validation",
  "description": "Validate officer energy before assignment",
  "acceptance_criteria": [
    "ValueError raised when energy < 10",
    "Test added for edge case",
    "Both locale files updated"
  ],
  "status": "pending",
  "model_hint": "sonnet"
}
```

See `ACCEPTANCE_CRITERIA_TEMPLATE.md` for detailed guidance.

## Token Optimization

| Task Complexity | Model | Use Case |
|-----------------|-------|----------|
| Simple | haiku | Formatting, simple tests |
| Standard | sonnet | Features, bug fixes |
| Complex | opus | Architecture, debugging |

## Observing Progress

While the loop runs, you can:
- Watch the terminal for real-time output
- Check `progress.txt` for iteration history
- Check `loop.log` for detailed logs
- View `tasks.json` for task status

## Stopping the Loop

- **Ctrl+C**: Graceful stop
- **Automatic**: When all tasks have `"status": "passed"`
- **Max iterations**: Default 100, configurable

## References

- [Ralph Methodology](https://ghuntley.com/ralph/)
- [snarktank/ralph](https://github.com/snarktank/ralph)
- [MIT Recursive Language Models](https://arxiv.org/abs/2512.24601)
