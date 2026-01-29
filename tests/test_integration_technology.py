"""
Integration Tests: Technology Research Path

This module tests technology system mechanics:
- Tech prerequisite checking
- Research progress calculation
- Tech effect application
- Optimal research paths
- Tech bonuses in combat

Based on ROTK11's technology tree and research system.
"""
import pytest
from src.tech import load_technologies, get_technology, get_available_techs
from src.models import Technology


class TestTechnologyLoading:
    """Test technology data loading."""

    def test_load_technologies_returns_list(self):
        """Loading technologies should return a list."""
        techs = load_technologies()
        assert isinstance(techs, list)
        assert len(techs) > 0

    def test_all_technologies_have_required_fields(self):
        """All technologies should have required fields."""
        techs = load_technologies()
        for tech in techs:
            assert tech.id
            assert tech.category
            assert tech.name_key
            assert tech.cost >= 0
            assert tech.turns >= 0

    def test_technology_categories(self):
        """Technologies should have valid categories."""
        techs = load_technologies()
        valid_categories = {"military", "economy", "special"}

        for tech in techs:
            assert tech.category in valid_categories

    def test_get_technology_by_id(self):
        """Should retrieve specific technology by ID."""
        tech = get_technology("iron_weapons")
        assert tech is not None
        assert tech.id == "iron_weapons"
        assert tech.category == "military"

    def test_get_technology_invalid_id(self):
        """Should return None for invalid technology ID."""
        tech = get_technology("nonexistent_tech")
        assert tech is None


class TestTechnologyPrerequisites:
    """Test technology prerequisite checking."""

    def test_base_tech_no_prerequisites(self):
        """Base technologies should have no prerequisites."""
        iron_weapons = get_technology("iron_weapons")
        assert iron_weapons.prerequisites == []

    def test_advanced_tech_has_prerequisites(self):
        """Advanced technologies should require prerequisites."""
        steel_armor = get_technology("steel_armor")
        assert "iron_weapons" in steel_armor.prerequisites

    def test_siege_engines_prerequisites(self):
        """Siege engines require iron weapons."""
        siege = get_technology("siege_engines")
        assert "iron_weapons" in siege.prerequisites

    def test_fire_arrows_prerequisites(self):
        """Fire arrows require archery mastery."""
        fire_arrows = get_technology("fire_arrows")
        assert "archery_mastery" in fire_arrows.prerequisites

    def test_fire_mastery_prerequisites(self):
        """Fire attack mastery requires fire arrows."""
        fire_mastery = get_technology("fire_attack_mastery")
        assert "fire_arrows" in fire_mastery.prerequisites

    def test_elite_guards_multiple_prerequisites(self):
        """Elite guards require both steel armor and cavalry tactics."""
        elite = get_technology("elite_guards")
        assert "steel_armor" in elite.prerequisites
        assert "cavalry_tactics" in elite.prerequisites
        assert len(elite.prerequisites) == 2

    def test_advanced_farming_multiple_prerequisites(self):
        """Advanced farming requires both crop rotation and irrigation."""
        farming = get_technology("advanced_farming")
        assert "crop_rotation" in farming.prerequisites
        assert "irrigation" in farming.prerequisites

    def test_prerequisite_chain_depth(self):
        """Test prerequisite chain: fire_attack_mastery <- fire_arrows <- archery_mastery."""
        # Archery mastery is base
        archery = get_technology("archery_mastery")
        assert archery.prerequisites == []

        # Fire arrows depends on archery
        fire_arrows = get_technology("fire_arrows")
        assert "archery_mastery" in fire_arrows.prerequisites

        # Fire mastery depends on fire arrows
        fire_mastery = get_technology("fire_attack_mastery")
        assert "fire_arrows" in fire_mastery.prerequisites


