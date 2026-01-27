"""
Tests for the game engine module.

This module tests core game mechanics including:
- Battle resolution
- City ownership transfers
- Officer assignments and their effects
- Monthly economy processing
- AI decision making
- Officer defection system
- Turn progression
- Victory conditions
"""

import pytest
from src.models import Officer, City, Faction, GameState, TurnEvent, EventCategory
from src import engine


class TestTechAttackBonus:
    """Tests for technology-based attack bonuses."""
    
    def test_no_cities_returns_base_multiplier(self, empty_game_state):
        """Faction with no cities gets 1.0 multiplier."""
        empty_game_state.factions["TestFaction"] = Faction(
            name="TestFaction", cities=[], officers=[], relations={}
        )
        result = engine.tech_attack_bonus(empty_game_state, "TestFaction")
        assert result == 1.0
    
    def test_tech_level_affects_multiplier(self, empty_game_state):
        """Higher tech level increases attack multiplier."""
        city1 = City(name="C1", owner="TestFaction", troops=100, food=100, gold=100, tech=60, defense=50, morale=70)
        city2 = City(name="C2", owner="TestFaction", troops=100, food=100, gold=100, tech=40, defense=50, morale=70)
        
        empty_game_state.cities = {"C1": city1, "C2": city2}
        empty_game_state.factions["TestFaction"] = Faction(
            name="TestFaction", cities=["C1", "C2"], officers=[], relations={}
        )
        
        result = engine.tech_attack_bonus(empty_game_state, "TestFaction")
        # Average tech = (60+40)/2 = 50, multiplier = 1.0 + 50/50 = 2.0
        assert result == 2.0


class TestBattle:
    """Tests for battle resolution mechanics."""
    
    def test_battle_reduces_troops(self, populated_game_state):
        """Battle should reduce troop counts."""
        # Create attacker and defender cities
        attacker = City(name="AttackerCity", owner="Shu", troops=200, food=100, gold=100, tech=50, defense=50, morale=70)
        defender = City(name="DefenderCity", owner="Wei", troops=150, food=100, gold=100, tech=50, defense=50, morale=70)
        
        populated_game_state.cities["AttackerCity"] = attacker
        populated_game_state.cities["DefenderCity"] = defender
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["DefenderCity"], officers=[], relations={})
        
        initial_atk_troops = attacker.troops
        initial_def_troops = defender.troops
        
        victory, casualties = engine.battle(populated_game_state, attacker, defender, 50)
        
        # Attacker loses casualties
        assert attacker.troops == initial_atk_troops - casualties
        # Defender loses some troops if battle was decisive
        assert defender.troops <= initial_def_troops
    
    def test_battle_affects_morale(self, populated_game_state):
        """Battle should adjust morale for both sides."""
        attacker = City(name="AttackerCity", owner="Shu", troops=200, food=100, gold=100, tech=50, defense=50, morale=70)
        defender = City(name="DefenderCity", owner="Wei", troops=150, food=100, gold=100, tech=50, defense=50, morale=70)
        
        populated_game_state.cities["AttackerCity"] = attacker
        populated_game_state.cities["DefenderCity"] = defender
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["DefenderCity"], officers=[], relations={})
        
        initial_atk_morale = attacker.morale
        initial_def_morale = defender.morale
        
        engine.battle(populated_game_state, attacker, defender, 50)
        
        # Morale should change (increase for winner, decrease for loser)
        assert attacker.morale != initial_atk_morale or defender.morale != initial_def_morale
    
    def test_battle_returns_valid_result(self, populated_game_state):
        """Battle should return victory bool and casualty count."""
        attacker = City(name="AttackerCity", owner="Shu", troops=200, food=100, gold=100, tech=50, defense=50, morale=70)
        defender = City(name="DefenderCity", owner="Wei", troops=150, food=100, gold=100, tech=50, defense=50, morale=70)
        
        populated_game_state.cities["AttackerCity"] = attacker
        populated_game_state.cities["DefenderCity"] = defender
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["DefenderCity"], officers=[], relations={})
        
        victory, casualties = engine.battle(populated_game_state, attacker, defender, 50)
        
        assert isinstance(victory, bool)
        assert isinstance(casualties, int)
        assert casualties >= 0


