# Acceptance Criteria Template

> Use this template to write proper acceptance criteria for AI-assisted development tasks.

## Template Structure

```markdown
## Task: [Short Imperative Title]

### Context
Brief background on why this task is needed.

### Scope
- What IS included in this task
- What is NOT included (explicitly state boundaries)

### Acceptance Criteria

#### Functional Requirements
- [ ] [Specific behavior 1 with exact input/output]
- [ ] [Specific behavior 2 with exact input/output]

#### Code Quality
- [ ] All existing tests pass (200+)
- [ ] New tests written for new functionality
- [ ] Code coverage maintained at 96%+
- [ ] No lint errors

#### Internationalization (if UI changes)
- [ ] Translation key added to `locales/en.json`
- [ ] Translation key added to `locales/zh.json`
- [ ] Both translations tested in browser

#### Verification Commands
```bash
# Command to verify this specific task
pytest tests/test_xxx.py::test_specific -v

# Full test suite
python -m pytest --no-cov -v
```

### Files to Modify
- `src/file1.py` - [What changes]
- `tests/test_file1.py` - [What tests to add]

### Model Hint
Recommended: haiku | sonnet | opus
```

---

## Example: Complete Task Definition

```markdown
## Task: Add Energy Validation for Officer Assignments

### Context
Officers can currently be assigned tasks even when their energy is 0,
which should not be allowed.

### Scope
- IS included: Validation check in assignment function
- NOT included: Energy regeneration mechanics (separate task)

### Acceptance Criteria

#### Functional Requirements
- [ ] `assign_officer()` in `src/engine.py` raises `ValueError` when officer energy < 10
- [ ] Error message includes officer name and current energy level
- [ ] Assignment proceeds normally when energy >= 10

#### Code Quality
- [ ] All 201 tests pass
- [ ] New test `test_assign_officer_low_energy` added
- [ ] Code coverage maintained at 96%+

#### Internationalization
- [ ] Key `error.insufficient_energy` added to `locales/en.json`
- [ ] Key `error.insufficient_energy` added to `locales/zh.json`

#### Verification Commands
```bash
pytest tests/test_engine.py::test_assign_officer_low_energy -v
python -m pytest --no-cov -v
```

### Files to Modify
- `src/engine.py` - Add energy check in `assign_officer()`
- `tests/test_engine.py` - Add test for low energy case
- `locales/en.json` - Add error message
- `locales/zh.json` - Add error message (Chinese)

### Model Hint
Recommended: opus (straightforward logic change with tests)
```

---

## Criteria Quality Checklist

Before submitting acceptance criteria, verify:

### Clarity
- [ ] Can someone unfamiliar with the codebase understand the task?
- [ ] Are all technical terms defined or obvious?
- [ ] Is there exactly ONE interpretation of each criterion?

### Completeness
- [ ] Are all affected files listed?
- [ ] Are i18n requirements included (if applicable)?
- [ ] Is the verification method specified?

### Testability
- [ ] Can each criterion be verified with a command?
- [ ] Are expected values/outputs specified?
- [ ] Is the pass/fail condition unambiguous?

### Sizing
- [ ] Can this be completed in ONE context window?
- [ ] Are there fewer than 5 files to modify?
- [ ] Is the scope clearly bounded?

---

## Anti-Patterns in Acceptance Criteria

### Too Vague
```
- [ ] Make the battle system better
```
**Fix:** Specify exact metric or behavior change.

### Not Testable
```
- [ ] Code should be clean
```
**Fix:** Use measurable criteria like "no lint errors" or "passes flake8".

### Missing Scope Boundaries
```
- [ ] Add user authentication
```
**Fix:** Break into subtasks: "Add login form", "Add session management", etc.

### Assumed Knowledge
```
- [ ] Update the usual files
```
**Fix:** Explicitly list every file to be modified.

---

## Quick Reference: Common Criteria

### For Bug Fixes
```markdown
- [ ] Regression test added that fails before fix
- [ ] Test passes after fix
- [ ] No other tests broken
```

### For New Features
```markdown
- [ ] Feature implemented as specified
- [ ] Unit tests with >90% coverage of new code
- [ ] Integration test for happy path
- [ ] Error handling for edge cases
```

### For Refactoring
```markdown
- [ ] All existing tests still pass
- [ ] No functional changes (same input/output)
- [ ] Code follows project style guide
```

### For i18n Tasks
```markdown
- [ ] Key added to en.json
- [ ] Key added to zh.json
- [ ] Key used in code (no hardcoded strings)
- [ ] Tested in both language modes
```
