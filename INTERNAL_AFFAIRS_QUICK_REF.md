# Internal Affairs Menu - Quick Reference

## Problem Solved
**Before**: Soldiers die after a year due to food shortages  
**After**: Develop cities to sustain armies indefinitely!

## Quick Start

### 1. Access Internal Affairs
```
> menu
> 1          # Set Current City
> 1          # Choose your city (e.g., Chengdu)
> menu
> 5          # Internal Affairs
```

### 2. Develop Your City
```
> 1          # Agriculture (increases food production)
> 1          # Agriculture again
> 3          # Commerce (increases gold income)
> 4          # Technology (improves combat)
```

### 3. Check Results
```
> 0          # Back to main
> status Chengdu
```

## What Each Option Does

| Option | Name | Increases | Use When |
|--------|------|-----------|----------|
| 1 | Agriculture | Food production | Army is starving |
| 2 | Flood Management | Food production | Same as agriculture |
| 3 | Commerce | Gold income | Need funds |
| 4 | Technology | Combat power | Preparing for war |
| 5 | Build School | (Coming soon) | N/A |

## Recommended Development Path

### Turn 1-3: Build Food Production
```
> menu > 5 > 1 (Agriculture x3)
Result: Sustainable food for army
```

### Turn 4-6: Build Economy
```
> menu > 5 > 3 (Commerce x2-3)
Result: Gold for expansion
```

### Turn 7+: Build Military Tech
```
> menu > 5 > 4 (Technology x2-3)
Result: Win battles more easily
```

## Sustainability Formula

**Minimum Agriculture Needed**:
```
Agriculture ≥ (Number of Troops ÷ 10)

Examples:
- 300 troops → Need 30+ Agriculture
- 500 troops → Need 50+ Agriculture
- 1000 troops → Need 100 Agriculture (max)
```

## Tips

1. **Develop early**: First 3-5 turns should be development
2. **Focus on food first**: Prevents troop losses
3. **Balance all three**: Don't neglect any stat
4. **Use best cities**: Develop your capital and major cities
5. **Check officer energy**: If no officers available, end turn

## Testing

All functionality is fully tested:
```bash
# Run tests
python -m pytest tests/test_menu_internal_affairs.py -v

# All tests (187 total)
python -m pytest tests/ -q
```

## Documentation

- **Full Guide**: See `INTERNAL_AFFAIRS_GUIDE.md`
- **Implementation**: See `INTERNAL_AFFAIRS_IMPLEMENTATION.md`
- **Menu System**: See `MENU_SYSTEM.md`

## Languages Supported

- English: `lang en`
- Chinese: `lang zh`

Both work identically in the menu system!

---

**Ready to play?** Start the server and try it out:
```bash
python web_server.py
# Open http://localhost:8080
# Choose faction → Click Menu → Internal Affairs
```