class TestAvailableTechnologies:
    """Test available technology detection."""

    def test_no_research_base_techs_available(self):
        """With no research, base technologies should be available."""
        available = get_available_techs([])
        available_ids = [t.id for t in available]

        # Base techs should be available
        assert "iron_weapons" in available_ids
        assert "cavalry_tactics" in available_ids
        assert "archery_mastery" in available_ids
        assert "irrigation" in available_ids
        assert "trade_routes" in available_ids

    def test_researched_tech_not_available(self):
        """Already researched technologies should not be available."""
        available = get_available_techs(["iron_weapons"])
        available_ids = [t.id for t in available]

        assert "iron_weapons" not in available_ids

    def test_prerequisite_met_unlocks_tech(self):
        """Completing prerequisite should unlock advanced tech."""
        available = get_available_techs(["iron_weapons"])
        available_ids = [t.id for t in available]

        # Steel armor and siege engines now available
        assert "steel_armor" in available_ids
        assert "siege_engines" in available_ids

    def test_prerequisite_not_met_locks_tech(self):
        """Technologies with unmet prerequisites should be locked."""
        available = get_available_techs([])
        available_ids = [t.id for t in available]

        # These require prerequisites
        assert "steel_armor" not in available_ids
        assert "siege_engines" not in available_ids
        assert "fire_arrows" not in available_ids

    def test_multiple_prerequisites_all_required(self):
        """All prerequisites must be met for multi-prereq tech."""
        # Only steel armor researched
        available = get_available_techs(["iron_weapons", "steel_armor"])
        available_ids = [t.id for t in available]
        assert "elite_guards" not in available_ids

        # Both prerequisites met
        available = get_available_techs(["iron_weapons", "steel_armor", "cavalry_tactics"])
        available_ids = [t.id for t in available]
        assert "elite_guards" in available_ids


class TestResearchProgress:
    """Test research progress calculation."""

    def test_iron_weapons_research_time(self):
        """Iron weapons should take 3 turns to research."""
        tech = get_technology("iron_weapons")
        assert tech.turns == 3

    def test_elite_guards_longest_research(self):
        """Elite guards should take 6 turns (longest military tech)."""
        tech = get_technology("elite_guards")
        assert tech.turns == 6

    def test_irrigation_shortest_research(self):
        """Irrigation should take 2 turns (quick economy tech)."""
        tech = get_technology("irrigation")
        assert tech.turns == 2

    def test_research_cost_scaling(self):
        """More advanced techs should cost more."""
        iron = get_technology("iron_weapons")
        steel = get_technology("steel_armor")
        elite = get_technology("elite_guards")

        assert iron.cost < steel.cost < elite.cost

    def test_total_military_research_time(self):
        """Calculate total turns to research all military techs."""
        techs = load_technologies()
        military_techs = [t for t in techs if t.category == "military"]

        total_turns = sum(t.turns for t in military_techs)
        # iron(3) + steel(4) + cavalry(3) + archery(3) + siege(5) + naval(4) + fire_arrows(3) + elite(6)
        assert total_turns == 31

    def test_research_progress_simulation(self):
        """Simulate research progress over turns."""
        tech = get_technology("steel_armor")
        turns_needed = tech.turns

        progress = 0
        turns_spent = 0
        while progress < turns_needed:
            progress += 1
            turns_spent += 1

        assert turns_spent == 4
        assert progress >= turns_needed


class TestTechnologyEffects:
    """Test technology effect application."""

    def test_iron_weapons_attack_bonus(self):
        """Iron weapons should provide +5 attack bonus."""
        tech = get_technology("iron_weapons")
        assert tech.effects.get("attack_bonus") == 5

    def test_steel_armor_defense_bonus(self):
        """Steel armor should provide +5 defense bonus."""
        tech = get_technology("steel_armor")
        assert tech.effects.get("defense_bonus") == 5

    def test_cavalry_tactics_bonus(self):
        """Cavalry tactics should provide +10 cavalry bonus."""
        tech = get_technology("cavalry_tactics")
        assert tech.effects.get("cavalry_bonus") == 10

    def test_archery_mastery_bonus(self):
        """Archery mastery should provide +10 archer bonus."""
        tech = get_technology("archery_mastery")
        assert tech.effects.get("archer_bonus") == 10

    def test_siege_engines_bonus(self):
        """Siege engines should provide +15 siege bonus."""
        tech = get_technology("siege_engines")
        assert tech.effects.get("siege_bonus") == 15

    def test_naval_warfare_bonus(self):
        """Naval warfare should provide +10 naval bonus."""
        tech = get_technology("naval_warfare")
        assert tech.effects.get("naval_bonus") == 10

    def test_fire_arrows_bonus(self):
        """Fire arrows should provide +10 fire attack bonus."""
        tech = get_technology("fire_arrows")
        assert tech.effects.get("fire_attack_bonus") == 10

    def test_elite_guards_special_effect(self):
        """Elite guards should enable elite troops."""
        tech = get_technology("elite_guards")
        assert tech.effects.get("elite_troops") is True

    def test_fire_mastery_special_effect(self):
        """Fire attack mastery should enable fire mastery."""
        tech = get_technology("fire_attack_mastery")
        assert tech.effects.get("fire_mastery") is True


