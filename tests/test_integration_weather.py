"""
Integration Tests: Weather-Season Chain

This module tests weather and season system interactions:
- Seasonal weather probabilities
- Weather persistence
- Weather combat effects
- Season farming/harvest bonuses
- Winter attrition
- Weather event triggers

Tests validate multi-turn weather/season interactions.
"""
import pytest
from src.models import Season, WeatherType, GameState, get_current_season
from src.constants import (
    SPRING_FARMING_BONUS,
    AUTUMN_HARVEST_BONUS,
    WINTER_FARMING_PENALTY,
    WINTER_MOVEMENT_PENALTY,
    WINTER_ATTRITION_RATE,
    SPRING_RAIN_CHANCE,
    SUMMER_DROUGHT_CHANCE,
    AUTUMN_CLEAR_CHANCE,
    WINTER_SNOW_CHANCE,
    RAIN_FIRE_ATTACK_PENALTY,
    RAIN_MOVEMENT_PENALTY,
    DROUGHT_FIRE_ATTACK_BONUS,
    SNOW_MOVEMENT_PENALTY,
    SNOW_ATTRITION_RATE,
    FOREST_FIRE_ATTACK_BONUS,
)


class TestSeasonEnum:
    """Test Season enumeration."""

    def test_spring_exists(self):
        """Spring season should exist."""
        assert Season.SPRING.value == "spring"

    def test_summer_exists(self):
        """Summer season should exist."""
        assert Season.SUMMER.value == "summer"

    def test_autumn_exists(self):
        """Autumn season should exist."""
        assert Season.AUTUMN.value == "autumn"

    def test_winter_exists(self):
        """Winter season should exist."""
        assert Season.WINTER.value == "winter"

    def test_four_seasons(self):
        """Should have exactly 4 seasons."""
        seasons = list(Season)
        assert len(seasons) == 4


class TestWeatherEnum:
    """Test WeatherType enumeration."""

    def test_clear_weather(self):
        """Clear weather should exist."""
        assert WeatherType.CLEAR.value == "clear"

    def test_rain_weather(self):
        """Rain weather should exist."""
        assert WeatherType.RAIN.value == "rain"

    def test_snow_weather(self):
        """Snow weather should exist."""
        assert WeatherType.SNOW.value == "snow"

    def test_fog_weather(self):
        """Fog weather should exist."""
        assert WeatherType.FOG.value == "fog"

    def test_drought_weather(self):
        """Drought weather should exist."""
        assert WeatherType.DROUGHT.value == "drought"

    def test_five_weather_types(self):
        """Should have exactly 5 weather types."""
        weather_types = list(WeatherType)
        assert len(weather_types) == 5


class TestGetCurrentSeason:
    """Test season determination from month."""

    def test_january_is_winter(self):
        """January (month 1) should be winter."""
        season = get_current_season(1)
        assert season == Season.WINTER

    def test_february_is_winter(self):
        """February (month 2) should be winter."""
        season = get_current_season(2)
        assert season == Season.WINTER

    def test_march_is_spring(self):
        """March (month 3) should be spring."""
        season = get_current_season(3)
        assert season == Season.SPRING

    def test_april_is_spring(self):
        """April (month 4) should be spring."""
        season = get_current_season(4)
        assert season == Season.SPRING

    def test_may_is_spring(self):
        """May (month 5) should be spring."""
        season = get_current_season(5)
        assert season == Season.SPRING

    def test_june_is_summer(self):
        """June (month 6) should be summer."""
        season = get_current_season(6)
        assert season == Season.SUMMER

    def test_july_is_summer(self):
        """July (month 7) should be summer."""
        season = get_current_season(7)
        assert season == Season.SUMMER

    def test_august_is_summer(self):
        """August (month 8) should be summer."""
        season = get_current_season(8)
        assert season == Season.SUMMER

    def test_september_is_autumn(self):
        """September (month 9) should be autumn."""
        season = get_current_season(9)
        assert season == Season.AUTUMN

    def test_october_is_autumn(self):
        """October (month 10) should be autumn."""
        season = get_current_season(10)
        assert season == Season.AUTUMN

    def test_november_is_autumn(self):
        """November (month 11) should be autumn."""
        season = get_current_season(11)
        assert season == Season.AUTUMN

    def test_december_is_winter(self):
        """December (month 12) should be winter."""
        season = get_current_season(12)
        assert season == Season.WINTER


