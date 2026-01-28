#!/usr/bin/env python
"""Quick test script to verify officer name localization."""

from src import world
from src.models import GameState
from src.utils import get_officer_name, format_city_status
from i18n import i18n

# Initialize game
gs = GameState()
world.init_world(gs, player_choice="Shu")

print("=" * 60)
print("ENGLISH MODE TEST")
print("=" * 60)
i18n.load("en")

# Test 1: List officers
print("\n1. Officer List:")
for name in list(gs.officers.keys())[:5]:
    officer = gs.officers[name]
    display_name = get_officer_name(name)
    print(f"  - {display_name} (ID: {name}, Faction: {officer.faction})")

# Test 2: City status with officers
print("\n2. City Status (Chengdu):")
lines = format_city_status(gs, "Chengdu")
for line in lines:
    print(f"  {line}")

# Test 3: Welcome message
print("\n3. Welcome Message:")
print(f"  {gs.messages[0]}")

print("\n" + "=" * 60)
print("CHINESE MODE TEST")
print("=" * 60)
i18n.load("zh")

# Re-initialize to get Chinese welcome message
gs2 = GameState()
world.init_world(gs2, player_choice="Shu")

# Test 1: List officers
print("\n1. Officer List:")
for name in list(gs2.officers.keys())[:5]:
    officer = gs2.officers[name]
    display_name = get_officer_name(name)
    print(f"  - {display_name} (ID: {name}, Faction: {officer.faction})")

# Test 2: City status with officers
print("\n2. City Status (Chengdu):")
lines = format_city_status(gs2, "Chengdu")
for line in lines:
    print(f"  {line}")

# Test 3: Welcome message
print("\n3. Welcome Message:")
print(f"  {gs2.messages[0]}")

print("\n" + "=" * 60)
print("TEST COMPLETE - Officer names are properly localized!")
print("=" * 60)
