"""
Integration Tests: Building Construction ROI

This module tests building system mechanics:
- Building construction progress
- Building bonus application
- Construction cost/time
- Optimal build priority
- Building synergies

Based on 3KYuYun's economic efficiency analysis for ROTK11.
"""
import pytest
from src.buildings import load_buildings, get_building, get_available_buildings
from src.models import Building


class TestBuildingLoading:
    """Test building data loading."""

    def test_load_buildings_returns_list(self):
        """Loading buildings should return a list."""
        buildings = load_buildings()
        assert isinstance(buildings, list)
        assert len(buildings) > 0

    def test_all_buildings_have_required_fields(self):
        """All buildings should have required fields."""
        buildings = load_buildings()
        for building in buildings:
            assert building.id
            assert building.name_key
            assert building.cost >= 0
            assert building.turns >= 0

    def test_get_building_by_id(self):
        """Should retrieve specific building by ID."""
        building = get_building("barracks")
        assert building is not None
        assert building.id == "barracks"

    def test_get_building_invalid_id(self):
        """Should return None for invalid building ID."""
        building = get_building("nonexistent_building")
        assert building is None

    def test_total_building_count(self):
        """Should have 10 buildings available."""
        buildings = load_buildings()
        assert len(buildings) == 10


class TestBuildingConstruction:
    """Test building construction progress."""

    def test_barracks_construction_time(self):
        """Barracks should take 3 turns to build."""
        building = get_building("barracks")
        assert building.turns == 3

    def test_granary_quick_construction(self):
        """Granary should be quick to build (2 turns)."""
        building = get_building("granary")
        assert building.turns == 2

    def test_academy_long_construction(self):
        """Academy should take longer (4 turns)."""
        building = get_building("academy")
        assert building.turns == 4

    def test_construction_progress_simulation(self):
        """Simulate construction progress over turns."""
        building = get_building("barracks")
        turns_needed = building.turns

        progress = 0
        turns_spent = 0
        while progress < turns_needed:
            progress += 1
            turns_spent += 1

        assert turns_spent == 3
        assert progress >= turns_needed

    def test_watchtower_fastest_construction(self):
        """Watchtower should be one of the fastest (2 turns)."""
        watchtower = get_building("watchtower")
        assert watchtower.turns == 2

    def test_walls_upgrade_longest(self):
        """Walls upgrade takes longest (4 turns)."""
        walls = get_building("walls_upgrade")
        assert walls.turns == 4


class TestBuildingCosts:
    """Test building construction costs."""

    def test_barracks_cost(self):
        """Barracks should cost 200 gold."""
        building = get_building("barracks")
        assert building.cost == 200

    def test_market_cost(self):
        """Market should cost 250 gold."""
        building = get_building("market")
        assert building.cost == 250

    def test_granary_cost(self):
        """Granary should cost 180 gold."""
        building = get_building("granary")
        assert building.cost == 180

    def test_academy_cost(self):
        """Academy should cost 300 gold."""
        building = get_building("academy")
        assert building.cost == 300

    def test_walls_upgrade_most_expensive(self):
        """Walls upgrade should be most expensive at 350."""
        walls = get_building("walls_upgrade")
        buildings = load_buildings()

        assert walls.cost == 350
        assert all(b.cost <= walls.cost for b in buildings)

    def test_watchtower_cheapest(self):
        """Watchtower should be cheapest at 150."""
        watchtower = get_building("watchtower")
        buildings = load_buildings()

        assert watchtower.cost == 150
        assert all(b.cost >= watchtower.cost for b in buildings)


class TestBuildingEffects:
    """Test building bonus application."""

    def test_barracks_train_speed(self):
        """Barracks should boost training speed by 5%."""
        building = get_building("barracks")
        assert building.effects.get("train_speed") == 5

    def test_market_commerce_income(self):
        """Market should boost commerce income by 10%."""
        building = get_building("market")
        assert building.effects.get("commerce_income") == 10

    def test_granary_food_storage(self):
        """Granary should increase food storage by 200."""
        building = get_building("granary")
        assert building.effects.get("food_storage") == 200

    def test_academy_research_speed(self):
        """Academy should boost research speed by 5%."""
        building = get_building("academy")
        assert building.effects.get("research_speed") == 5

    def test_forge_weapon_bonus(self):
        """Forge should boost weapon strength by 5%."""
        building = get_building("forge")
        assert building.effects.get("weapon_bonus") == 5

    def test_walls_upgrade_defense(self):
        """Walls upgrade should boost walls by 10."""
        building = get_building("walls_upgrade")
        assert building.effects.get("walls_bonus") == 10

    def test_stable_cavalry_training(self):
        """Stable should boost cavalry training by 5%."""
        building = get_building("stable")
        assert building.effects.get("cavalry_train") == 5

    def test_watchtower_defense(self):
        """Watchtower should boost defense by 5%."""
        building = get_building("watchtower")
        assert building.effects.get("defense_bonus") == 5

    def test_temple_morale(self):
        """Temple should boost morale by 5."""
        building = get_building("temple")
        assert building.effects.get("morale_bonus") == 5

    def test_hospital_recovery(self):
        """Hospital should boost recovery by 10%."""
        building = get_building("hospital")
        assert building.effects.get("recovery_bonus") == 10