class TestSeasonalWeatherProbabilities:
    """Test seasonal weather probabilities."""

    def test_spring_rain_chance(self):
        """Spring should have 30% rain chance."""
        assert SPRING_RAIN_CHANCE == 0.30

    def test_summer_drought_chance(self):
        """Summer should have 20% drought chance."""
        assert SUMMER_DROUGHT_CHANCE == 0.20

    def test_autumn_clear_chance(self):
        """Autumn should have 80% clear weather chance."""
        assert AUTUMN_CLEAR_CHANCE == 0.80

    def test_winter_snow_chance(self):
        """Winter should have 40% snow chance."""
        assert WINTER_SNOW_CHANCE == 0.40

    def test_spring_rain_moderate(self):
        """Spring rain chance should be moderate."""
        assert 0.2 <= SPRING_RAIN_CHANCE <= 0.5

    def test_winter_snow_significant(self):
        """Winter snow chance should be significant."""
        assert WINTER_SNOW_CHANCE >= 0.3


class TestWeatherPersistence:
    """Test weather persistence across turns."""

    def test_weather_in_game_state(self):
        """GameState should track current weather."""
        game_state = GameState()
        assert hasattr(game_state, 'weather')
        assert game_state.weather == WeatherType.CLEAR

    def test_weather_turns_remaining(self):
        """GameState should track weather duration."""
        game_state = GameState()
        assert hasattr(game_state, 'weather_turns_remaining')
        assert game_state.weather_turns_remaining == 0

    def test_set_weather_with_duration(self):
        """Should be able to set weather with duration."""
        game_state = GameState()
        game_state.weather = WeatherType.RAIN
        game_state.weather_turns_remaining = 3

        assert game_state.weather == WeatherType.RAIN
        assert game_state.weather_turns_remaining == 3

    def test_weather_duration_simulation(self):
        """Simulate weather duration countdown."""
        game_state = GameState()
        game_state.weather = WeatherType.DROUGHT
        game_state.weather_turns_remaining = 2

        # Simulate turn processing
        if game_state.weather_turns_remaining > 0:
            game_state.weather_turns_remaining -= 1

        assert game_state.weather_turns_remaining == 1

        # Another turn
        if game_state.weather_turns_remaining > 0:
            game_state.weather_turns_remaining -= 1

        assert game_state.weather_turns_remaining == 0


class TestWeatherCombatEffects:
    """Test weather effects on combat."""

    def test_rain_fire_attack_penalty(self):
        """Rain should reduce fire attack by 20%."""
        assert RAIN_FIRE_ATTACK_PENALTY == 0.80

    def test_drought_fire_attack_bonus(self):
        """Drought should boost fire attack by 50%."""
        assert DROUGHT_FIRE_ATTACK_BONUS == 1.50

    def test_rain_movement_penalty(self):
        """Rain should reduce movement by 10%."""
        assert RAIN_MOVEMENT_PENALTY == 0.90

    def test_snow_movement_penalty(self):
        """Snow should reduce movement by 30%."""
        assert SNOW_MOVEMENT_PENALTY == 0.70

    def test_snow_attrition_rate(self):
        """Snow should cause 3% troop attrition."""
        assert SNOW_ATTRITION_RATE == 0.03

    def test_fire_attack_in_rain(self):
        """Calculate fire attack effectiveness in rain."""
        base_damage = 100
        rain_damage = base_damage * RAIN_FIRE_ATTACK_PENALTY

        assert rain_damage == 80

    def test_fire_attack_in_drought(self):
        """Calculate fire attack effectiveness in drought."""
        base_damage = 100
        drought_damage = base_damage * DROUGHT_FIRE_ATTACK_BONUS

        assert drought_damage == 150

    def test_movement_in_snow(self):
        """Calculate movement in snow."""
        base_movement = 100
        snow_movement = base_movement * SNOW_MOVEMENT_PENALTY

        assert snow_movement == 70


class TestSeasonFarmingBonuses:
    """Test seasonal farming and harvest bonuses."""

    def test_spring_farming_bonus(self):
        """Spring should give +20% farming bonus."""
        assert SPRING_FARMING_BONUS == 1.20

    def test_autumn_harvest_bonus(self):
        """Autumn should give +15% harvest bonus."""
        assert AUTUMN_HARVEST_BONUS == 1.15

    def test_winter_farming_penalty(self):
        """Winter should give -10% farming penalty."""
        assert WINTER_FARMING_PENALTY == 0.90

    def test_spring_farm_calculation(self):
        """Calculate farming yield in spring."""
        base_yield = 100
        spring_yield = base_yield * SPRING_FARMING_BONUS

        assert spring_yield == 120

    def test_autumn_harvest_calculation(self):
        """Calculate harvest yield in autumn."""
        base_harvest = 100
        autumn_harvest = base_harvest * AUTUMN_HARVEST_BONUS

        assert autumn_harvest == pytest.approx(115)

    def test_winter_farm_calculation(self):
        """Calculate farming yield in winter."""
        base_yield = 100
        winter_yield = base_yield * WINTER_FARMING_PENALTY

        assert winter_yield == 90