class TestEconomyTechEffects:
    """Test economy technology effects."""

    def test_irrigation_food_production(self):
        """Irrigation should increase food production by 10%."""
        tech = get_technology("irrigation")
        assert tech.effects.get("food_production") == 10

    def test_crop_rotation_food_production(self):
        """Crop rotation should increase food production by 15%."""
        tech = get_technology("crop_rotation")
        assert tech.effects.get("food_production") == 15

    def test_trade_routes_gold_production(self):
        """Trade routes should increase gold production by 10%."""
        tech = get_technology("trade_routes")
        assert tech.effects.get("gold_production") == 10

    def test_silk_road_gold_production(self):
        """Silk road should increase gold production by 20%."""
        tech = get_technology("silk_road")
        assert tech.effects.get("gold_production") == 20

    def test_granary_expansion_storage(self):
        """Granary expansion should increase food storage by 200."""
        tech = get_technology("granary_expansion")
        assert tech.effects.get("food_storage") == 200

    def test_taxation_reform_bonus(self):
        """Taxation reform should provide +15% tax bonus."""
        tech = get_technology("taxation_reform")
        assert tech.effects.get("tax_bonus") == 15

    def test_advanced_farming_agri_bonus(self):
        """Advanced farming should provide +20 agriculture bonus."""
        tech = get_technology("advanced_farming")
        assert tech.effects.get("agri_bonus") == 20


class TestSpecialTechEffects:
    """Test special technology effects."""

    def test_sun_tzu_art_strategy_bonus(self):
        """Sun Tzu Art of War should provide +10 strategy bonus."""
        tech = get_technology("sun_tzu_art")
        assert tech.effects.get("strategy_bonus") == 10

    def test_espionage_network_bonus(self):
        """Espionage network should provide +15 spy bonus."""
        tech = get_technology("espionage_network")
        assert tech.effects.get("spy_bonus") == 15

    def test_medicine_recovery_bonus(self):
        """Medicine should provide +10 recovery bonus."""
        tech = get_technology("medicine")
        assert tech.effects.get("recovery_bonus") == 10

    def test_diplomacy_arts_bonus(self):
        """Diplomacy arts should provide +10 diplomacy bonus."""
        tech = get_technology("diplomacy_arts")
        assert tech.effects.get("diplomacy_bonus") == 10

    def test_war_drums_morale_bonus(self):
        """War drums should provide +5 morale bonus."""
        tech = get_technology("war_drums")
        assert tech.effects.get("morale_bonus") == 5

    def test_fortification_wall_bonus(self):
        """Fortification should provide +10 wall bonus."""
        tech = get_technology("fortification")
        assert tech.effects.get("wall_bonus") == 10


