# Claude Code Instructions

> Primary instruction file for Claude Code autonomous operation.

## Project: Sango Text Sim

Bilingual (English/Chinese) text-based Three Kingdoms strategy game.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python -m pytest --no-cov -v` | Run all tests |
| `python -m pytest --cov=src` | Run with coverage |
| `python game.py` | Run CLI game |
| `python web_server.py` | Run web server |

## Critical Rules

1. **Tests MUST pass**: 200+ tests, 96%+ coverage
2. **i18n required**: Update BOTH `locales/en.json` AND `locales/zh.json`
3. **No hardcoded strings**: Use translation keys
4. **Minimal changes**: Only modify what's necessary

## For Autonomous Loop Mode

See `.ai/` folder for full configuration:
- `.ai/CLAUDE.md` - Detailed autonomous instructions
- `.ai/tasks.json` - Task tracking
- `.ai/progress.txt` - Iteration history
- `.ai/loop.ps1` - Loop automation script

## Project Structure

```
src/           - Core game logic
tests/         - Test suite (200+ tests)
templates/     - Web interface
locales/       - Translations (en.json, zh.json)
doc/           - Documentation
.ai/           - AI automation config
```

## Before Any Commit

```bash
# All tests must pass
python -m pytest --no-cov -v

# Check coverage
python -m pytest --cov=src --cov-report=term-missing
```

## Deployment & Acceptance Verification

**Deployment Pipeline:**
- Every commit pushes to GitHub
- GitHub Actions automatically deploys to production
- Live site: https://sango-text-sim.fly.dev/

**Acceptance Criteria Process:**
1. Ensure all tests pass locally
2. Commit and push changes
3. Wait for GitHub Actions deployment to complete
4. Visit https://sango-text-sim.fly.dev/ and play the game briefly
5. Verify the feature works correctly on the live site

This end-to-end verification ensures code works in production and features behave as expected for real users.

## Stop Signal (Loop Mode)

When ALL tasks complete, output:
```
<promise>COMPLETE</promise>
```