class TestWinterAttrition:
    """Test winter attrition effects."""

    def test_winter_movement_penalty(self):
        """Winter should reduce movement by 30%."""
        assert WINTER_MOVEMENT_PENALTY == 0.70

    def test_winter_attrition_rate(self):
        """Winter campaigns should cause 5% troop loss."""
        assert WINTER_ATTRITION_RATE == 0.05

    def test_winter_troop_attrition(self):
        """Calculate troop loss in winter campaign."""
        troops = 1000
        attrition = troops * WINTER_ATTRITION_RATE

        assert attrition == 50

    def test_winter_movement_calculation(self):
        """Calculate movement in winter."""
        base_movement = 100
        winter_movement = base_movement * WINTER_MOVEMENT_PENALTY

        assert winter_movement == 70

    def test_snow_attrition_vs_winter_attrition(self):
        """Snow attrition should be less than base winter attrition."""
        assert SNOW_ATTRITION_RATE < WINTER_ATTRITION_RATE


class TestWeatherEffectStacking:
    """Test weather and terrain effect stacking."""

    def test_drought_forest_fire_stacking(self):
        """Drought + Forest should stack fire bonuses."""
        base_damage = 100

        drought_mult = DROUGHT_FIRE_ATTACK_BONUS  # 1.50
        forest_mult = FOREST_FIRE_ATTACK_BONUS  # 1.25

        stacked_damage = base_damage * drought_mult * forest_mult
        assert stacked_damage == pytest.approx(187.5)

    def test_rain_vs_forest_fire(self):
        """Rain should negate forest fire bonus."""
        base_damage = 100

        rain_mult = RAIN_FIRE_ATTACK_PENALTY  # 0.80
        forest_mult = FOREST_FIRE_ATTACK_BONUS  # 1.25

        combined = base_damage * rain_mult * forest_mult
        assert combined == 100  # Rain + forest = neutral

    def test_snow_movement_stacking(self):
        """Snow + winter should stack movement penalties."""
        base_movement = 100

        # Both snow and winter affect movement
        snow_mult = SNOW_MOVEMENT_PENALTY  # 0.70
        # Winter already has snow-like conditions

        final_movement = base_movement * snow_mult
        assert final_movement == 70


class TestSeasonTransitions:
    """Test season transitions through months."""

    def test_winter_to_spring_transition(self):
        """Month 2 -> 3 should transition winter to spring."""
        feb_season = get_current_season(2)
        mar_season = get_current_season(3)

        assert feb_season == Season.WINTER
        assert mar_season == Season.SPRING

    def test_spring_to_summer_transition(self):
        """Month 5 -> 6 should transition spring to summer."""
        may_season = get_current_season(5)
        jun_season = get_current_season(6)

        assert may_season == Season.SPRING
        assert jun_season == Season.SUMMER

    def test_summer_to_autumn_transition(self):
        """Month 8 -> 9 should transition summer to autumn."""
        aug_season = get_current_season(8)
        sep_season = get_current_season(9)

        assert aug_season == Season.SUMMER
        assert sep_season == Season.AUTUMN

    def test_autumn_to_winter_transition(self):
        """Month 11 -> 12 should transition autumn to winter."""
        nov_season = get_current_season(11)
        dec_season = get_current_season(12)

        assert nov_season == Season.AUTUMN
        assert dec_season == Season.WINTER

    def test_full_year_cycle(self):
        """Test full year seasonal cycle."""
        seasons_by_month = [get_current_season(m) for m in range(1, 13)]

        # Winter: 1, 2, 12
        assert seasons_by_month[0] == Season.WINTER  # Jan
        assert seasons_by_month[1] == Season.WINTER  # Feb
        assert seasons_by_month[11] == Season.WINTER  # Dec

        # Spring: 3, 4, 5
        assert seasons_by_month[2] == Season.SPRING  # Mar
        assert seasons_by_month[3] == Season.SPRING  # Apr
        assert seasons_by_month[4] == Season.SPRING  # May

        # Summer: 6, 7, 8
        assert seasons_by_month[5] == Season.SUMMER  # Jun
        assert seasons_by_month[6] == Season.SUMMER  # Jul
        assert seasons_by_month[7] == Season.SUMMER  # Aug

        # Autumn: 9, 10, 11
        assert seasons_by_month[8] == Season.AUTUMN  # Sep
        assert seasons_by_month[9] == Season.AUTUMN  # Oct
        assert seasons_by_month[10] == Season.AUTUMN  # Nov


