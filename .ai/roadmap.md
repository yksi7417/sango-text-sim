# Sango Text Sim: ROTK11-Inspired Enhancement Roadmap

## 🎯 Vision: Capturing ROTK11's Magic in Text

ROTK11's addictiveness comes from several key elements that need text-based equivalents:

### What Makes ROTK11 Addictive
1. **Visual Map Satisfaction** - Watching your territory expand across a beautiful 2.5D map
2. **General Personality** - Officers feel like real characters with portraits, skills, relationships
3. **Strategic Depth** - Multiple layers of decisions (internal affairs, diplomacy, military)
4. **Dramatic Moments** - Duels, debates, fire attacks, ambushes create memorable stories
5. **Progression Feel** - Building up from nothing to a mighty empire

---

## 🗺️ Phase 1: ASCII Map System (The "2.5D" Feel)

### 1.1 Strategic Map Display

Replace text-only status with a visual ASCII map that shows territories at a glance:

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

### 1.2 City Detail View

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

### 1.3 Battle Map View

```
═══════════════════════════════════════════════════════════════
              ⚔️ BATTLE FOR HANZHONG ⚔️
           Attacking: Liu Bei │ Defending: Cao Cao
═══════════════════════════════════════════════════════════════

     TERRAIN: Mountainous │ Weather: Clear │ Turn: 3/20

                    ╔════════════════════╗
                    ║    HANZHONG CITY   ║
                    ║   🏰 Defense: 280   ║
                    ╚════════════════════╝
                           │
            ═══════════════╪═══════════════  (River)
           /               │               \
     [Mountain]      [Plains]         [Forest]
         │               │                │
    ┌─────────┐    ┌─────────┐      ┌─────────┐
    │ 夏侯淵   │    │ ⚔️ CLASH │      │ 黃忠    │
    │ ⚔️ 8,000 │ ←→ │ IN       │ ←→   │ ⚔️ 6,000 │
    │ CAV     │    │ PROGRESS │      │ ARC     │
    └─────────┘    └─────────┘      └─────────┘
         │               ↑                │
         │          [Siege Ramp]          │
         │               │                │
    ┌─────────┐    ┌─────────┐      ┌─────────┐
    │ 張郃     │    │ 劉備     │      │ 趙雲    │
    │ ⚔️12,000│    │ ⚔️15,000 │      │ ⚔️10,000│
    │ INF     │    │ INF     │      │ CAV     │
    └─────────┘    └─────────┘      └─────────┘

═══════════════════════════════════════════════════════════════
  YOUR FORCES: 31,000 │ ENEMY: 20,000 │ SUPPLIES: 45 days
═══════════════════════════════════════════════════════════════
```

---

## 🎭 Phase 2: Character Depth & Relationships

### 2.1 Enhanced Officer Profiles

```
╔══════════════════════════════════════════════════════════════╗
║  ╔═══════════╗                                               ║
║  ║           ║   GUAN YU (關羽) "God of War"                  ║
║  ║  [ASCII   ║   ─────────────────────────────               ║
║  ║  PORTRAIT ║   Age: 47  │  From: Hedong                    ║
║  ║   HERE]   ║                                               ║
║  ║           ║   "I would rather die than surrender!"        ║
║  ╚═══════════╝                                               ║
╠══════════════════════════════════════════════════════════════╣
║  ABILITIES                        STATS                      ║
║  ────────────                     ─────                      ║
║  ⚔️ Leadership: ██████████ 97     💪 Health: ████████░░ 82   ║
║  🗡️ Combat:     ██████████ 99     ⚡ Energy: █████░░░░░ 54   ║
║  📚 Intelligence:████████░░ 78    ❤️ Loyalty: ██████████ 100 ║
║  🏛️ Politics:   ██████░░░░ 62                                ║
║  👑 Charisma:   █████████░ 93                                ║
╠══════════════════════════════════════════════════════════════╣
║  TRAITS                                                      ║
║  ───────                                                     ║
║  [勇猛 BRAVE] +15% attack when charging                      ║
║  [傲氣 PROUD] Won't serve under former subordinates          ║
║  [義絕 RIGHTEOUS] +20 loyalty to oath brothers, -30 to rest  ║
╠══════════════════════════════════════════════════════════════╣
║  SPECIAL ABILITIES                                           ║
║  ─────────────────                                           ║
║  🐉 Green Dragon Slash │ Devastating single-target attack    ║
║     Cost: 50 Morale │ Cooldown: 3 turns                      ║
║                                                              ║
║  ⚡ Lone Rider │ Can retreat through enemy lines             ║
║     Passive ability                                          ║
╠══════════════════════════════════════════════════════════════╣
║  RELATIONSHIPS                                               ║
║  ─────────────                                               ║
║  👑 Liu Bei      [Sworn Brother] ♥️♥️♥️♥️♥️ "For my brother!" ║
║  ⚔️ Zhang Fei    [Sworn Brother] ♥️♥️♥️♥️♥️ "Third brother!" ║
║  📜 Zhuge Liang  [Colleague]     ♥️♥️♥️░░   "Talented..."    ║
║  ⚔️ Zhang Liao   [Rival]         💢💢💢░░   "Worthy foe!"    ║
║  👿 Lu Meng      [Enemy]         💀💀💀💀💀 "Treacherous!"   ║
╚══════════════════════════════════════════════════════════════╝
```

