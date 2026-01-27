# Sango Text Sim - Vision Document

## Goal: ROTK11-Inspired Text Strategy Game

Transform the current prototype into an addictive, text-based Three Kingdoms experience that captures ROTK11's magic through ASCII visualization, narrative depth, and strategic complexity.

---

## What Makes ROTK11 Addictive

1. **Visual Map Satisfaction** - Watching territory expand across a beautiful map
2. **Officer Personality** - Characters feel real with portraits, skills, relationships
3. **Strategic Depth** - Multiple layers: internal affairs, diplomacy, military
4. **Dramatic Moments** - Duels, debates, fire attacks, ambushes create stories
5. **Progression Feel** - Building from nothing to a mighty empire
6. **"One More Turn"** - Always something pending, something about to happen

---

## Core Feature Mockups

### 1. Strategic Map (Province-Based, Extensible)

```
═══════════════════════════════════════════════════════════════
                    CHINA - Spring 194 AD
═══════════════════════════════════════════════════════════════

                          ╔═══╗
                          ║幽州║ [Cao Cao] 🏰
                          ╚═╦═╝
                            ║
              ╔═══╗       ╔═╩═╗       ╔═══╗
              ║并州║───────║冀州║───────║青州║ [Cao Cao]
              ╚═══╝       ╚═╦═╝       ╚═══╝
              [Cao]         ║
                    ╔═══╗ ╔═╩═╗ ╔═══╗
                    ║雍州║─║司隸║─║徐州║ [Liu Bei] ⭐
                    ╚═╦═╝ ╚═╦═╝ ╚═══╝
                      ║     ║
              ╔═══╗ ╔═╩═╗ ╔═╩═╗ ╔═══╗
              ║涼州║─║漢中║─║荊州║─║揚州║
              ╚═══╝ ╚═══╝ ╚═╦═╝ ╚═══╝
              [Ma]  [Zhang] ║    [Sun Quan]
                          ╔═╩═╗
                          ║益州║ [Liu Zhang]
                          ╚═══╝

═══════════════════════════════════════════════════════════════
  YOUR FACTION: 蜀 (Shu) │ Cities: 2 │ Officers: 12 │ Gold: 5,400
═══════════════════════════════════════════════════════════════
```

**Key Design Principle**: Map data is loaded from JSON, not hardcoded. This allows easy expansion to 40+ cities.

### 2. City Detail View

```
╔══════════════════════════════════════════════════════════════╗
║                    📍 CHENGDU (成都)                          ║
╠══════════════════════════════════════════════════════════════╣
║  RULER: Liu Bei (劉備)          GOVERNOR: Zhuge Liang (諸葛亮) ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   ┌─────────┐  RESOURCES         DEVELOPMENT                 ║
║   │ ⛫⛫⛫⛫⛫ │  💰 Gold: 12,400   🌾 Agriculture: ████████░░ 82║
║   │ ⛫     ⛫ │  🍚 Food: 89,000   💹 Commerce:    ██████░░░░ 64║
║   │ ⛫  成  ⛫ │  ⚔️ Troops: 35,000 📚 Technology:  █████░░░░░ 54║
║   │ ⛫     ⛫ │                    🏰 Walls:       ████████░░ 78║
║   │ ⛫⛫⛫⛫⛫ │  DEFENSE: 340                                  ║
║   └─────────┘  MORALE: 85                                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  STATIONED OFFICERS (8)                                      ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ ⭐ Zhuge Liang  INT:100 POL:95  [Strategist] Governing │  ║
║  │ ⚔️ Guan Yu      WAR:97  LED:95  [Brave]      Training  │  ║
║  │ ⚔️ Zhang Fei    WAR:98  LED:85  [Fierce]     Resting   │  ║
║  │ 📜 Fa Zheng     INT:95  POL:90  [Schemer]    Research  │  ║
║  └────────────────────────────────────────────────────────┘  ║
╠══════════════════════════════════════════════════════════════╣
║  ADJACENT: Hanzhong (N), Jianning (S), Jiangzhou (E)        ║
╚══════════════════════════════════════════════════════════════╝
```

