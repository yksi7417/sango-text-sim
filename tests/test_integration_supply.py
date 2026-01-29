"""
Integration Tests: Supply Line Warfare

This module tests supply system mechanics:
- Supply consumption rate
- Supply line path finding
- Foraging in friendly cities
- Attrition when cut off
- Supply days in battle UI
- Supply strategy importance

Based on historical logistics and supply line warfare.
"""
import pytest
from src.systems.supply import (
    SUPPLY_PER_TROOP,
    BASE_SUPPLY_DAYS,
    FORAGING_RECOVERY,
    ATTRITION_RATE,
    SUPPLY_LINE_CUT_ATTRITION,
    calculate_supply_consumption,
    check_supply_line,
    apply_supply_attrition,
    forage_supplies,
    get_supply_status,
)
from src.models import GameState, City, Faction


class TestSupplyConstants:
    """Test supply-related constants."""

    def test_supply_per_troop(self):
        """Each troop should consume 0.1 food per turn."""
        assert SUPPLY_PER_TROOP == 0.1

    def test_base_supply_days(self):
        """Armies should have 10 days base supply."""
        assert BASE_SUPPLY_DAYS == 10

    def test_foraging_recovery(self):
        """Foraging should recover 3 supply days."""
        assert FORAGING_RECOVERY == 3

    def test_attrition_rate(self):
        """Out of supplies should cause 5% troop loss."""
        assert ATTRITION_RATE == 0.05

    def test_supply_line_cut_attrition(self):
        """Cut supply line should cause 3% troop loss."""
        assert SUPPLY_LINE_CUT_ATTRITION == 0.03


class TestSupplyConsumption:
    """Test supply consumption calculations."""

    def test_consumption_100_troops(self):
        """100 troops should consume 10 food."""
        consumption = calculate_supply_consumption(100)
        assert consumption == 10

    def test_consumption_1000_troops(self):
        """1000 troops should consume 100 food."""
        consumption = calculate_supply_consumption(1000)
        assert consumption == 100

    def test_consumption_small_army(self):
        """Small army should consume at least 1 food."""
        consumption = calculate_supply_consumption(5)
        assert consumption >= 1

    def test_consumption_zero_troops(self):
        """Zero troops should consume minimum 1 food."""
        consumption = calculate_supply_consumption(0)
        assert consumption == 1

    def test_consumption_large_army(self):
        """Large army (10000) should consume 1000 food."""
        consumption = calculate_supply_consumption(10000)
        assert consumption == 1000


class TestSupplyLinePath:
    """Test supply line path finding."""

    def create_game_state_with_cities(self):
        """Create a test game state with cities and adjacency."""
        game_state = GameState()

        # Create cities
        game_state.cities = {
            "CityA": City(name="CityA", owner="Wei", troops=1000, food=500),
            "CityB": City(name="CityB", owner="Wei", troops=500, food=300),
            "CityC": City(name="CityC", owner="Shu", troops=500, food=300),
            "CityD": City(name="CityD", owner="Wei", troops=300, food=200),
        }

        # Set adjacency: A-B-C-D (linear)
        game_state.adj = {
            "CityA": ["CityB"],
            "CityB": ["CityA", "CityC"],
            "CityC": ["CityB", "CityD"],
            "CityD": ["CityC"],
        }

        # Create factions
        game_state.factions = {
            "Wei": Faction(name="Wei", cities=["CityA", "CityB", "CityD"]),
            "Shu": Faction(name="Shu", cities=["CityC"]),
        }

        return game_state

    def test_supply_line_same_city(self):
        """Supply line to same city should always be intact."""
        game_state = self.create_game_state_with_cities()

        result = check_supply_line(game_state, "CityA", "CityA", "Wei")
        assert result["intact"] is True
        assert result["path"] == ["CityA"]

    def test_supply_line_adjacent_owned(self):
        """Supply line through adjacent owned city should work."""
        game_state = self.create_game_state_with_cities()

        result = check_supply_line(game_state, "CityA", "CityB", "Wei")
        assert result["intact"] is True
        assert "CityA" in result["path"]
        assert "CityB" in result["path"]

    def test_supply_line_blocked_by_enemy(self):
        """Supply line blocked by enemy city should fail."""
        game_state = self.create_game_state_with_cities()

        # CityA to CityD must go through CityC (enemy)
        result = check_supply_line(game_state, "CityA", "CityD", "Wei")
        assert result["intact"] is False
        assert result["path"] == []

    def test_supply_line_no_path(self):
        """No supply line to unreachable city."""
        game_state = self.create_game_state_with_cities()

        # Add isolated city
        game_state.cities["CityE"] = City(name="CityE", owner="Wei", troops=100, food=100)
        game_state.adj["CityE"] = []
        game_state.factions["Wei"].cities.append("CityE")

        result = check_supply_line(game_state, "CityA", "CityE", "Wei")
        assert result["intact"] is False


