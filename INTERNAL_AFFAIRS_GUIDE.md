# Internal Affairs Guide - Sustaining Your Empire

## The Problem

As you've discovered, resources deplete quickly in the game:
- **Troops consume food** every month
- **Without development**, your cities can't sustain a large army
- **Soldiers start dying** when food runs out after about a year

## The Solution: Internal Affairs Menu

The Internal Affairs menu allows you to develop your cities to sustain your empire long-term.

## How to Access

### Via Web UI:
1. Start the game: `python web_server.py`
2. Choose your faction (Wei/Shu/Wu)
3. Click "📋 Menu" or type `menu`
4. Select option `1` to **Set Current City**
5. Choose a city (e.g., `1` for Chengdu)
6. Type `menu` to return to main menu
7. Select option `5` for **Internal Affairs**

### Quick Path:
```
> menu
> 1          (Set Current City)
> 1          (Select Chengdu)
> menu
> 5          (Internal Affairs)
```

## Internal Affairs Options

### 1. Agriculture (農業)
- **Purpose**: Increases food production
- **Effect**: Raises the city's Agriculture stat
- **Benefits**:
  - Higher monthly food income
  - 5x multiplier in July (harvest season)
  - Prevents starvation and troop losses
- **When to use**: If food is running low or you want to sustain a large army

### 2. Flood Management (治水)
- **Purpose**: Protects agricultural land from flooding
- **Effect**: Also improves Agriculture stat
- **Benefits**: Same as Agriculture
- **Historical note**: Flood control was crucial in ancient China

### 3. Commerce (商業)
- **Purpose**: Increases gold production
- **Effect**: Raises the city's Commerce stat
- **Benefits**:
  - Higher monthly gold income
  - 5x multiplier in January (tax season)
  - Funds for recruiting, rewards, and diplomacy
- **When to use**: If you need gold for expansion or officer rewards

### 4. Technology (科技)
- **Purpose**: Advances military technology
- **Effect**: Raises the city's Technology stat
- **Benefits**:
  - Combat bonuses in battles
  - Better attack and defense multipliers
  - Long-term military advantage
- **When to use**: Preparing for war or defending against enemies

### 5. Build School (興建學府)
- **Status**: Coming soon!
- **Planned features**:
  - Military Academy: Train better officers
  - Scholar Academy: Improve political abilities
  - Engineering School: Advance war technology

## Strategy Guide

### Early Game (Year 1)
**Priority: Survival**
1. **Set current city** to your capital
2. **Develop Agriculture** 2-3 times
3. **Develop Commerce** 1-2 times
4. Ensure you have enough food for your troops

### Mid Game (Years 2-3)
**Priority: Expansion**
1. **Balance all three**: Agriculture, Commerce, Technology
2. Develop **Technology** before major battles
3. Keep **Agriculture** ahead of troop count
4. Use **Commerce** to fund recruitment and diplomacy

### Late Game (Year 4+)
**Priority: Domination**
1. **Max out Technology** for military superiority
2. Maintain **high Agriculture** to support massive armies
3. **High Commerce** for rapid expansion and rewards

## Resource Management Tips

### Preventing Starvation
- **Rule of thumb**: Agriculture should be > (Troops ÷ 10)
- Example: 500 troops needs ~50+ Agriculture
- **Develop agriculture early and often**
- Check food levels regularly with `status CITY`

### Gold Management
- **Commerce generates gold** monthly
- **January provides 5x multiplier** (tax season)
- **Save gold for**: recruiting soldiers, rewarding officers, diplomacy
- **Develop commerce** in cities you plan to use for recruitment

### Technology Timing
- **Develop before major campaigns**
- **Higher tech = better combat performance**
- **Don't neglect** even in peacetime

## How It Works

### Automatic Officer Assignment
The system automatically:
1. Finds available officers in your current city
2. Selects the **best officer** for the task based on:
   - Politics skill (for agriculture/commerce)
   - Intelligence skill (for technology)
   - Beneficial traits (e.g., Benevolent for farming, Merchant for trade)
3. Assigns and executes the task immediately
4. Shows results and city status