class TestAvailableBuildings:
    """Test available building detection."""

    def test_no_buildings_all_available(self):
        """With no buildings, all should be available."""
        available = get_available_buildings([])
        assert len(available) == 10

    def test_one_building_excludes_it(self):
        """Built buildings should be excluded."""
        available = get_available_buildings(["barracks"])
        available_ids = [b.id for b in available]

        assert "barracks" not in available_ids
        assert len(available) == 9

    def test_multiple_buildings_excluded(self):
        """Multiple built buildings should be excluded."""
        built = ["barracks", "market", "granary"]
        available = get_available_buildings(built)
        available_ids = [b.id for b in available]

        for b in built:
            assert b not in available_ids
        assert len(available) == 7

    def test_all_buildings_built(self):
        """No available buildings when all are built."""
        all_ids = [b.id for b in load_buildings()]
        available = get_available_buildings(all_ids)

        assert len(available) == 0


class TestBuildingROI:
    """Test building return on investment calculations."""

    def test_market_roi_calculation(self):
        """Calculate market's return on investment."""
        market = get_building("market")
        cost = market.cost  # 250
        income_bonus = market.effects.get("commerce_income", 0)  # 10%

        # Assume base commerce income of 50 per turn
        base_income = 50
        bonus_income = base_income * income_bonus / 100  # 5 per turn

        # ROI turns = cost / bonus income
        roi_turns = cost / bonus_income if bonus_income > 0 else float('inf')

        assert roi_turns == 50  # Takes 50 turns to pay for itself

    def test_granary_immediate_value(self):
        """Granary provides immediate storage value."""
        granary = get_building("granary")
        cost = granary.cost  # 180
        storage = granary.effects.get("food_storage", 0)  # 200

        # Storage value is immediate
        immediate_value = storage
        assert immediate_value > cost  # More value than cost

    def test_watchtower_cost_efficiency(self):
        """Watchtower is cost-efficient for defense."""
        watchtower = get_building("watchtower")
        walls = get_building("walls_upgrade")

        # Watchtower: 150 cost, 5 defense
        wt_efficiency = watchtower.effects.get("defense_bonus", 0) / watchtower.cost

        # Walls: 350 cost, 10 walls
        walls_efficiency = walls.effects.get("walls_bonus", 0) / walls.cost

        # Watchtower is more cost efficient
        assert wt_efficiency > walls_efficiency

    def test_barracks_vs_stable_efficiency(self):
        """Compare barracks vs stable training efficiency."""
        barracks = get_building("barracks")
        stable = get_building("stable")

        barracks_eff = barracks.effects.get("train_speed", 0) / barracks.cost
        stable_eff = stable.effects.get("cavalry_train", 0) / stable.cost

        # Both provide 5% bonus
        assert barracks.effects.get("train_speed") == stable.effects.get("cavalry_train")
        # But barracks is slightly more cost efficient
        assert barracks_eff > stable_eff