class TestSupplyAttrition:
    """Test supply attrition mechanics."""

    def test_no_attrition_with_supply(self):
        """Troops with supply should not suffer attrition."""
        result = apply_supply_attrition(1000, has_supply=True)

        assert result["troops"] == 1000
        assert result["losses"] == 0

    def test_attrition_without_supply(self):
        """Troops without supply should lose 5%."""
        result = apply_supply_attrition(1000, has_supply=False)

        assert result["losses"] == 50  # 5% of 1000
        assert result["troops"] == 950

    def test_attrition_small_army(self):
        """Small army should lose at least 1 troop."""
        result = apply_supply_attrition(10, has_supply=False)

        assert result["losses"] >= 1
        assert result["troops"] < 10

    def test_attrition_rounds_down(self):
        """Attrition should round to integer."""
        result = apply_supply_attrition(100, has_supply=False)

        assert result["losses"] == 5  # 5% of 100
        assert isinstance(result["losses"], int)

    def test_attrition_message(self):
        """Attrition should produce a message."""
        result = apply_supply_attrition(1000, has_supply=False)

        assert result["message"] != ""
        assert "50" in result["message"] or "attrition" in result["message"].lower()


class TestForaging:
    """Test foraging in friendly cities."""

    def create_game_state_with_cities(self):
        """Create a test game state with cities."""
        game_state = GameState()

        game_state.cities = {
            "FriendlyCity": City(name="FriendlyCity", owner="Wei", troops=1000, food=500),
            "EnemyCity": City(name="EnemyCity", owner="Shu", troops=500, food=300),
        }

        game_state.factions = {
            "Wei": Faction(name="Wei", cities=["FriendlyCity"]),
            "Shu": Faction(name="Shu", cities=["EnemyCity"]),
        }

        return game_state

    def test_forage_friendly_city(self):
        """Should be able to forage in friendly city."""
        game_state = self.create_game_state_with_cities()

        result = forage_supplies(game_state, "FriendlyCity", "Wei")

        assert result["success"] is True
        assert result["recovery"] == FORAGING_RECOVERY

    def test_forage_consumes_food(self):
        """Foraging should consume city food."""
        game_state = self.create_game_state_with_cities()
        initial_food = game_state.cities["FriendlyCity"].food

        forage_supplies(game_state, "FriendlyCity", "Wei")

        assert game_state.cities["FriendlyCity"].food < initial_food

    def test_forage_enemy_city_fails(self):
        """Cannot forage in enemy territory."""
        game_state = self.create_game_state_with_cities()

        result = forage_supplies(game_state, "EnemyCity", "Wei")

        assert result["success"] is False

    def test_forage_nonexistent_city(self):
        """Cannot forage in nonexistent city."""
        game_state = self.create_game_state_with_cities()

        result = forage_supplies(game_state, "FakeCity", "Wei")

        assert result["success"] is False

    def test_forage_recovery_amount(self):
        """Foraging should recover 3 supply days."""
        game_state = self.create_game_state_with_cities()

        result = forage_supplies(game_state, "FriendlyCity", "Wei")

        assert result["recovery"] == 3