### 3. Officer Profile with ASCII Portrait

```
╔══════════════════════════════════════════════════════════════╗
║  ╔═══════════╗                                               ║
║  ║  ╭───╮    ║   ZHAO YUN (趙雲) "God of War"                ║
║  ║  │ 雲 │    ║   ─────────────────────────────               ║
║  ║  │ ─── │    ║   Age: 47  │  From: Changshan                ║
║  ║  │ ╱│╲ │    ║                                              ║
║  ║  ╰─┴─╯    ║   "I am the one who charges through ten       ║
║  ╚═══════════╝    thousand enemies!"                         ║
╠══════════════════════════════════════════════════════════════╣
║  STATS                           CONDITION                   ║
║  ─────                           ─────────                   ║
║  ⚔️ Leadership: ██████████ 96    💪 Health: ████████░░ 82    ║
║  📚 Intelligence:████████░░ 74    ⚡ Energy: █████░░░░░ 54    ║
║  🏛️ Politics:   ██████░░░░ 65    ❤️ Loyalty: ██████████ 100  ║
║  👑 Charisma:   ████████░░ 82                                ║
╠══════════════════════════════════════════════════════════════╣
║  TRAITS                                                      ║
║  ───────                                                     ║
║  [勇猛 BRAVE] +15% attack when charging                      ║
║  [忠義 LOYAL] Will never defect, +20 base loyalty            ║
╠══════════════════════════════════════════════════════════════╣
║  SPECIAL ABILITY                                             ║
║  ─────────────────                                           ║
║  🐉 Lone Rider │ Can retreat through enemy encirclement      ║
║     Cost: Passive │ "I'll save Lord Liu's son!"              ║
╠══════════════════════════════════════════════════════════════╣
║  RELATIONSHIPS                                               ║
║  ─────────────                                               ║
║  👑 Liu Bei      [Lord]         ♥️♥️♥️♥️♥️ "My life for you!" ║
║  ⚔️ Guan Yu      [Comrade]      ♥️♥️♥️♥️░ "Respected brother" ║
║  ⚔️ Zhang Fei    [Comrade]      ♥️♥️♥️♥️░ "Fierce ally"       ║
╚══════════════════════════════════════════════════════════════╝
```

### 4. Duel System (Interactive Mini-Game)

```
═══════════════════════════════════════════════════════════════
                ⚔️ DUEL: ZHAO YUN vs XIAHOU DUN ⚔️
═══════════════════════════════════════════════════════════════

        ┌─────────────┐              ┌─────────────┐
        │   ZHAO YUN  │      VS      │ XIAHOU DUN  │
        │ ⚔️ WAR: 96   │              │ ⚔️ WAR: 83   │
        │ ❤️ HP: ████████░░ 78       │ ❤️ HP: ██████░░░░ 54
        └─────────────┘              └─────────────┘

═══════════════════════════════════════════════════════════════
                         ROUND 3
═══════════════════════════════════════════════════════════════

  The two generals circle each other, weapons gleaming...

  ⚔️ Zhao Yun strikes! 15 damage!
  🛡️ Xiahou Dun parries, counters for 8!

  Xiahou Dun lunges with a powerful thrust!

  [ZHAO YUN] Choose your response:

    [1] ⚔️ ATTACK         (Standard damage, may trade blows)
    [2] 🛡️ DEFEND         (Reduce damage, slower counter)
    [3] 🐉 SPECIAL: Dragon Pierces the Clouds
        (High damage, 60% hit rate, costs 30 morale)

═══════════════════════════════════════════════════════════════
```

### 5. Battle Map with Terrain