### 2.2 Relationship Events

Random events based on officer relationships:

```
═══════════════════════════════════════════════════════════════
                    📜 EVENT: OATH OF THE PEACH GARDEN
═══════════════════════════════════════════════════════════════

Guan Yu and Zhang Fei approach you with a request...

    "My lord, we three have shared hardships since the Yellow
     Turban Rebellion. Zhang Fei and I wish to swear an oath
     of brotherhood with you in the peach garden."

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   "Though we were not born on the same day, in the     │
    │    same month, in the same year, we hope to die so."   │
    │                                                         │
    └─────────────────────────────────────────────────────────┘

EFFECTS IF ACCEPTED:
  • Liu Bei, Guan Yu, Zhang Fei become [Sworn Brothers]
  • +100 Loyalty between all three (permanent)
  • +20 Morale to all troops when fighting together
  • Special combo abilities unlocked

═══════════════════════════════════════════════════════════════
         [1] Accept the Oath    [2] Decline politely
═══════════════════════════════════════════════════════════════
```

---

## ⚔️ Phase 3: Dynamic Battle System

### 3.1 Tactical Conversation-Based Combat

Instead of just "march and roll dice," create narrative battles:

```
═══════════════════════════════════════════════════════════════
                    ⚔️ BATTLE PHASE: TURN 4
═══════════════════════════════════════════════════════════════

Current Situation:
  Your vanguard (Zhao Yun, 5,000 cavalry) has engaged
  Xiahou Dun's infantry (8,000) on the plains.

  The enemy holds the high ground. Your cavalry advantage
  is reduced.

  TERRAIN: Plains with Hill     │ WEATHER: Light Rain
  YOUR MORALE: 85               │ ENEMY MORALE: 78

═══════════════════════════════════════════════════════════════
  Zhao Yun reports: "My lord, their formation is tight.
  A frontal assault will be costly. What are your orders?"
═══════════════════════════════════════════════════════════════

TACTICAL OPTIONS:

  [1] CHARGE! 🐎
      "Break their lines with cavalry momentum!"
      Risk: HIGH │ Reward: HIGH │ Casualties: ~30%

  [2] FEIGNED RETREAT 🏃
      "Lure them from the hill, then strike!"
      Requires: INT 70+ │ Risk: MEDIUM │ Success: 65%

  [3] WAIT FOR REINFORCEMENTS ⏳
      "Zhang Fei's unit is 2 turns away"
      Risk: LOW │ Enemy may fortify

  [4] FIRE ATTACK 🔥
      "The grass is dry despite the rain..."
      Requires: Strategist │ Risk: VERY HIGH │ Reward: DEVASTATING
      ⚠️ Weather penalty: -20% success chance

  [5] CHALLENGE TO DUEL ⚔️
      "I, Zhao Yun, challenge Xiahou Dun to single combat!"
      Risk: Personal │ Reward: Enemy morale collapse if won

═══════════════════════════════════════════════════════════════
  > What is your command?
═══════════════════════════════════════════════════════════════
```

### 3.2 Duel System

```
═══════════════════════════════════════════════════════════════
                    ⚔️ DUEL: ZHAO YUN vs XIAHOU DUN
═══════════════════════════════════════════════════════════════

        ┌─────────────┐              ┌─────────────┐
        │   ZHAO YUN  │      VS      │ XIAHOU DUN  │
        │ ⚔️ WAR: 96   │              │ ⚔️ WAR: 83   │
        │ ❤️ HP: 100   │              │ ❤️ HP: 100   │
        └─────────────┘              └─────────────┘

═══════════════════════════════════════════════════════════════
                         ROUND 1
═══════════════════════════════════════════════════════════════

  The two generals circle each other, weapons gleaming...

  Xiahou Dun strikes first! A powerful horizontal slash!

  [ZHAO YUN] Choose your response:

    [1] PARRY & COUNTER ⚔️     (Balanced - Standard damage)
    [2] DODGE & THRUST 🗡️      (Risky - High damage if successful)
    [3] DEFENSIVE STANCE 🛡️    (Safe - Reduce incoming damage)
    [4] SPECIAL: Dragon Pierces the Clouds ⚡
        (Costs 30 Morale - Devastating if hits)

═══════════════════════════════════════════════════════════════
```