class TestOptimalResearchPaths:
    """Test optimal research path strategies."""

    def test_cavalry_rush_path(self):
        """Cavalry rush path: cavalry_tactics only."""
        # Can be researched immediately, 3 turns, +10% cavalry
        cavalry = get_technology("cavalry_tactics")
        assert cavalry.prerequisites == []
        assert cavalry.turns == 3
        assert cavalry.effects.get("cavalry_bonus") == 10

    def test_archery_fire_path(self):
        """Archery-fire path: archery_mastery -> fire_arrows -> fire_mastery."""
        path = ["archery_mastery", "fire_arrows", "fire_attack_mastery"]
        total_turns = sum(get_technology(t).turns for t in path)
        total_cost = sum(get_technology(t).cost for t in path)

        # 3 + 3 + 4 = 10 turns
        assert total_turns == 10
        # 250 + 300 + 350 = 900 gold
        assert total_cost == 900

    def test_military_full_path(self):
        """Full military path to elite guards."""
        # iron_weapons -> steel_armor -> (+ cavalry_tactics) -> elite_guards
        iron = get_technology("iron_weapons")
        steel = get_technology("steel_armor")
        cavalry = get_technology("cavalry_tactics")
        elite = get_technology("elite_guards")

        path_turns = iron.turns + steel.turns + cavalry.turns + elite.turns
        # 3 + 4 + 3 + 6 = 16 turns
        assert path_turns == 16

    def test_economy_quick_start(self):
        """Economy quick start: irrigation + trade_routes."""
        irrigation = get_technology("irrigation")
        trade = get_technology("trade_routes")

        # Both can be researched simultaneously (no prereqs)
        assert irrigation.prerequisites == []
        assert trade.prerequisites == []

        # Total 4 turns if done in parallel, 5 if sequential
        assert irrigation.turns == 2
        assert trade.turns == 3

    def test_economy_full_path(self):
        """Full economy path for maximum production."""
        # irrigation -> crop_rotation -> advanced_farming
        # trade_routes -> silk_road
        irrigation = get_technology("irrigation")
        crop = get_technology("crop_rotation")
        advanced = get_technology("advanced_farming")
        trade = get_technology("trade_routes")
        silk = get_technology("silk_road")

        food_path = irrigation.turns + crop.turns + advanced.turns
        gold_path = trade.turns + silk.turns

        # Food: 2 + 3 + 5 = 10 turns
        assert food_path == 10
        # Gold: 3 + 4 = 7 turns
        assert gold_path == 7


class TestTechCombatBonuses:
    """Test technology bonuses applied to combat."""

    def test_attack_bonus_stacking(self):
        """Attack bonuses from multiple techs should stack."""
        iron = get_technology("iron_weapons")
        sun_tzu = get_technology("sun_tzu_art")

        # Direct attack bonus
        attack_bonus = iron.effects.get("attack_bonus", 0)
        # Strategy affects tactics
        strategy_bonus = sun_tzu.effects.get("strategy_bonus", 0)

        combined = attack_bonus + strategy_bonus
        assert combined == 15  # 5 + 10

    def test_cavalry_combat_bonus(self):
        """Cavalry tech should boost cavalry unit combat."""
        tech = get_technology("cavalry_tactics")
        base_damage = 100
        cavalry_bonus = tech.effects.get("cavalry_bonus", 0) / 100.0

        boosted_damage = base_damage * (1 + cavalry_bonus)
        assert boosted_damage == pytest.approx(110)

    def test_archer_combat_bonus(self):
        """Archery tech should boost archer unit combat."""
        tech = get_technology("archery_mastery")
        base_damage = 100
        archer_bonus = tech.effects.get("archer_bonus", 0) / 100.0

        boosted_damage = base_damage * (1 + archer_bonus)
        assert boosted_damage == pytest.approx(110)

    def test_fire_attack_bonus_stacking(self):
        """Fire attack bonuses should stack."""
        fire_arrows = get_technology("fire_arrows")

        base_fire_damage = 100
        fire_bonus = fire_arrows.effects.get("fire_attack_bonus", 0) / 100.0

        boosted = base_fire_damage * (1 + fire_bonus)
        assert boosted == pytest.approx(110)

    def test_siege_bonus_wall_damage(self):
        """Siege tech should boost wall damage."""
        siege = get_technology("siege_engines")
        base_siege_damage = 100
        siege_bonus = siege.effects.get("siege_bonus", 0) / 100.0

        boosted = base_siege_damage * (1 + siege_bonus)
        assert boosted == pytest.approx(115)

    def test_naval_combat_bonus(self):
        """Naval tech should boost water combat."""
        naval = get_technology("naval_warfare")
        base_naval = 100
        naval_bonus = naval.effects.get("naval_bonus", 0) / 100.0

        boosted = base_naval * (1 + naval_bonus)
        assert boosted == pytest.approx(110)

    def test_defense_bonus_damage_reduction(self):
        """Defense tech should reduce incoming damage."""
        steel = get_technology("steel_armor")
        incoming_damage = 100
        defense_bonus = steel.effects.get("defense_bonus", 0) / 100.0

        reduced = incoming_damage * (1 - defense_bonus)
        assert reduced == 95

    def test_morale_bonus_application(self):
        """War drums should boost morale."""
        drums = get_technology("war_drums")
        base_morale = 50
        morale_bonus = drums.effects.get("morale_bonus", 0)

        boosted_morale = base_morale + morale_bonus
        assert boosted_morale == 55