### Officer Requirements
- Must be in the **current city**
- Must have **20+ energy**
- Must not be **busy** with another task

### Energy Management
- Officers lose energy when performing tasks
- **Energy recovers** when officers are idle
- If no officers available, you'll see: "No available officers with sufficient energy"
- **Solution**: Wait a turn or assign more officers to the city

## Example Workflow

```
Step 1: Check your resources
> status Chengdu
City Status shows: Gold: 650, Food: 980, Troops: 380
Agriculture: 65, Commerce: 58, Technology: 52

Step 2: Identify the problem
Food is running low (980 food / 380 troops = 2.5 months)
Need to increase food production!

Step 3: Develop Agriculture
> menu
> 1 (Set Current City)
> Chengdu
> menu
> 5 (Internal Affairs)
> 1 (Agriculture)

Result: Officer assigned, Agriculture increased to 70+

Step 4: Continue development
> 1 (Agriculture again)
> 3 (Commerce)
> 4 (Technology)

Step 5: Check progress
> 0 (Back to main menu)
> status Chengdu
Now: Agriculture: 80+, Commerce: 65+, Tech: 60+
```

## Multiple Cities Strategy

### Capital City (e.g., Chengdu)
- **Focus**: Balanced development
- Develop all three stats evenly
- Main production base

### Border Cities (e.g., Hanzhong)
- **Focus**: Military (Tech + Food for troops)
- High Agriculture to feed garrison
- High Technology for defense

### Economic Cities
- **Focus**: Commerce
- Maximize gold production
- Fund your empire's expansion

## Troubleshooting

### "No available officers"
**Problem**: All officers in the city are tired or busy
**Solutions**:
- End turn to restore officer energy
- Move officers from other cities
- Cancel other tasks with traditional commands

### "Please set a current city first"
**Problem**: No current city selected
**Solution**: Main Menu > Option 1 > Select a city

### "City no longer under your control"
**Problem**: You lost the city to an enemy
**Solution**: Recapture the city or select a different one

### Stats aren't increasing much
**Problem**: Officers have low Politics/Intelligence
**Solutions**:
- Use officers with higher stats
- Officers with beneficial traits (Benevolent, Merchant, Scholar)
- Develop multiple times over several turns

## Testing Your Setup

Run the manual test to see the system in action:
```bash
python test_internal_affairs_manual.py
```

This interactive demo will walk you through:
- Setting current city
- Developing agriculture, commerce, and technology
- Viewing results in both English and Chinese
- Understanding the menu flow

## Long-term Sustainability

### Sustainable Army Size Formula
```
Maximum Sustainable Troops = (Agriculture × 8) + (Monthly Food Income)
```

### Example Calculation
- Agriculture: 80
- Monthly base food: ~50
- July harvest bonus: Agriculture × 5 = 400
- **Sustainable troops**: ~650-700 troops long-term

### Growth Strategy
1. **Year 1**: Build Agriculture to 70-80
2. **Year 2**: Build Commerce to 70+
3. **Year 3**: Build Technology to 60+
4. **Year 4+**: Maintain and expand

## Advanced Tips

1. **Develop before conquering**: Build strong economic base first
2. **Use officers wisely**: High-stat officers = bigger improvements
3. **Balance is key**: Don't neglect any stat
4. **Plan for seasons**: Boost Commerce before January, Agriculture before July
5. **Multiple cities**: Specialize each city for different purposes

## Test Coverage

The Internal Affairs system is backed by **23 comprehensive tests** covering:
- ✅ Menu navigation
- ✅ Agriculture, Commerce, Technology development
- ✅ Officer selection and assignment
- ✅ Energy management
- ✅ Resource display
- ✅ Chinese/English language support
- ✅ Integration with game mechanics
- ✅ Error handling and validation

Run tests with:
```bash
python -m pytest tests/test_menu_internal_affairs.py -v
```

## Summary

**Before Internal Affairs:**
- Resources deplete → Troops starve → Game Over

**With Internal Affairs:**
- Develop cities → Sustainable production → Long-term empire → Victory!

**Key Takeaway**: Spend your first few turns developing your cities' infrastructure. This investment will pay off massively as the game progresses!