---

## 🏛️ Phase 4: Deep Internal Affairs

### 4.1 Council System

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
  [5] Adjourn Council

═══════════════════════════════════════════════════════════════
```

### 4.2 Officer Assignment Interface

```
═══════════════════════════════════════════════════════════════
                    👥 OFFICER MANAGEMENT - CHENGDU
═══════════════════════════════════════════════════════════════

TASK ASSIGNMENTS                    EFFECTIVENESS
────────────────                    ─────────────

  🌾 AGRICULTURE (2 slots)
     ├─ Huang Zhong [POL:62]        ████████░░ Good
     └─ [EMPTY - Assign officer]

  💹 COMMERCE (2 slots)
     ├─ Mi Zhu [CHR:89] +MERCHANT   ██████████ Excellent!
     └─ [EMPTY - Assign officer]

  📚 RESEARCH (1 slot)
     └─ Fa Zheng [INT:95]           ██████████ Excellent!

  ⚔️ TRAINING (3 slots)
     ├─ Guan Yu [LED:97] +STRICT    ██████████ Excellent!
     ├─ Zhang Fei [LED:85]          █████████░ Very Good
     └─ [EMPTY - Assign officer]

  🏰 FORTIFICATION (1 slot)
     └─ [EMPTY - Assign officer]

═══════════════════════════════════════════════════════════════
AVAILABLE OFFICERS (Not Assigned)

  Name          Best Stat    Traits           Energy
  ──────────────────────────────────────────────────
  Zhao Yun      LED:96       Brave, Loyal     ████████░░
  Wei Yan       LED:89       Fierce           ██████████
  Ma Chao       LED:91       Brave            █████░░░░░ (tired)

═══════════════════════════════════════════════════════════════
  [A]ssign │ [R]emove │ [V]iew Officer │ [B]ack
═══════════════════════════════════════════════════════════════
```

---

## 📋 Task Breakdown for Implementation

### Epic 1: ASCII Map System
```
Priority: HIGH │ Complexity: MEDIUM │ Fun Factor: ⭐⭐⭐⭐⭐

Tasks:
  [ ] 1.1 Create map_renderer.py module
  [ ] 1.2 Define map topology (city connections, terrain)
  [ ] 1.3 Implement strategic map display
  [ ] 1.4 Implement city detail view
  [ ] 1.5 Implement battle map view
  [ ] 1.6 Add army movement visualization on map
  [ ] 1.7 Add faction color coding
  [ ] 1.8 Add zoom levels (China → Region → City)
```

### Epic 2: Enhanced Officer System
```
Priority: HIGH │ Complexity: MEDIUM │ Fun Factor: ⭐⭐⭐⭐⭐

Tasks:
  [ ] 2.1 Add relationship system to Officer model
  [ ] 2.2 Create ASCII portrait generator
  [ ] 2.3 Add special abilities per officer
  [ ] 2.4 Implement trait effects on gameplay
  [ ] 2.5 Add officer dialogue/personality
  [ ] 2.6 Create random event system
  [ ] 2.7 Add historical events (Peach Garden, etc.)
  [ ] 2.8 Implement officer death/retirement events
```

### Epic 3: Battle System Overhaul
```
Priority: HIGH │ Complexity: HIGH │ Fun Factor: ⭐⭐⭐⭐⭐

Tasks:
  [ ] 3.1 Design tactical decision tree
  [ ] 3.2 Implement terrain effects
  [ ] 3.3 Add weather system
  [ ] 3.4 Create duel mini-game
  [ ] 3.5 Implement special tactics (fire, ambush, etc.)
  [ ] 3.6 Add morale and stamina systems
  [ ] 3.7 Create battle narrative generator
  [ ] 3.8 Implement siege mechanics
  [ ] 3.9 Add supply line system
```

### Epic 4: Internal Affairs Depth
```
Priority: MEDIUM │ Complexity: MEDIUM │ Fun Factor: ⭐⭐⭐⭐

Tasks:
  [ ] 4.1 Implement council system
  [ ] 4.2 Add advisor recommendations
  [ ] 4.3 Create policy system
  [ ] 4.4 Add city specialization options
  [ ] 4.5 Implement population growth/migration
  [ ] 4.6 Add facilities (markets, academies, etc.)
  [ ] 4.7 Create espionage system
```

### Epic 5: Diplomacy System
```
Priority: MEDIUM │ Complexity: MEDIUM │ Fun Factor: ⭐⭐⭐⭐

Tasks:
  [ ] 5.1 Add faction relationships
  [ ] 5.2 Implement alliance system
  [ ] 5.3 Create marriage/hostage mechanics
  [ ] 5.4 Add trade agreements
  [ ] 5.5 Implement tribute system
  [ ] 5.6 Create envoy conversations