```
═══════════════════════════════════════════════════════════════
              ⚔️ BATTLE FOR HANZHONG ⚔️
           Attacking: Liu Bei │ Defending: Cao Cao
═══════════════════════════════════════════════════════════════

     TERRAIN: Mountainous │ Weather: Clear │ Turn: 4/20

                    ╔════════════════════╗
                    ║    HANZHONG CITY   ║
                    ║   🏰 Defense: 280   ║
                    ╚════════════════════╝
                           │
            ═══════════════╪═══════════════  〰️ River
           /               │               \
     [Mountain]       [Plains]         [Forest]
         │               │                │
    ┌─────────┐    ┌─────────┐      ┌─────────┐
    │ 夏侯淵   │    │ ⚔️ CLASH │      │ 黃忠    │
    │ ⚔️ 8,000 │ ←→ │ IN       │ ←→   │ ⚔️ 6,000 │
    │ CAV     │    │ PROGRESS │      │ ARC     │
    └─────────┘    └─────────┘      └─────────┘
         │               ↑                │
    ┌─────────┐    ┌─────────┐      ┌─────────┐
    │ 張郃     │    │ 劉備     │      │ 趙雲    │
    │ ⚔️12,000│    │ ⚔️15,000 │      │ ⚔️10,000│
    │ INF     │    │ INF     │      │ CAV     │
    └─────────┘    └─────────┘      └─────────┘

═══════════════════════════════════════════════════════════════
  YOUR FORCES: 31,000 │ ENEMY: 20,000 │ SUPPLIES: 45 days
═══════════════════════════════════════════════════════════════

📜 Huang Zhong reports: "My lord, their formation is tight.
   Shall we support him or continue the siege?"

TACTICAL OPTIONS:
  [1] ⚔️ ALL-OUT ATTACK    [2] 🏰 CONTINUE SIEGE
  [3] 🔥 FIRE ATTACK       [4] 🏃 TACTICAL RETREAT
═══════════════════════════════════════════════════════════════
```

### 6. Council System (Morning Meeting)

```
═══════════════════════════════════════════════════════════════
                🏛️ MORNING COUNCIL - Spring 194
═══════════════════════════════════════════════════════════════

Your advisors have gathered to discuss the state's affairs.

AGENDA ITEMS:

  📊 1. ECONOMIC REPORT (Fa Zheng)
     "Gold reserves are low. I recommend increasing
      commerce development in Chengdu."

  ⚔️ 2. MILITARY ASSESSMENT (Huang Zhong)
     "Cao Cao masses troops at Hanzhong. We should
      reinforce our northern border."

  🤝 3. DIPLOMATIC PROPOSAL (Zhuge Liang)
     "Sun Quan sends an envoy. He proposes alliance
      against Cao Cao."

  📜 4. PERSONNEL MATTER (Liu Ba)
     "Ma Chao wishes to defect to our faction. He
      brings 5,000 cavalry but demands a high position."

═══════════════════════════════════════════════════════════════

  [1] Discuss Economic Report
  [2] Discuss Military Assessment
  [3] Discuss Diplomatic Proposal
  [4] Discuss Personnel Matter
  [5] Adjourn Council (End Turn)

═══════════════════════════════════════════════════════════════
```

### 7. Turn Preview ("One More Turn" Hook)

```
═══════════════════════════════════════════════════════════════
📜 NEXT TURN PREVIEW:
  • Ma Chao arrives at your court seeking refuge
  • Cao Cao's army spotted near Hanzhong (8,000 troops)
  • Your new cavalry unit completes training (+500 cavalry)
  • Guan Yu's loyalty is low (45) - consider rewarding him

[Press ENTER to continue...]
═══════════════════════════════════════════════════════════════
```

---

## Extensibility Architecture

### Data-Driven Design

All game content should be loaded from JSON files, not hardcoded:

```
src/data/
├── maps/
│   ├── china_190.json      # Coalition era (40+ cities)
│   ├── china_200.json      # Guandu era
│   ├── china_208.json      # Red Cliff era
│   └── china_220.json      # Three Kingdoms era
├── officers/
│   ├── legendary.json      # 100+ legendary officers
│   ├── generic.json        # Random officer templates
│   └── abilities.json      # Special abilities
├── events/
│   ├── random.json         # Random events
│   └── historical.json     # Historical events
├── factions.json           # Faction definitions
└── terrain.json            # Terrain types and effects
```

### City/Province Model Extension