class TestOptimalBuildPriority:
    """Test optimal build order strategies."""

    def test_economy_first_priority(self):
        """Economy-first strategy: market -> granary."""
        market = get_building("market")
        granary = get_building("granary")

        # Market provides income, granary provides storage
        assert market.effects.get("commerce_income") == 10
        assert granary.effects.get("food_storage") == 200

        # Granary is faster and cheaper
        assert granary.turns < market.turns
        assert granary.cost < market.cost

    def test_military_priority(self):
        """Military priority: barracks -> forge -> stable."""
        barracks = get_building("barracks")
        forge = get_building("forge")
        stable = get_building("stable")

        # All military buildings for troop improvement
        assert barracks.effects.get("train_speed") == 5
        assert forge.effects.get("weapon_bonus") == 5
        assert stable.effects.get("cavalry_train") == 5

    def test_defense_priority(self):
        """Defense priority: watchtower -> walls_upgrade."""
        watchtower = get_building("watchtower")
        walls = get_building("walls_upgrade")

        # Quick defense from watchtower
        assert watchtower.turns == 2
        # Stronger defense from walls
        assert walls.effects.get("walls_bonus") == 10

    def test_research_priority(self):
        """Research priority: academy first for tech bonuses."""
        academy = get_building("academy")

        assert academy.effects.get("research_speed") == 5
        # Academy is most expensive after walls
        assert academy.cost == 300

    def test_recovery_priority(self):
        """Hospital priority for sustained warfare."""
        hospital = get_building("hospital")

        assert hospital.effects.get("recovery_bonus") == 10
        # Good for long campaigns

    def test_quick_build_priority(self):
        """Quick builds: granary, watchtower (2 turns each)."""
        buildings = load_buildings()
        quick_builds = [b for b in buildings if b.turns == 2]

        assert len(quick_builds) == 2
        quick_ids = [b.id for b in quick_builds]
        assert "granary" in quick_ids
        assert "watchtower" in quick_ids


class TestBuildingSynergies:
    """Test building synergies."""

    def test_barracks_forge_synergy(self):
        """Barracks + Forge synergy for troop quality."""
        barracks = get_building("barracks")
        forge = get_building("forge")

        # Combined training speed + weapon bonus
        train_bonus = barracks.effects.get("train_speed", 0)
        weapon_bonus = forge.effects.get("weapon_bonus", 0)

        combined_military = train_bonus + weapon_bonus
        assert combined_military == 10

    def test_stable_forge_cavalry_synergy(self):
        """Stable + Forge synergy for cavalry quality."""
        stable = get_building("stable")
        forge = get_building("forge")

        cavalry_bonus = stable.effects.get("cavalry_train", 0)
        weapon_bonus = forge.effects.get("weapon_bonus", 0)

        assert cavalry_bonus + weapon_bonus == 10

    def test_defense_synergy(self):
        """Watchtower + Walls synergy for strong defense."""
        watchtower = get_building("watchtower")
        walls = get_building("walls_upgrade")

        defense_bonus = watchtower.effects.get("defense_bonus", 0)
        walls_bonus = walls.effects.get("walls_bonus", 0)

        # Combined defense power
        total_defense = defense_bonus + walls_bonus
        assert total_defense == 15

    def test_economy_synergy(self):
        """Market + Granary synergy for economic stability."""
        market = get_building("market")
        granary = get_building("granary")

        commerce = market.effects.get("commerce_income", 0)
        storage = granary.effects.get("food_storage", 0)

        # Gold income + food buffer
        assert commerce == 10
        assert storage == 200

    def test_hospital_temple_morale_synergy(self):
        """Hospital + Temple synergy for troop welfare."""
        hospital = get_building("hospital")
        temple = get_building("temple")

        recovery = hospital.effects.get("recovery_bonus", 0)
        morale = temple.effects.get("morale_bonus", 0)

        # Troop welfare combination
        total_welfare = recovery + morale
        assert total_welfare == 15


class TestBuildingEffectApplication:
    """Test building effect application to city stats."""

    def test_market_commerce_application(self):
        """Apply market bonus to commerce income."""
        market = get_building("market")
        base_commerce = 50
        bonus_percent = market.effects.get("commerce_income", 0)

        boosted_commerce = base_commerce * (1 + bonus_percent / 100)
        assert boosted_commerce == pytest.approx(55)

    def test_barracks_training_application(self):
        """Apply barracks bonus to training speed."""
        barracks = get_building("barracks")
        base_train_rate = 100  # troops per turn
        bonus_percent = barracks.effects.get("train_speed", 0)

        boosted_train = base_train_rate * (1 + bonus_percent / 100)
        assert boosted_train == pytest.approx(105)

    def test_forge_attack_application(self):
        """Apply forge bonus to attack power."""
        forge = get_building("forge")
        base_attack = 100
        bonus_percent = forge.effects.get("weapon_bonus", 0)

        boosted_attack = base_attack * (1 + bonus_percent / 100)
        assert boosted_attack == pytest.approx(105)

    def test_watchtower_defense_application(self):
        """Apply watchtower bonus to defense."""
        watchtower = get_building("watchtower")
        base_defense = 100
        bonus_percent = watchtower.effects.get("defense_bonus", 0)

        boosted_defense = base_defense * (1 + bonus_percent / 100)
        assert boosted_defense == pytest.approx(105)

    def test_temple_morale_application(self):
        """Apply temple bonus to morale."""
        temple = get_building("temple")
        base_morale = 50
        morale_bonus = temple.effects.get("morale_bonus", 0)

        boosted_morale = base_morale + morale_bonus
        assert boosted_morale == 55