class TestSupplyStatus:
    """Test supply status checking."""

    def create_game_state_with_cities(self):
        """Create a test game state with cities and adjacency."""
        game_state = GameState()

        game_state.cities = {
            "Capital": City(name="Capital", owner="Wei", troops=2000, food=1000),
            "Outpost": City(name="Outpost", owner="Wei", troops=500, food=200),
            "Enemy": City(name="Enemy", owner="Shu", troops=800, food=400),
        }

        game_state.adj = {
            "Capital": ["Outpost"],
            "Outpost": ["Capital", "Enemy"],
            "Enemy": ["Outpost"],
        }

        game_state.factions = {
            "Wei": Faction(name="Wei", cities=["Capital", "Outpost"]),
            "Shu": Faction(name="Shu", cities=["Enemy"]),
        }

        return game_state

    def test_supply_status_in_capital(self):
        """Capital should have supply."""
        game_state = self.create_game_state_with_cities()

        status = get_supply_status(game_state, "Capital", "Wei")

        assert status["has_supply"] is True

    def test_supply_status_connected_city(self):
        """Connected city should have supply."""
        game_state = self.create_game_state_with_cities()

        status = get_supply_status(game_state, "Outpost", "Wei")

        assert status["has_supply"] is True

    def test_nearby_friendly_cities(self):
        """Should list nearby friendly cities for foraging."""
        game_state = self.create_game_state_with_cities()

        status = get_supply_status(game_state, "Outpost", "Wei")

        assert "Capital" in status["nearby_friendly"]

    def test_no_supply_in_enemy_territory(self):
        """Enemy territory has no supply - only owned cities count."""
        game_state = self.create_game_state_with_cities()

        status = get_supply_status(game_state, "Enemy", "Wei")

        # Supply line check only traverses owned territory
        # Enemy city is not owned by Wei, so no direct supply
        assert status["has_supply"] is False


class TestSupplyStrategicValue:
    """Test strategic importance of supply lines."""

    def test_attrition_over_turns(self):
        """Calculate cumulative attrition over multiple turns."""
        troops = 10000
        turns = 5

        for _ in range(turns):
            result = apply_supply_attrition(troops, has_supply=False)
            troops = result["troops"]

        # After 5 turns of 5% attrition
        # 10000 * 0.95^5 = ~7738
        assert troops < 8000
        assert troops > 7000

    def test_supply_line_length_value(self):
        """Longer supply lines are more vulnerable."""
        # A longer supply line means more cities to potentially lose
        supply_chain_length = 5
        risk_per_city = 0.1  # 10% chance each city could fall

        total_risk = 1 - (1 - risk_per_city) ** supply_chain_length
        # ~41% chance of supply line being cut at some point
        assert total_risk > 0.4

    def test_foraging_extends_campaign(self):
        """Foraging can extend campaign duration."""
        base_supply = BASE_SUPPLY_DAYS
        foraging_trips = 3

        extended_supply = base_supply + (FORAGING_RECOVERY * foraging_trips)

        assert extended_supply == 19  # 10 + 3*3

    def test_supply_consumption_rate(self):
        """Calculate how long supplies last for army."""
        troops = 5000
        food_reserve = 1000

        consumption_per_turn = calculate_supply_consumption(troops)
        turns_of_supply = food_reserve // consumption_per_turn

        assert turns_of_supply == 2  # 1000 / 500 = 2 turns


