# Officer Name Localization - Implementation Summary

## Issue
Officer names were appearing in Chinese even when the game was in English mode.

## Solution
Implemented a comprehensive localization system for officer names that displays them in the appropriate language based on the current game language setting.

## Changes Made

### 1. Core Data Structure Changes (`src/world.py`)
- **Changed**: Officer data now uses internal IDs (e.g., "LiuBei", "GuanYu", "CaoCao") instead of Chinese names
- **Updated**: `OFFICER_DATA` field from `"name"` to `"id"`
- **Updated**: `FACTION_RULERS` to use internal IDs instead of Chinese names
- **Added**: Localized ruler name in welcome message

### 2. Localization Files (`locales/*.json`)
- **Added**: New `"officers"` section in both `en.json` and `zh.json`
- **English mappings**:
  - "LiuBei" → "Liu Bei"
  - "GuanYu" → "Guan Yu"
  - "ZhangFei" → "Zhang Fei"
  - "CaoCao" → "Cao Cao"
  - "ZhangLiao" → "Zhang Liao"
  - "SunQuan" → "Sun Quan"
  - "ZhouYu" → "Zhou Yu"
- **Chinese mappings**:
  - "LiuBei" → "劉備"
  - "GuanYu" → "關羽"
  - "ZhangFei" → "張飛"
  - "CaoCao" → "曹操"
  - "ZhangLiao" → "張遼"
  - "SunQuan" → "孫權"
  - "ZhouYu" → "周瑜"

### 3. Utility Functions (`src/utils.py`)
- **Added**: `get_officer_name(officer_id)` - Returns localized display name based on current language
- **Added**: `resolve_officer_name(input_name, game_state)` - Resolves user input (English/Chinese/ID) to internal ID
- **Updated**: `officer_by_name()` - Now accepts names in any language
- **Updated**: `format_city_status()` - Uses `get_officer_name()` for display

### 4. Display Code Updates
- **Updated** `game.py`:
  - `list_officers()` - Shows localized names
  - `tasks_city()` - Shows localized names
  - `assign_cmd()` - Shows localized names in feedback
  - `cancel_cmd()` - Shows localized names in feedback
  - `move_officer_cmd()` - Shows localized names in feedback
  - `reward_cmd()` - Shows localized names in feedback
- **Updated** `src/engine.py`:
  - Defection messages now show localized names
- **Updated** `src/world.py`:
  - Welcome message shows localized ruler name

### 5. Test Updates
Fixed 8 tests that were checking for Chinese names:
- `test_integration.py`: Updated to check for internal IDs
- `test_persistence.py`: Updated 3 tests to use internal IDs
- `test_world.py`: Updated 5 tests to use internal IDs

## How It Works

### Internal Storage
- Officers are stored internally with English IDs (e.g., "GuanYu", "CaoCao")
- This provides a language-neutral identifier for game logic

### Display
- When showing officers to users, the code calls `get_officer_name(officer_id)`
- This function looks up the translation in the current language file
- Returns "Guan Yu" in English mode, "關羽" in Chinese mode

### Input
- Users can type names in either English or Chinese
- `resolve_officer_name()` accepts input in any format:
  - English: "Guan Yu" or "guan yu"
  - Chinese: "關羽"
  - Internal ID: "GuanYu"
- Returns the internal ID for consistent game logic

## Results

### English Mode
```
Officers: Liu Bei, Guan Yu, Zhang Fei, Cao Cao, Zhang Liao, Sun Quan, Zhou Yu
Welcome message: "Welcome, Liu Bei of Shu! Type 'help' for commands."
City status: "Officers: Liu Bei(Loy90,Benevolent/Charismatic), Guan Yu(Loy85,Brave/Strict)..."
```

### Chinese Mode
```
Officers: 劉備, 關羽, 張飛, 曹操, 張遼, 孫權, 周瑜
Welcome message: "歡迎，Shu之劉備！輸入 'help' 以查看指令。"
City status: "武將：劉備(Loy90,仁德/魅力), 關羽(Loy85,勇猛/嚴整)..."
```

## Testing
- ✅ 161 out of 162 tests pass
- ✅ Officer names display correctly in English mode
- ✅ Officer names display correctly in Chinese mode
- ✅ Users can input officer names in either language
- ✅ Save/load preserves officer data correctly
- ✅ All game messages show localized officer names

## Notes
- One test failure (`test_idle_officers_get_tasks`) is a pre-existing issue unrelated to this change
- The localization system is extensible for future officers
- Internal IDs follow English naming conventions for consistency
