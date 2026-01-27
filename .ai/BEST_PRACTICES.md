# AI-Assisted Development Best Practices

> Based on Ralph methodology, MIT RLM research, and production experience.

## Core Philosophy

"Each time the agent does something bad, the agent gets tuned - like a guitar."

Failures are tuning opportunities. Refine prompts and instructions based on observed agent behavior.

## Token Optimization Strategies

### 1. Model Selection by Task Complexity

| Task Type | Recommended Model | Examples |
|-----------|-------------------|----------|
| Simple formatting | Haiku | Fix indentation, add comments |
| Standard dev | Sonnet | Implement features, write tests |
| Complex reasoning | Opus | Architecture decisions, debugging complex issues |

### 2. Context Window Management

Based on MIT Recursive Language Model research:

- **Chunked Processing**: Break large tasks into smaller, focused subtasks
- **Programmatic Buffering**: Use external files (`progress.txt`, `tasks.json`) instead of context
- **Smart Filtering**: Use targeted searches (grep, glob) before reading files
- **Avoid Context Rot**: Start fresh contexts for new task categories

### 3. File-Based Scaffolding

```
.ai/
├── CLAUDE.md         # Agent instructions (read each iteration)
├── tasks.json        # Task tracking with status
├── progress.txt      # Append-only learnings log
└── BEST_PRACTICES.md # This file
```

## Task Definition Best Practices

### Good Task Characteristics

1. **Atomic**: Completable in one context window
2. **Testable**: Clear pass/fail criteria
3. **Isolated**: Minimal dependencies on other tasks
4. **Specific**: No ambiguity in requirements

### Task Template

```json
{
  "id": "unique-id",
  "priority": 1,
  "title": "Short imperative title",
  "description": "Detailed description of what needs to be done",
  "acceptance_criteria": [
    "Specific testable criterion 1",
    "Specific testable criterion 2"
  ],
  "status": "pending",
  "model_hint": "haiku|sonnet|opus"
}
```

## Acceptance Criteria Writing

### The SMART Framework for AI Tasks

- **S**pecific: Exact files, functions, behaviors
- **M**easurable: Tests pass, coverage maintained
- **A**chievable: Within single context window
- **R**elevant: Directly addresses user need
- **T**estable: Clear verification method

### Good Examples

```markdown
- [ ] Function `calculate_battle_outcome()` returns tuple (attacker_losses, defender_losses)
- [ ] Unit test in `test_engine.py` covers edge case where troops = 0
- [ ] Translation key `battle.victory` exists in both en.json and zh.json
- [ ] Running `pytest tests/test_engine.py::test_battle_zero_troops` passes
```

### Bad Examples

```markdown
- [ ] Make battles work better (too vague)
- [ ] Improve performance (not measurable)
- [ ] Add all the translations (not specific)
```

## Loop Execution Patterns

### Continuous Improvement Loop

```
1. Read task → 2. Implement → 3. Test → 4. Commit → 5. Log learnings → Repeat
```

### Recovery from Failures

1. Agent fails a task
2. Failure is logged to `progress.txt`
3. Task remains in `pending` status
4. Next iteration reads progress and avoids same mistake
5. Instructions refined if pattern emerges

## Quality Gates

### Pre-Commit Checklist

```bash
# 1. Run all tests
python -m pytest --no-cov -v

# 2. Check coverage (if changed)
python -m pytest --cov=src --cov-report=term-missing

# 3. Lint check
python -m flake8 src/ --max-line-length=120

# 4. Type check (if using types)
python -m mypy src/ --ignore-missing-imports
```

### Automated Validation

The loop script (`loop.ps1`) enforces:
- Test passage before accepting task completion
- Automatic logging of iterations
- Token usage tracking
- Error recovery

## Anti-Patterns to Avoid

### 1. Context Stuffing
Don't read entire codebase into context. Use targeted searches.

### 2. Mega-Tasks
Break "implement feature X" into 5-10 atomic subtasks.

### 3. Skipping Tests
Never mark task complete without running tests.

### 4. Hardcoded Strings
Always use i18n keys for user-facing text.

### 5. Silent Failures
Log all errors to progress.txt for future iterations.

## References

- [Ralph Methodology](https://ghuntley.com/ralph/)
- [MIT Recursive Language Models](https://arxiv.org/abs/2512.24601)
- [MemGPT: Virtual Context Management](https://arxiv.org/abs/2310.08560)
- [A-Mem: Agentic Memory](https://arxiv.org/abs/2502.12110)