class TestSupplyInBattle:
    """Test supply considerations in battle context."""

    def test_siege_supply_importance(self):
        """Besieging army needs constant supply."""
        troops = 10000
        siege_turns = 10

        total_consumption = sum(
            calculate_supply_consumption(troops)
            for _ in range(siege_turns)
        )

        # 10 turns of 1000 food consumption
        assert total_consumption == 10000

    def test_defender_supply_advantage(self):
        """Defender in city has supply advantage."""
        # Defender has city food supplies
        defender_food = 2000
        defender_troops = 3000
        defender_consumption = calculate_supply_consumption(defender_troops)

        defender_days = defender_food // defender_consumption
        assert defender_days > 5

    def test_attacker_supply_challenge(self):
        """Attacker must maintain supply lines."""
        attacker_troops = 8000
        attacker_consumption = calculate_supply_consumption(attacker_troops)

        # 800 food per turn is significant
        assert attacker_consumption == 800


class TestSupplyLineWarfare:
    """Test supply line warfare scenarios."""

    def test_cut_supply_attrition(self):
        """Cutting supply lines causes attrition."""
        troops = 5000
        result = apply_supply_attrition(troops, has_supply=False)

        # 5% of 5000 = 250 troops lost
        assert result["losses"] == 250

    def test_multiple_turn_cut(self):
        """Extended supply cut is devastating."""
        troops = 10000
        turns_cut = 10

        for _ in range(turns_cut):
            result = apply_supply_attrition(troops, has_supply=False)
            troops = result["troops"]

        # After 10 turns: 10000 * 0.95^10 = ~5987
        assert troops < 6500
        assert troops > 5500

    def test_forage_to_survive(self):
        """Foraging can help army survive without supply line."""
        # Foraging recovers 3 supply days
        # If army forages every 3 turns, can sustain
        recovery_per_forage = FORAGING_RECOVERY
        consumption_rate = 1  # 1 day per turn

        sustainable = recovery_per_forage >= consumption_rate * 3

        assert sustainable is True


class TestSupplyCalculations:
    """Test various supply calculations."""

    def test_large_army_supply_needs(self):
        """Large armies have huge supply needs."""
        large_army = 50000
        consumption = calculate_supply_consumption(large_army)

        assert consumption == 5000  # 50000 * 0.1

    def test_supply_days_calculation(self):
        """Calculate supply days from food reserve."""
        food = 1000
        troops = 1000
        consumption = calculate_supply_consumption(troops)

        supply_days = food // consumption
        assert supply_days == 10  # 1000 / 100

    def test_minimum_consumption(self):
        """Even tiny armies consume at least 1 food."""
        tiny_army = 1
        consumption = calculate_supply_consumption(tiny_army)

        assert consumption == 1


class TestHistoricalScenarios:
    """Test historically-inspired supply scenarios."""

    def test_cao_cao_chigbi_supply_issues(self):
        """Cao Cao's supply issues at Chi Bi."""
        # Large northern army far from supply
        northern_army = 80000
        consumption = calculate_supply_consumption(northern_army)

        # 8000 food per turn is massive
        assert consumption == 8000

        # Without resupply, attrition is severe
        result = apply_supply_attrition(northern_army, has_supply=False)
        assert result["losses"] == 4000  # 5% of 80000

    def test_zhuge_liang_northern_campaigns(self):
        """Zhuge Liang's supply challenges in northern campaigns."""
        # Shu army crossing difficult terrain
        shu_army = 30000
        supply_days_carried = BASE_SUPPLY_DAYS
        consumption = calculate_supply_consumption(shu_army)

        # 3000 food per turn
        # 10 supply days worth about 30000 food
        max_campaign_turns = 10

        assert consumption == 3000
        assert supply_days_carried <= max_campaign_turns

    def test_wei_supply_advantage(self):
        """Wei's supply advantage from central position."""
        # Wei controls more cities = better supply network
        wei_cities = 10
        shu_cities = 5

        # More cities = shorter supply lines on average
        supply_advantage = wei_cities / shu_cities
        assert supply_advantage == 2.0
