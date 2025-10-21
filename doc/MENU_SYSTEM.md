# Menu System Documentation

## Overview

The web-based UI now includes a hierarchical menu system that provides an easier, more structured way to interact with the game. Instead of memorizing commands, users can navigate through numbered menus.

## How to Access

1. Start the web server: `python web_server.py`
2. Open the game in your browser
3. Click the **📋 Menu** button or type `menu` in the command line

## Menu Hierarchy

### Main Menu (1-8)

1. **Set Current City** - Select which city to focus on
2. **War** - Military operations
3. **Officer Management** - Handle your officers
4. **Diplomacy** - Foreign relations
5. **Internal Affairs** - Domestic development
6. **Merchant** - Trade operations
7. **Tactics** - Espionage and covert operations
8. **Advice** - Consult your advisors

### 1. Set Current City

Choose from your controlled cities:
- Select by number (1, 2, 3...) or by name
- Shows troops, gold, and food for each city
- Current city is displayed in the game info bar

### 2. War Menu (1-7)

1. Move Troops - Transfer forces between your cities
2. Transfer Troops - Reassign garrison
3. Wage War - Launch attacks on enemies
4. Recruit Soldiers - Raise new troops
5. Training - Improve troop quality
6. Make Weapons - Produce armaments
7. Surveillance - Scout enemy positions

### 3. Officer Management (1-3)

1. Search for Officers - Look for new talent
2. Recruit Officer - Hire available officers
3. Reward Officer - Grant rewards to increase loyalty

### 4. Diplomacy (1-6)

1. Form Alliance - Create diplomatic ties
2. Attack Common Enemy - Coordinate with allies
3. Send Gift - Improve relations through gifts
4. Persuade to Capitulate - Convince enemies to surrender
5. Break Alliance - End diplomatic agreements
6. Rescue Prisoner of War - Free captured officers

### 5. Internal Affairs (1-5)

1. Agriculture - Develop farming (increases food production)
2. Flood Management - Prevent disasters
3. Commerce - Boost trade (increases gold income)
4. Technology - Advance research (military bonuses)
5. Build School - Construct educational facilities:
   - Military Academy (for Officers)
   - Scholar Academy (for Politics)
   - Engineering School (for War Technology)

### 6. Merchant (1-3)

1. Buy/Sell Food - Trade grain supplies
2. Buy/Sell Weapons - Trade armaments
3. Buy/Sell Horses - Trade cavalry mounts

### 7. Tactics (1-6)

1. Espionage - Gather intelligence (costs 50 gold)
2. Spread Rumors/Defamation - Damage enemy reputation
3. Set Fire - Sabotage enemy facilities
4. Detect Double Agent - Find enemy spies
5. Send Undercover Agent - Plant your own spies
6. Spread False Information - Deceive enemies

### 8. Advisor's Counsel (1-8)

Get strategic advice on:
1. War Strategy
2. Officer Management
3. Diplomacy
4. Internal Affairs
5. Trade & Commerce
6. Tactics & Espionage
7. Current Situation
8. Long-term Strategy

## Navigation

- **Numbers (1-8)**: Select menu options
- **0 or "back"**: Return to main menu
- **"menu"**: Return to main menu from anywhere
- **Traditional commands**: Still work (status, officers, turn, etc.)

## Language Support

The menu system supports both English and Chinese:
- Type `lang en` for English
- Type `lang zh` for Chinese (中文)
- Click the language buttons in the quick commands bar

## Current Implementation Status

### ✅ Fully Implemented
- Menu navigation system
- Set Current City
- Language switching
- Menu state persistence

### 🚧 Partially Implemented
- War operations (some commands work: move, attack, spy)
- Officer Management (reward works)
- Internal Affairs (assign officers to tasks)

### 📋 Planned Features
- Advanced war tactics
- Diplomatic negotiations
- Merchant trading system
- School building system
- Advisor AI recommendations

## Design Notes

### Grammar Corrections Made

**English:**
- "Dipolmacy" → "Diplomacy"
- "aliance" → "Form Alliance"
- "persaude" → "Persuade"
- "distroy" → "Break Alliance"
- "agrictuluture" → "Agriculture"
- "soliders" → "Soldiers"

**Chinese:**
- Used proper traditional characters
- Applied appropriate terminology for historical context
- Used period-appropriate military and political terms

### Better Word Choices

- "Set Current City" instead of "Choose City" (clearer action)
- "Officer Management" instead of "Officers" (more descriptive)
- "Internal Affairs" instead of "Domestic" (historical accuracy)
- "Wage War" instead of just "War" (specific action)
- "Espionage" instead of just "Spy" (broader category)
- "Advisor's Counsel" instead of just "Advice" (more formal)
- "Persuade to Capitulate" instead of "Force Surrender" (diplomatic)
- "Rescue Prisoner of War" instead of "Free POW" (formal military term)

## Technical Implementation

- Menu state stored per session in `session_states` dictionary
- Supports both menu navigation and traditional command input
- Backward compatible with existing commands
- Localization handled through i18n system
- State persists across commands within a session

## Usage Tips

1. **New Players**: Use the menu system for guided gameplay
2. **Experienced Players**: Mix menu and traditional commands as needed
3. **Set Current City**: Do this first to focus your operations
4. **Language**: Switch language at any time with `lang` command
5. **Help**: Type `help` for traditional command reference

## Future Enhancements

- Context-sensitive menus based on current city
- Officer recommendations for tasks
- AI advisor implementation
- Resource cost previews
- Confirmation prompts for major decisions
- Multi-target operations (select multiple cities/officers)
