# Documentation Index

## 📚 Development Documentation

This project has comprehensive documentation to guide development and maintain code quality.

### Quick Start
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** 🚀
  - Essential commands and checklists
  - Common workflows
  - Pre-commit checklist
  - Emergency fixes

### Complete Guidelines  
- **[COPILOT_INSTRUCTIONS.md](COPILOT_INSTRUCTIONS.md)** 📖
  - Full development rules and patterns
  - Architecture guidelines
  - Testing requirements
  - Code quality standards
  - Internationalization (i18n) rules
  - Commit guidelines

### GitHub Copilot Configuration
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** 🤖
  - Critical rules summary
  - Quick command reference
  - Integration with GitHub Copilot

---

## 🎯 Critical Rules

### Testing (Mandatory)
```bash
python -m pytest --no-cov -v
```
- ✅ All 187 tests must pass
- ✅ Maintain 96%+ code coverage
- ✅ Write tests for every change

### Internationalization
- ✅ Update both `locales/en.json` AND `locales/zh.json`
- ✅ Never hardcode display text
- ✅ Test in both English and Chinese

### Game State
- ✅ Validate `game_started` flag
- ✅ Check faction initialization
- ✅ Menu navigation returns `""`
- ✅ Default to first city when needed

---

## 📋 Documentation Files

| Document | Purpose | Audience |
|----------|---------|----------|
| `COPILOT_INSTRUCTIONS.md` | Complete development guide | Developers & Copilot |
| `QUICK_REFERENCE.md` | Quick commands & checklists | All developers |
| `.github/copilot-instructions.md` | Copilot configuration | GitHub Copilot |
| `ARCHITECTURE.md` | System architecture | Developers |
| `MENU_SYSTEM.md` | Menu implementation | Feature developers |
| `GAME_STATE_FIXES.md` | State management fixes | Bug fixers |
| `README.md` | Project overview | Everyone |

---

## 🔍 Find What You Need

### "How do I...?"

**Run tests?**
→ `QUICK_REFERENCE.md` - Test Commands section

**Add a new feature?**
→ `COPILOT_INSTRUCTIONS.md` - When Adding New Features section

**Fix a bug?**
→ `COPILOT_INSTRUCTIONS.md` - When Fixing Bugs section

**Understand the architecture?**
→ `ARCHITECTURE.md`

**Work with menus?**
→ `MENU_SYSTEM.md`

**Add translations?**
→ `COPILOT_INSTRUCTIONS.md` - Internationalization section

**Debug state issues?**
→ `GAME_STATE_FIXES.md`

---

## 🎓 Learning Path

### New to Project
1. Read `README.md` - Project overview
2. Skim `ARCHITECTURE.md` - Understand structure
3. Review `QUICK_REFERENCE.md` - Learn commands
4. Read `.github/copilot-instructions.md` - Critical rules

### Contributing Code
1. Study `COPILOT_INSTRUCTIONS.md` - Full guidelines
2. Check `QUICK_REFERENCE.md` - Pre-commit checklist
3. Reference specific docs as needed

### Fixing Bugs
1. Check `GAME_STATE_FIXES.md` - Known issues
2. Review `COPILOT_INSTRUCTIONS.md` - Debugging section
3. Use `QUICK_REFERENCE.md` - Emergency fixes

---

## ✅ Before Every Commit

```bash
python -m pytest --no-cov -v
```

**Checklist:** See `QUICK_REFERENCE.md` - Pre-Commit Checklist

---

## 📊 Current Status

| Metric | Value |
|--------|-------|
| Tests | 187/187 ✅ |
| Coverage | 96% ✅ |
| Languages | EN + ZH ✅ |
| Lint Errors | 0 ✅ |

---

## 🆘 Need Help?

1. **Quick answer?** → `QUICK_REFERENCE.md`
2. **Detailed guide?** → `COPILOT_INSTRUCTIONS.md`
3. **Architecture question?** → `ARCHITECTURE.md`
4. **Still stuck?** → Check specific feature docs

---

**Remember:** Documentation exists to help you. Use it! 📚
