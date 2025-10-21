# Menu System Quick Start Guide

## What's New?

A new hierarchical menu system has been added to the web UI, making the game much easier to play without memorizing commands!

## How to Use

### Starting the Game

1. Start the web server:
   ```bash
   python web_server.py
   ```

2. Open your browser to: `http://localhost:8080`

3. Choose your faction: Click "Choose Shu" (or Wei/Wu)

4. Click the **📋 Menu** button or type `menu`

### Main Menu Options

Type a number (1-8) to select:

1. **Set Current City** - Choose which city to focus on
2. **War** - Military operations
3. **Officer Management** - Handle your officers  
4. **Diplomacy** - Foreign relations
5. **Internal Affairs** - Domestic development
6. **Merchant** - Trade operations
7. **Tactics** - Espionage and covert operations
8. **Advice** - Consult your advisors

### Navigation

- **Type 1-8**: Select menu option
- **Type 0 or "back"**: Return to main menu
- **Type "menu"**: Show main menu anytime
- **Traditional commands still work!** (status, officers, turn, etc.)

### Language Support

Switch between English and Chinese:
- Click "English" or "中文" buttons
- Or type: `lang en` or `lang zh`

## Example Session

```
> choose Shu
You are now playing as Shu!
Type 'menu' to use the menu system.

> menu
=== Main Menu ===

1. Set Current City
2. War
3. Officer Management
...

> 1
=== Select Current City ===

1. Chengdu (Troops: 380, Gold: 650, Food: 980)
2. Hanzhong (Troops: 320, Gold: 560, Food: 820)

Choose a city (number or name):

> 1
Current city set to: Chengdu

> menu
=== Main Menu ===

Current City: Chengdu

1. Set Current City
2. War
...

> 2
=== War Menu ===

1. Move Troops
2. Transfer Troops
...

> 0
[Back to Main Menu]
```

## Features

✅ Easy navigation with numbered menus  
✅ Bilingual support (English/Chinese)  
✅ Shows current city in game info  
✅ Grammar-corrected text  
✅ Better word choices for clarity  
✅ Backward compatible with all existing commands  

## Tips

1. **Set your current city first** - This helps contextualize your actions
2. **Mix menu and commands** - Use whichever is more convenient
3. **Try both languages** - See historically-accurate Chinese terminology!
4. **Press 0 anytime** - Quick way to return to main menu

## Full Documentation

See `MENU_SYSTEM.md` for complete documentation of all menu options and features.