class TestBuildingCategories:
    """Test building categorization."""

    def test_military_buildings(self):
        """Identify military buildings."""
        military = ["barracks", "forge", "stable"]
        for bid in military:
            building = get_building(bid)
            assert building is not None
            # All have military-related effects
            effects = building.effects
            assert any(k in effects for k in ["train_speed", "weapon_bonus", "cavalry_train"])

    def test_economy_buildings(self):
        """Identify economy buildings."""
        economy = ["market", "granary"]
        for bid in economy:
            building = get_building(bid)
            assert building is not None
            effects = building.effects
            assert any(k in effects for k in ["commerce_income", "food_storage"])

    def test_defense_buildings(self):
        """Identify defense buildings."""
        defense = ["watchtower", "walls_upgrade"]
        for bid in defense:
            building = get_building(bid)
            assert building is not None
            effects = building.effects
            assert any(k in effects for k in ["defense_bonus", "walls_bonus"])

    def test_support_buildings(self):
        """Identify support buildings."""
        support = ["academy", "temple", "hospital"]
        for bid in support:
            building = get_building(bid)
            assert building is not None


class TestBuildingStrategies:
    """Test faction-specific building strategies."""

    def test_wei_military_focus(self):
        """Wei should prioritize military buildings."""
        # Recommended: barracks, forge, stable for cavalry
        wei_priority = ["barracks", "forge", "stable"]
        total_cost = sum(get_building(b).cost for b in wei_priority)
        total_turns = sum(get_building(b).turns for b in wei_priority)

        assert total_cost == 700  # 200 + 280 + 220
        assert total_turns == 9  # 3 + 3 + 3

    def test_wu_economy_focus(self):
        """Wu should prioritize economy for navy funding."""
        wu_priority = ["market", "granary", "hospital"]
        total_cost = sum(get_building(b).cost for b in wu_priority)

        assert total_cost == 680  # 250 + 180 + 250

    def test_shu_balanced_focus(self):
        """Shu should take balanced approach."""
        shu_priority = ["academy", "temple", "barracks"]
        total_cost = sum(get_building(b).cost for b in shu_priority)

        assert total_cost == 700  # 300 + 200 + 200

    def test_defensive_city_strategy(self):
        """Defensive city should prioritize walls and watchtower."""
        defense_priority = ["watchtower", "walls_upgrade", "granary"]
        total_cost = sum(get_building(b).cost for b in defense_priority)
        total_turns = sum(get_building(b).turns for b in defense_priority)

        assert total_cost == 680  # 150 + 350 + 180
        assert total_turns == 8  # 2 + 4 + 2


class TestTotalBuildingStats:
    """Test aggregate building statistics."""

    def test_total_building_cost(self):
        """Calculate total cost to build everything."""
        buildings = load_buildings()
        total_cost = sum(b.cost for b in buildings)

        # 200+250+180+300+280+350+220+150+200+250 = 2380
        assert total_cost == 2380

    def test_total_building_turns(self):
        """Calculate total turns to build everything."""
        buildings = load_buildings()
        total_turns = sum(b.turns for b in buildings)

        # 3+3+2+4+3+4+3+2+3+3 = 30
        assert total_turns == 30

    def test_average_building_cost(self):
        """Calculate average building cost."""
        buildings = load_buildings()
        avg_cost = sum(b.cost for b in buildings) / len(buildings)

        assert avg_cost == 238  # 2380 / 10

    def test_average_building_turns(self):
        """Calculate average building construction time."""
        buildings = load_buildings()
        avg_turns = sum(b.turns for b in buildings) / len(buildings)

        assert avg_turns == 3.0  # 30 / 10

    def test_cost_per_turn_ratio(self):
        """Calculate cost per construction turn."""
        buildings = load_buildings()

        for b in buildings:
            cost_per_turn = b.cost / b.turns
            # Should be between 70-90 gold per turn on average
            assert 50 <= cost_per_turn <= 100