class TestTransferCity:
    """Tests for city ownership transfer."""
    
    def test_transfer_changes_owner(self, populated_game_state):
        """Transferring city should change its owner."""
        city = populated_game_state.cities["TestCity"]
        old_owner = city.owner
        new_owner = "Wei"
        
        engine.transfer_city(populated_game_state, new_owner, city)
        
        assert city.owner == new_owner
        assert city.owner != old_owner
    
    def test_transfer_updates_faction_cities(self, populated_game_state):
        """Transferring city should update faction city lists."""
        city = populated_game_state.cities["TestCity"]
        old_owner = city.owner
        new_owner = "Wei"
        
        engine.transfer_city(populated_game_state, new_owner, city)
        
        # Old owner loses city
        if old_owner in populated_game_state.factions:
            assert city.name not in populated_game_state.factions[old_owner].cities
        # New owner gains city
        assert city.name in populated_game_state.factions[new_owner].cities
    
    def test_transfer_resets_defense_and_morale(self, populated_game_state):
        """Transferring city should reset defense and morale."""
        city = populated_game_state.cities["TestCity"]
        
        engine.transfer_city(populated_game_state, "Wei", city)
        
        assert city.defense == 20
        assert city.morale == 50


class TestAssignmentEffect:
    """Tests for officer assignment effects."""
    
    def test_farm_increases_food(self, populated_game_state):
        """Farming task should increase city food."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "farm"
        officer.task_city = city.name
        
        initial_food = city.food
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert city.food > initial_food
    
    def test_trade_increases_gold(self, populated_game_state):
        """Trading task should increase city gold."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "trade"
        officer.task_city = city.name
        
        initial_gold = city.gold
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert city.gold > initial_gold
    
    def test_research_increases_tech(self, populated_game_state):
        """Research task should increase city tech."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "research"
        officer.task_city = city.name
        
        initial_tech = city.tech
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert city.tech > initial_tech
    
    def test_train_increases_troops(self, populated_game_state):
        """Training task should increase city troops."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "train"
        officer.task_city = city.name
        
        initial_troops = city.troops
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert city.troops > initial_troops
    
    def test_fortify_increases_defense(self, populated_game_state):
        """Fortifying task should increase city defense."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "fortify"
        officer.task_city = city.name
        
        initial_defense = city.defense
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert city.defense > initial_defense
    
    def test_recruit_creates_new_officer(self, populated_game_state):
        """Recruiting task should create a new officer."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "recruit"
        officer.task_city = city.name
        
        initial_officer_count = len(populated_game_state.officers)
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert len(populated_game_state.officers) > initial_officer_count
    
    def test_assignment_reduces_energy(self, populated_game_state):
        """Completing assignment should reduce officer energy."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "farm"
        officer.task_city = city.name
        
        initial_energy = officer.energy
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert officer.energy < initial_energy
    
    def test_assignment_clears_task(self, populated_game_state):
        """Completing assignment should clear task fields."""
        officer = populated_game_state.officers["TestOfficer"]
        city = populated_game_state.cities["TestCity"]
        officer.task = "farm"
        officer.task_city = city.name
        officer.busy = True
        
        engine.assignment_effect(populated_game_state, officer, city)
        
        assert officer.task is None
        assert officer.task_city is None
        assert officer.busy is False


class TestProcessAssignments:
    """Tests for assignment processing."""
    
    def test_processes_all_officers_with_tasks(self, populated_game_state):
        """Should process all officers with assigned tasks."""
        # Get test officer
        test_officer = populated_game_state.officers["TestOfficer"]
        test_officer.task = "farm"
        test_officer.task_city = "TestCity"
        
        # Create second officer
        officer2 = Officer(
            name="Officer2", faction="Shu", city="TestCity",
            leadership=50, intelligence=50, politics=50, charisma=50,
            energy=80, loyalty=70, traits=[], task="trade", task_city="TestCity", busy=True
        )
        populated_game_state.officers["Officer2"] = officer2
        populated_game_state.factions["Shu"].officers.append("Officer2")
        
        engine.process_assignments(populated_game_state)
        
        # Both should have tasks cleared
        assert test_officer.task is None
        assert officer2.task is None
    
    def test_skips_officers_in_enemy_cities(self, populated_game_state):
        """Should not process officers in cities not owned by their faction."""
        officer = populated_game_state.officers["TestOfficer"]
        # Create an enemy city
        enemy_city = City(name="EnemyCity", owner="Wei", troops=100, food=100, gold=100, 
                         tech=50, defense=50, morale=70)
        populated_game_state.cities["EnemyCity"] = enemy_city
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["EnemyCity"], officers=[], relations={})
        
        officer.task = "farm"
        officer.task_city = "EnemyCity"  # Enemy city
        initial_energy = officer.energy
        
        engine.process_assignments(populated_game_state)
        
        # Task should be cleared but no effect applied
        assert officer.energy == initial_energy  # No energy consumed


class TestMonthlyEconomy:
    """Tests for monthly economic processing."""
    
    def test_cities_receive_income(self, populated_game_state):
        """Cities should receive base income."""
        city = populated_game_state.cities["TestCity"]
        initial_gold = city.gold
        
        engine.monthly_economy(populated_game_state)
        
        assert city.gold >= initial_gold  # May decrease due to upkeep, but base income added
    
    def test_upkeep_consumes_resources(self, populated_game_state):
        """Troops should consume food and gold."""
        city = populated_game_state.cities["TestCity"]
        city.troops = 1000  # High troop count
        city.food = 1000
        initial_food = city.food
        
        engine.monthly_economy(populated_game_state)
        
        assert city.food < initial_food  # Upkeep consumed food
    
    def test_starvation_reduces_troops(self, populated_game_state):
        """Food shortage should cause troop losses."""
        city = populated_game_state.cities["TestCity"]
        city.troops = 100
        city.food = -10  # Negative food triggers starvation
        
        engine.monthly_economy(populated_game_state)
        
        assert city.troops < 100  # Some troops deserted
        assert city.food == 0  # Food reset to 0
    
    def test_desertion_reduces_troops(self, populated_game_state):
        """Gold shortage should cause desertions."""
        city = populated_game_state.cities["TestCity"]
        city.troops = 100
        city.gold = -10  # Negative gold triggers desertion
        
        engine.monthly_economy(populated_game_state)
        
        assert city.troops < 100  # Some troops deserted
        assert city.gold == 0  # Gold reset to 0
    
    def test_january_tax_bonus(self, populated_game_state):
        """January should provide tax bonus."""
        populated_game_state.month = 1
        city = populated_game_state.cities["TestCity"]
        initial_gold = city.gold
        
        engine.monthly_economy(populated_game_state)
        
        # Should receive base income + tax bonus
        assert city.gold > initial_gold
    
    def test_july_harvest_bonus(self, populated_game_state):
        """July should provide harvest bonus."""
        populated_game_state.month = 7
        city = populated_game_state.cities["TestCity"]
        initial_food = city.food
        
        engine.monthly_economy(populated_game_state)
        
        # Should receive harvest bonus
        assert city.food > initial_food


class TestAITurn:
    """Tests for AI decision making."""
    
    def test_player_faction_skipped(self, populated_game_state):
        """AI should not process player faction."""
        player_officer = populated_game_state.officers["TestOfficer"]
        initial_energy = player_officer.energy
        
        engine.ai_turn(populated_game_state, populated_game_state.player_faction)
        
        # Player officer should not be modified
        assert player_officer.energy == initial_energy
    
    def test_low_energy_officers_rest(self, populated_game_state):
        """Officers with low energy should rest."""
        # Create AI faction and city
        ai_city = City(name="AICity", owner="TestAI", troops=100, food=100, gold=100, 
                      tech=50, defense=50, morale=70)
        populated_game_state.cities["AICity"] = ai_city
        populated_game_state.factions["TestAI"] = Faction(
            name="TestAI", cities=["AICity"], officers=["TestOfficer2"], relations={}
        )
        
        officer = Officer(
            name="TestOfficer2", faction="TestAI", city="AICity",
            leadership=50, intelligence=50, politics=50, charisma=50,
            energy=20,  # Low energy
            loyalty=70, traits=[], task="farm", task_city="AICity", busy=True
        )
        populated_game_state.officers["TestOfficer2"] = officer
        
        engine.ai_turn(populated_game_state, "TestAI")
        
        # Task should be cleared and energy increased
        assert officer.task is None
        assert officer.energy > 20
    
    def test_idle_officers_get_tasks(self, populated_game_state):
        """Idle officers with sufficient energy should get tasks."""
        # Create AI faction and city
        ai_city = City(name="AICity", owner="TestAI", troops=100, food=100, gold=100, 
                      tech=50, defense=50, morale=70)
        populated_game_state.cities["AICity"] = ai_city
        populated_game_state.factions["TestAI"] = Faction(
            name="TestAI", cities=["AICity"], officers=["TestOfficer3"], relations={}
        )
        
        officer = Officer(
            name="TestOfficer3", faction="TestAI", city="AICity",
            leadership=50, intelligence=50, politics=50, charisma=50,
            energy=80,  # Good energy
            loyalty=70, traits=[], task=None, task_city=None, busy=False
        )
        populated_game_state.officers["TestOfficer3"] = officer
        
        engine.ai_turn(populated_game_state, "TestAI")
        
        # Officer should get a task or rest
        # Energy should change (either task assigned or rest recovery)
        assert officer.energy != 80 or officer.task is not None


class TestTryDefections:
    """Tests for officer defection system."""
    
    def test_low_loyalty_officer_may_defect(self, populated_game_state):
        """Officers with very low loyalty may defect."""
        officer = populated_game_state.officers["TestOfficer"]
        officer.loyalty = 30  # Very low loyalty
        officer.city = "TestCity"
        
        # Add adjacent enemy city
        enemy_city = City(name="EnemyCity", owner="Wei", troops=100, food=100, gold=100, 
                         tech=50, defense=50, morale=70)
        populated_game_state.cities["EnemyCity"] = enemy_city
        populated_game_state.adj["TestCity"] = ["EnemyCity"]
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["EnemyCity"], officers=[], relations={})
        
        # Run multiple times to account for randomness
        original_faction = officer.faction
        defected = False
        for _ in range(100):  # 10% chance, so should defect in 100 tries
            officer.faction = original_faction
            officer.city = "TestCity"
            populated_game_state.factions[original_faction].officers = [officer.name]
            populated_game_state.factions["Wei"].officers = []
            
            engine.try_defections(populated_game_state)
            
            if officer.faction != original_faction:
                defected = True
                break
        
        assert defected  # Should defect at least once in 100 tries
    
    def test_high_loyalty_officer_does_not_defect(self, populated_game_state):
        """Officers with high loyalty should not defect."""
        officer = populated_game_state.officers["TestOfficer"]
        officer.loyalty = 90  # High loyalty
        officer.city = "TestCity"
        original_faction = officer.faction
        
        # Add adjacent enemy city
        enemy_city = City(name="EnemyCity", owner="Wei", troops=100, food=100, gold=100, 
                         tech=50, defense=50, morale=70)
        populated_game_state.cities["EnemyCity"] = enemy_city
        populated_game_state.adj["TestCity"] = ["EnemyCity"]
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["EnemyCity"], officers=[], relations={})
        
        engine.try_defections(populated_game_state)
        
        assert officer.faction == original_faction


class TestEndTurn:
    """Tests for turn progression."""

    def test_end_turn_advances_month(self, populated_game_state):
        """End turn should increment month."""
        initial_month = populated_game_state.month

        events = engine.end_turn(populated_game_state)

        assert populated_game_state.month == initial_month + 1
        assert isinstance(events, list)

    def test_end_turn_advances_year(self, populated_game_state):
        """End turn in December should advance year."""
        populated_game_state.month = 12
        initial_year = populated_game_state.year

        events = engine.end_turn(populated_game_state)

        assert populated_game_state.year == initial_year + 1
        assert populated_game_state.month == 1
        assert isinstance(events, list)

    def test_end_turn_recovers_idle_officers(self, populated_game_state):
        """Idle officers should recover energy at end of turn."""
        officer = populated_game_state.officers["TestOfficer"]
        officer.task = None
        officer.energy = 50

        events = engine.end_turn(populated_game_state)

        assert officer.energy > 50
        assert isinstance(events, list)

    def test_end_turn_returns_events_list(self, populated_game_state):
        """End turn should return a list of TurnEvent objects."""
        events = engine.end_turn(populated_game_state)

        assert isinstance(events, list)
        # All items should be TurnEvent objects
        for event in events:
            assert isinstance(event, TurnEvent)
            assert isinstance(event.category, EventCategory)
            assert isinstance(event.message, str)
            assert isinstance(event.data, dict)


class TestCategorizeMessage:
    """Tests for message categorization."""

    def test_categorize_military_message(self):
        """Military keywords should categorize as MILITARY."""
        messages = [
            "Battle won at TestCity",
            "Victory! TestCity captured",
            "Defeat at the gates",
            "Attack successful",
            "Troops deployed"
        ]
        for msg in messages:
            category = engine.categorize_message(msg)
            assert category == EventCategory.MILITARY

    def test_categorize_officer_message(self):
        """Officer keywords should categorize as OFFICER."""
        messages = [
            "Officer recruited at TestCity",
            "Liu Bei defected to Wei",
            "Loyalty increased",
            "New officer joins"
        ]
        for msg in messages:
            category = engine.categorize_message(msg)
            assert category == EventCategory.OFFICER

    def test_categorize_diplomatic_message(self):
        """Diplomatic keywords should categorize as DIPLOMATIC."""
        messages = [
            "Alliance formed with Wei",
            "Treaty signed",
            "Relations improved",
            "Diplomatic mission successful"
        ]
        for msg in messages:
            category = engine.categorize_message(msg)
            assert category == EventCategory.DIPLOMATIC

    def test_categorize_economy_message(self):
        """Economic messages should categorize as ECONOMY."""
        messages = [
            "Tax collected: 100 gold",
            "Harvest yields 200 food",
            "Starvation at TestCity",
            "Income from commerce"
        ]
        for msg in messages:
            category = engine.categorize_message(msg)
            assert category == EventCategory.ECONOMY


class TestCheckVictory:
    """Tests for victory and defeat conditions."""
    
    def test_player_controls_all_cities_wins(self, populated_game_state):
        """Player owning all cities should trigger victory."""
        # Set all cities to player faction
        for city in populated_game_state.cities.values():
            city.owner = populated_game_state.player_faction
        
        result = engine.check_victory(populated_game_state)
        
        assert result is True
    
    def test_player_has_no_cities_loses(self, populated_game_state):
        """Player with no cities should trigger defeat."""
        # Remove all player cities
        populated_game_state.factions[populated_game_state.player_faction].cities = []
        
        result = engine.check_victory(populated_game_state)
        
        assert result is True
    
    def test_ongoing_game_no_victory(self, populated_game_state):
        """Normal game state should not trigger victory."""
        # Add a second city owned by a different faction
        enemy_city = City(name="EnemyCity", owner="Wei", troops=100, food=100, gold=100, 
                         tech=50, defense=50, morale=70)
        populated_game_state.cities["EnemyCity"] = enemy_city
        populated_game_state.factions["Wei"] = Faction(name="Wei", cities=["EnemyCity"], officers=[], relations={})
        
        result = engine.check_victory(populated_game_state)
        
        assert result is False