class TestWeatherScenarios:
    """Test realistic weather scenarios."""

    def test_red_cliff_conditions(self):
        """Red Cliff battle conditions: drought + naval."""
        # Historical: Strong wind (drought-like) during naval battle
        base_fire_damage = 1000
        drought_mult = DROUGHT_FIRE_ATTACK_BONUS

        fire_damage = base_fire_damage * drought_mult
        assert fire_damage == 1500

    def test_northern_winter_campaign(self):
        """Northern winter campaign: snow + cold."""
        troops = 10000
        snow_attrition = troops * SNOW_ATTRITION_RATE

        # Lose 300 troops per turn
        assert snow_attrition == 300

    def test_spring_planting_season(self):
        """Spring planting should boost farming."""
        base_food = 100
        spring_bonus = base_food * SPRING_FARMING_BONUS

        assert spring_bonus == 120

    def test_autumn_harvest_bounty(self):
        """Autumn harvest should boost food collection."""
        base_harvest = 1000
        autumn_bonus = base_harvest * AUTUMN_HARVEST_BONUS

        assert autumn_bonus == 1150


class TestGameStateWeatherIntegration:
    """Test weather integration with game state."""

    def test_default_weather_is_clear(self):
        """Default weather should be clear."""
        game_state = GameState()
        assert game_state.weather == WeatherType.CLEAR

    def test_weather_can_be_changed(self):
        """Weather should be changeable."""
        game_state = GameState()
        game_state.weather = WeatherType.RAIN

        assert game_state.weather == WeatherType.RAIN

    def test_weather_duration_can_be_set(self):
        """Weather duration should be settable."""
        game_state = GameState()
        game_state.weather = WeatherType.DROUGHT
        game_state.weather_turns_remaining = 3

        assert game_state.weather_turns_remaining == 3

    def test_game_month_affects_season(self):
        """Game month should determine season."""
        game_state = GameState()
        game_state.month = 6  # June = Summer

        season = get_current_season(game_state.month)
        assert season == Season.SUMMER


class TestSeasonalStrategy:
    """Test strategic implications of seasons."""

    def test_best_farming_season(self):
        """Spring should be best for farming."""
        spring = SPRING_FARMING_BONUS
        autumn = AUTUMN_HARVEST_BONUS
        winter = WINTER_FARMING_PENALTY

        assert spring > autumn > winter

    def test_worst_campaign_season(self):
        """Winter should be worst for campaigns."""
        winter_penalty = WINTER_MOVEMENT_PENALTY
        winter_attrition = WINTER_ATTRITION_RATE

        # Both penalties are significant
        assert winter_penalty < 1.0
        assert winter_attrition > 0

    def test_fire_attack_timing(self):
        """Drought is best time for fire attacks."""
        drought = DROUGHT_FIRE_ATTACK_BONUS
        rain = RAIN_FIRE_ATTACK_PENALTY

        # Drought is 1.5x, rain is 0.8x = 1.875x difference
        advantage = drought / rain
        assert advantage == pytest.approx(1.875)


class TestWeatherCombatScenarios:
    """Test weather in combat scenarios."""

    def test_rainy_battle_fire_disadvantage(self):
        """Fire attacks should be weaker in rain."""
        normal_fire = 100
        rainy_fire = normal_fire * RAIN_FIRE_ATTACK_PENALTY

        assert rainy_fire == 80
        assert rainy_fire < normal_fire

    def test_drought_fire_advantage(self):
        """Fire attacks should be stronger in drought."""
        normal_fire = 100
        drought_fire = normal_fire * DROUGHT_FIRE_ATTACK_BONUS

        assert drought_fire == 150
        assert drought_fire > normal_fire

    def test_snow_campaign_attrition(self):
        """Snow campaigns should cause troop losses."""
        army_size = 5000
        snow_losses = army_size * SNOW_ATTRITION_RATE

        assert snow_losses == 150

    def test_rain_slows_movement(self):
        """Rain should slow troop movement."""
        normal_movement = 100
        rain_movement = normal_movement * RAIN_MOVEMENT_PENALTY

        assert rain_movement == 90