```

### Epic 6: Quality of Life
```
Priority: LOW │ Complexity: LOW │ Fun Factor: ⭐⭐⭐

Tasks:
  [ ] 6.1 Add turn summary reports
  [ ] 6.2 Create notification system
  [ ] 6.3 Implement auto-assign officers
  [ ] 6.4 Add difficulty settings
  [ ] 6.5 Create achievement system
```

---

## 🔄 Suggested Development Loop

For each feature:

```
1. DESIGN (30 min)
   └─ Sketch ASCII layout on paper/notepad
   └─ Define data models needed
   └─ Write user stories

2. TEST FIRST (20 min)
   └─ Write failing tests for new functionality
   └─ Define edge cases

3. IMPLEMENT (1-2 hours)
   └─ Code the feature
   └─ Make tests pass

4. POLISH (30 min)
   └─ Add i18n strings (EN + ZH)
   └─ Refine ASCII art
   └─ Manual testing in browser

5. ITERATE
   └─ Play test for fun factor
   └─ Adjust based on feel
```

---

## 🎮 What Makes It "Addictive"

### Hook Mechanics
1. **"One More Turn"** - End each turn with a teaser
   ```
   ═══════════════════════════════════════════════════════════
   📜 NEXT TURN PREVIEW:
     • Ma Chao arrives at your court seeking refuge
     • Cao Cao's army spotted near Hanzhong
     • Your new cavalry unit completes training

   [Press ENTER to continue...]
   ═══════════════════════════════════════════════════════════
   ```

2. **Narrative Weight** - Make decisions feel consequential
   ```
   ⚠️ Guan Yu's loyalty has dropped to 45.
      He mentions missing his oath brothers...

   If loyalty drops below 30, he may defect to Cao Cao!
   ```

3. **Celebration Moments** - Reward achievements
   ```
   🎉 ACHIEVEMENT UNLOCKED: "The Sleeping Dragon Awakens"
      You've recruited Zhuge Liang to your faction!

   🎉 MILESTONE: You now control 5 cities!
      The people whisper of a new power rising...
   ```

4. **Emergent Stories** - Random events create unique narratives
   ```
   📜 EVENT: A wandering warrior seeks employment...

   A disheveled man in tattered armor approaches your court.

   "I am Xu Shu. I was once advisor to Cao Cao, but I could
    not serve a tyrant. I offer you my sword and my mind."

   [1] Welcome him warmly
   [2] Test his abilities first
   [3] Refuse - he may be a spy
   ```

---

## 📁 Suggested File Structure Update

```
sango-text-sim/
├── src/
│   ├── models.py           # Core data models
│   ├── constants.py        # Game balance
│   ├── utils.py            # Helpers
│   ├── engine.py           # Core mechanics
│   ├── world.py            # World data
│   ├── persistence.py      # Save/load
│   │
│   ├── display/            # NEW: ASCII rendering
│   │   ├── __init__.py
│   │   ├── map_view.py     # Strategic map
│   │   ├── city_view.py    # City details
│   │   ├── battle_view.py  # Battle display
│   │   ├── officer_view.py # Officer profiles
│   │   └── components.py   # Reusable UI elements
│   │
│   ├── systems/            # NEW: Game systems
│   │   ├── __init__.py
│   │   ├── battle.py       # Tactical combat
│   │   ├── duel.py         # Duel mini-game
│   │   ├── diplomacy.py    # Faction relations
│   │   ├── events.py       # Random events
│   │   └── council.py      # Advisor system
│   │
│   └── data/               # NEW: Static game data
│       ├── officers.json   # Officer definitions
│       ├── cities.json     # City data
│       ├── events.json     # Event definitions
│       └── abilities.json  # Special abilities
│
├── templates/              # Web templates
├── tests/                  # Test suite
├── locales/                # i18n
├── game.py                 # CLI entry
└── web_server.py           # Web entry
```

---

## 🚀 Recommended First Sprint (2 weeks)

**Goal: Make the map feel alive**

Week 1:
- [ ] Implement ASCII strategic map renderer
- [ ] Add city detail view with progress bars
- [ ] Create officer profile view
- [ ] Add 5 special abilities to key officers

Week 2:
- [ ] Implement basic duel system
- [ ] Add 3 random events
- [ ] Create turn summary with preview
- [ ] Add relationship basics (sworn brothers)

This sprint alone will dramatically improve the "feel" of the game!

---

## Questions for You

1. **Platform Priority**: Is the web interface or CLI your main focus?
2. **Scope**: Do you want ALL ROTK11 features, or a curated subset?
3. **Historical Accuracy**: Strict to history, or allow alternate scenarios?
4. **AI Difficulty**: How smart should enemy AI be?

Let me know and I can dive deeper into any of these areas!