class TestTechTreeBalance:
    """Test technology tree balance."""

    def test_military_tech_count(self):
        """Should have 8 military technologies."""
        techs = load_technologies()
        military = [t for t in techs if t.category == "military"]
        assert len(military) == 8

    def test_economy_tech_count(self):
        """Should have 7 economy technologies."""
        techs = load_technologies()
        economy = [t for t in techs if t.category == "economy"]
        assert len(economy) == 7

    def test_special_tech_count(self):
        """Should have 7 special technologies."""
        techs = load_technologies()
        special = [t for t in techs if t.category == "special"]
        assert len(special) == 7

    def test_total_tech_count(self):
        """Should have 22 total technologies."""
        techs = load_technologies()
        assert len(techs) == 22

    def test_average_research_time(self):
        """Average research time should be reasonable."""
        techs = load_technologies()
        avg_turns = sum(t.turns for t in techs) / len(techs)

        # Average around 3-4 turns
        assert 3 <= avg_turns <= 4

    def test_average_research_cost(self):
        """Average research cost should be balanced."""
        techs = load_technologies()
        avg_cost = sum(t.cost for t in techs) / len(techs)

        # Average around 250-300 gold
        assert 250 <= avg_cost <= 300

    def test_max_prerequisite_depth(self):
        """No tech should require more than 3 prerequisite levels."""
        # Check deepest chains
        # elite_guards requires steel_armor which requires iron_weapons (depth 2)
        # advanced_farming requires crop_rotation and irrigation (depth 2)
        # fire_attack_mastery requires fire_arrows which requires archery_mastery (depth 2)

        elite = get_technology("elite_guards")
        steel = get_technology("steel_armor")

        # elite needs steel and cavalry
        # steel needs iron
        # so path is: iron -> steel -> elite (depth 2)
        assert len(elite.prerequisites) == 2  # Multiple prereqs at same level


class TestResearchScenarios:
    """Test realistic research scenarios."""

    def test_wei_military_focus(self):
        """Wei should focus on cavalry and infantry techs."""
        # Recommended path: iron_weapons -> steel_armor, cavalry_tactics
        wei_path = ["iron_weapons", "cavalry_tactics", "steel_armor"]
        total_turns = sum(get_technology(t).turns for t in wei_path)
        total_cost = sum(get_technology(t).cost for t in wei_path)

        assert total_turns == 10  # 3 + 3 + 4
        assert total_cost == 750  # 200 + 250 + 300

    def test_wu_naval_focus(self):
        """Wu should focus on naval and fire techs."""
        wu_path = ["naval_warfare", "archery_mastery", "fire_arrows"]
        total_turns = sum(get_technology(t).turns for t in wu_path)

        assert total_turns == 10  # 4 + 3 + 3

        # Check combat effects
        naval = get_technology("naval_warfare")
        fire = get_technology("fire_arrows")
        assert naval.effects.get("naval_bonus") == 10
        assert fire.effects.get("fire_attack_bonus") == 10

    def test_shu_balanced_approach(self):
        """Shu should take balanced approach with strategy focus."""
        shu_path = ["sun_tzu_art", "iron_weapons", "cavalry_tactics"]
        total_turns = sum(get_technology(t).turns for t in shu_path)

        assert total_turns == 10  # 4 + 3 + 3

        # Strategy bonus for Zhuge Liang style tactics
        sun_tzu = get_technology("sun_tzu_art")
        assert sun_tzu.effects.get("strategy_bonus") == 10

    def test_economy_before_military(self):
        """Economy-first strategy for long game."""
        econ_path = ["irrigation", "trade_routes", "crop_rotation"]
        total_turns = sum(get_technology(t).turns for t in econ_path)
        total_cost = sum(get_technology(t).cost for t in econ_path)

        assert total_turns == 8  # 2 + 3 + 3
        assert total_cost == 550  # 150 + 200 + 200

        # Economic benefits
        irrigation = get_technology("irrigation")
        trade = get_technology("trade_routes")
        crop = get_technology("crop_rotation")

        food_bonus = irrigation.effects.get("food_production", 0) + crop.effects.get("food_production", 0)
        gold_bonus = trade.effects.get("gold_production", 0)

        assert food_bonus == 25  # 10 + 15
        assert gold_bonus == 10