```python
@dataclass
class City:
    """Extended city model for full game support."""
    id: str                      # Unique identifier
    name_en: str                 # English name
    name_zh: str                 # Chinese name
    owner: str                   # Controlling faction

    # Geography
    province: str                # Parent province (州)
    terrain: str                 # Mountain/Plains/Coastal/etc
    is_coastal: bool             # Can build navy
    is_capital: bool             # Faction capital
    coordinates: Tuple[int, int] # For map rendering

    # Resources
    gold: int
    food: int
    population: int              # NEW: affects recruitment

    # Military
    troops: Dict[str, int]       # NEW: by unit type
    # {"infantry": 5000, "cavalry": 2000, "archers": 1000, "navy": 0}

    # Development (0-100)
    agriculture: int
    commerce: int
    technology: int
    walls: int
    defense: int
    morale: int

    # Buildings
    buildings: List[str]         # NEW: constructed buildings
```

### Map Data Format

```json
{
  "scenario": "china_208",
  "name": "Red Cliff Era",
  "year": 208,
  "cities": {
    "Chengdu": {
      "name_zh": "成都",
      "province": "Yizhou",
      "coordinates": [25, 70],
      "terrain": "plains",
      "is_coastal": false,
      "adjacent": ["Hanzhong", "Jianning", "Jiangzhou"]
    },
    "Jianye": {
      "name_zh": "建業",
      "province": "Yangzhou",
      "coordinates": [75, 55],
      "terrain": "coastal",
      "is_coastal": true,
      "adjacent": ["Wuchang", "Lujiang", "Kuaiji"]
    }
    // ... 40+ more cities
  },
  "provinces": {
    "Yizhou": {"cities": ["Chengdu", "Hanzhong", "Jianning"]},
    "Yangzhou": {"cities": ["Jianye", "Lujiang", "Kuaiji"]}
    // ... more provinces
  }
}
```

---

## Implementation Phases

### Phase 1: Core Visual Enhancement (Foundation)
**Goal**: Make the game visually engaging

1. ASCII Map Renderer (extensible for any number of cities)
2. City Detail View with progress bars
3. Officer Profile with ASCII portraits
4. Turn Reports with narrative style
5. Seasonal descriptions

### Phase 2: Interactive Combat Systems
**Goal**: Make battles dramatic and engaging

6. Duel Mini-Game (interactive HP, actions)
7. Tactical Battle Map with terrain
8. Weather effects on combat
9. Battle narrative generator
10. Siege mechanics (multi-turn)

### Phase 3: Deep Strategy Layer
**Goal**: Add "one more turn" mechanics

11. Council System (advisor meetings)
12. Unit Types (Infantry/Cavalry/Archers/Navy)
13. Officer Relationships (sworn brothers, rivals)
14. Random Event System
15. Technology Tree
16. Building System

### Phase 4: Narrative & Polish
**Goal**: Make players care

17. Historical Events (Red Cliff, Peach Garden, etc.)
18. More Legendary Officers (100+)
19. Unique Special Abilities
20. Achievement System
21. Turn Preview/Teaser
22. Multiple Scenarios

### Phase 5: Full Game Scale
**Goal**: Match ROTK11 scope

23. 40+ City Map
24. Alliance System
25. Naval Combat
26. Population & Migration
27. Espionage System
28. Supply Lines

---

## Success Metrics

A successful text-based ROTK should achieve:

1. **Session Length**: Players naturally play 30+ minutes
2. **"One More Turn"**: Hard to find natural stopping points
3. **Officer Attachment**: Players remember their officers' names
4. **Strategic Depth**: Multiple valid paths to victory
5. **Memorable Stories**: Players have tales to share

---

## Design Principles

1. **Data-Driven**: All content in JSON, easily extensible
2. **Text as Art**: ASCII art and Unicode create visual appeal
3. **Personality Over Numbers**: Officers are characters, not stats
4. **Choice Matters**: Decisions have visible consequences
5. **Show Progress**: Every turn should feel productive
6. **Surprise & Delight**: Random events keep it fresh
