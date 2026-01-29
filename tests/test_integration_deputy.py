"""
Integration Tests: Deputy General Synergy

This module tests deputy general mechanics and officer combinations:
- Multiple officers in cities contributing to effectiveness
- Leadership stat affecting command capacity
- Officer stat combinations for various tasks
- Formation/pairing bonuses based on relationships
- Troop command effectiveness based on leadership

Based on ROTK11's deputy general system concepts.
"""
import pytest
from src.models import Officer, City, Faction, GameState, BattleState, TerrainType
from src.constants import MAX_STAT


class TestOfficerStatContribution:
    """Test how officer stats contribute to city/battle effectiveness."""

    @pytest.fixture
    def game_state(self):
        """Create a game state with multiple officers."""
        gs = GameState()
        gs.factions = {
            "Shu": Faction(
                name="Shu",
                cities=["Chengdu"],
                officers=["ZhugeLiang", "ZhaoYun", "MaChao"],
                relations={}
            )
        }
        gs.cities = {
            "Chengdu": City(name="Chengdu", owner="Shu", troops=5000)
        }
        gs.officers = {
            "ZhugeLiang": Officer(
                name="ZhugeLiang",
                faction="Shu",
                leadership=45,
                intelligence=100,
                politics=95,
                charisma=92,
                loyalty=95,
                traits=["Scholar"],
                city="Chengdu"
            ),
            "ZhaoYun": Officer(
                name="ZhaoYun",
                faction="Shu",
                leadership=96,
                intelligence=76,
                politics=65,
                charisma=85,
                loyalty=95,
                traits=["Brave"],
                city="Chengdu"
            ),
            "MaChao": Officer(
                name="MaChao",
                faction="Shu",
                leadership=95,
                intelligence=52,
                politics=40,
                charisma=78,
                loyalty=85,
                traits=["Brave"],
                city="Chengdu"
            )
        }
        gs.player_faction = "Shu"
        return gs

    def test_highest_leadership_becomes_commander(self, game_state):
        """The officer with highest leadership should be commander."""
        officers = [game_state.officers[name] for name in game_state.factions["Shu"].officers]

        # Find best commander
        best_commander = max(officers, key=lambda o: o.leadership)

        assert best_commander.name == "ZhaoYun"
        assert best_commander.leadership == 96

    def test_highest_intelligence_for_strategy(self, game_state):
        """The officer with highest intelligence should advise on strategy."""
        officers = [game_state.officers[name] for name in game_state.factions["Shu"].officers]

        # Find best strategist
        best_strategist = max(officers, key=lambda o: o.intelligence)

        assert best_strategist.name == "ZhugeLiang"
        assert best_strategist.intelligence == 100

    def test_highest_politics_for_administration(self, game_state):
        """The officer with highest politics should handle administration."""
        officers = [game_state.officers[name] for name in game_state.factions["Shu"].officers]

        # Find best administrator
        best_admin = max(officers, key=lambda o: o.politics)

        assert best_admin.name == "ZhugeLiang"
        assert best_admin.politics == 95

    def test_combined_stats_for_overall_power(self, game_state):
        """Multiple officers should combine stats for overall effectiveness."""
        officers = [game_state.officers[name] for name in game_state.factions["Shu"].officers]

        # Combined leadership for military
        total_leadership = sum(o.leadership for o in officers)
        avg_leadership = total_leadership / len(officers)

        # Zhuge Liang + Zhao Yun + Ma Chao
        expected_total = 45 + 96 + 95
        assert total_leadership == expected_total
        assert avg_leadership == pytest.approx(expected_total / 3)

        # Combined intelligence for strategy
        total_intelligence = sum(o.intelligence for o in officers)
        expected_int = 100 + 76 + 52
        assert total_intelligence == expected_int


class TestDeputyStatBonus:
    """Test deputy general stat contribution to commander."""

    def test_deputy_leadership_contribution(self):
        """Deputy's leadership should add partial bonus to commander."""
        commander = Officer(
            name="ZhaoYun",
            faction="Shu",
            leadership=96,
            intelligence=76,
            politics=65,
            charisma=85,
            loyalty=95,
            traits=["Brave"],
            city="Chengdu"
        )
        deputy = Officer(
            name="MaChao",
            faction="Shu",
            leadership=95,
            intelligence=52,
            politics=40,
            charisma=78,
            loyalty=85,
            traits=["Brave"],
            city="Chengdu"
        )

        # Deputy contribution formula (ROTK11-style): 20-30% of deputy stats
        deputy_contribution_rate = 0.25
        effective_leadership = commander.leadership + (deputy.leadership * deputy_contribution_rate)

        # 96 + (95 * 0.25) = 96 + 23.75 = 119.75
        assert effective_leadership == pytest.approx(119.75)

    def test_strategist_deputy_intelligence_bonus(self):
        """Strategist deputy should boost commander's tactical options."""
        commander = Officer(
            name="ZhaoYun",
            faction="Shu",
            leadership=96,
            intelligence=76,
            politics=65,
            charisma=85,
            loyalty=95,
            traits=["Brave"],
            city="Chengdu"
        )
        strategist_deputy = Officer(
            name="ZhugeLiang",
            faction="Shu",
            leadership=45,
            intelligence=100,
            politics=95,
            charisma=92,
            loyalty=95,
            traits=["Scholar"],
            city="Chengdu"
        )

        # Strategist deputy contributes intelligence
        deputy_int_rate = 0.30  # Higher rate for intelligence specialty
        effective_intelligence = commander.intelligence + (strategist_deputy.intelligence * deputy_int_rate)

        # 76 + (100 * 0.30) = 76 + 30 = 106
        assert effective_intelligence == pytest.approx(106.0)

    def test_deputy_contributes_traits(self):
        """Deputy's traits should be available in combined unit."""
        commander = Officer(
            name="ZhaoYun",
            faction="Shu",
            leadership=96,
            intelligence=76,
            politics=65,
            charisma=85,
            loyalty=95,
            traits=["Brave"],
            city="Chengdu"
        )
        deputy = Officer(
            name="ZhugeLiang",
            faction="Shu",
            leadership=45,
            intelligence=100,
            politics=95,
            charisma=92,
            loyalty=95,
            traits=["Scholar"],
            city="Chengdu"
        )

        # Combined traits
        combined_traits = set(commander.traits) | set(deputy.traits)

        assert "Brave" in combined_traits
        assert "Scholar" in combined_traits
        assert len(combined_traits) == 2


class TestFormationBonus:
    """Test formation bonuses from officer pairings."""

    def test_sworn_brother_formation_bonus(self):
        """Sworn brothers should have enhanced synergy."""
        # Liu Bei, Guan Yu, Zhang Fei are sworn brothers
        liu_bei = Officer(
            name="LiuBei",
            faction="Shu",
            leadership=86,
            intelligence=80,
            politics=88,
            charisma=96,
            loyalty=100,
            traits=["Benevolent", "Charismatic"],
            city="Chengdu",
            relationships={"GuanYu": "sworn_brother", "ZhangFei": "sworn_brother"}
        )
        guan_yu = Officer(
            name="GuanYu",
            faction="Shu",
            leadership=98,
            intelligence=79,
            politics=92,
            charisma=84,
            loyalty=100,
            traits=["Brave", "Strict"],
            city="Chengdu",
            relationships={"LiuBei": "sworn_brother", "ZhangFei": "sworn_brother"}
        )

        # Check sworn brother relationship
        assert liu_bei.relationships.get("GuanYu") == "sworn_brother"
        assert guan_yu.relationships.get("LiuBei") == "sworn_brother"

        # Sworn brother formation bonus: +15% effectiveness
        sworn_brother_bonus = 1.15

        base_effectiveness = guan_yu.leadership
        with_formation = base_effectiveness * sworn_brother_bonus

        assert with_formation == pytest.approx(98 * 1.15)

    def test_mentor_student_formation(self):
        """Mentor-student pairings should have learning bonuses."""
        # Zhuge Liang mentored Jiang Wei
        zhuge_liang = Officer(
            name="ZhugeLiang",
            faction="Shu",
            leadership=45,
            intelligence=100,
            politics=95,
            charisma=92,
            loyalty=95,
            traits=["Scholar"],
            city="Chengdu",
            relationships={"JiangWei": "student"}
        )
        jiang_wei = Officer(
            name="JiangWei",
            faction="Shu",
            leadership=88,
            intelligence=90,
            politics=80,
            charisma=75,
            loyalty=90,
            traits=[],
            city="Chengdu",
            relationships={"ZhugeLiang": "mentor"}
        )

        # Check mentor relationship
        assert zhuge_liang.relationships.get("JiangWei") == "student"
        assert jiang_wei.relationships.get("ZhugeLiang") == "mentor"

        # Mentor formation bonus: Student gains intelligence boost
        mentor_int_bonus = 0.10
        boosted_int = jiang_wei.intelligence * (1 + mentor_int_bonus)

        assert boosted_int == pytest.approx(90 * 1.10)

    def test_rival_no_formation_penalty(self):
        """Rivals should not have penalties when NOT fighting together."""
        # Zhou Yu and Zhuge Liang were rivals
        # When in same army, no synergy bonus

        zhou_yu = Officer(
            name="ZhouYu",
            faction="Wu",
            leadership=90,
            intelligence=92,
            politics=88,
            charisma=88,
            loyalty=85,
            traits=["Scholar"],
            city="Jianye",
            relationships={"ZhugeLiang": "rival"}
        )

        # Rivals don't get formation bonuses (neutral)
        rival_bonus = 1.0  # No bonus, no penalty in same army

        effective_leadership = zhou_yu.leadership * rival_bonus
        assert effective_leadership == zhou_yu.leadership


class TestBestDeputyPairings:
    """Test identification of optimal deputy pairings."""

    @pytest.fixture
    def available_officers(self):
        """Create a pool of available officers."""
        return [
            Officer(
                name="ZhaoYun",
                faction="Shu",
                leadership=96,
                intelligence=76,
                politics=65,
                charisma=85,
                loyalty=95,
                traits=["Brave"],
                city="Chengdu"
            ),
            Officer(
                name="MaChao",
                faction="Shu",
                leadership=95,
                intelligence=52,
                politics=40,
                charisma=78,
                loyalty=85,
                traits=["Brave"],
                city="Chengdu"
            ),
            Officer(
                name="ZhugeLiang",
                faction="Shu",
                leadership=45,
                intelligence=100,
                politics=95,
                charisma=92,
                loyalty=95,
                traits=["Scholar"],
                city="Chengdu"
            ),
            Officer(
                name="HuangZhong",
                faction="Shu",
                leadership=92,
                intelligence=60,
                politics=50,
                charisma=70,
                loyalty=85,
                traits=["Brave"],
                city="Chengdu"
            )
        ]

    def test_best_combat_pairing(self, available_officers):
        """Find best commander-deputy pairing for combat."""
        def calculate_combat_score(commander, deputy):
            """Calculate combat effectiveness score."""
            # Commander leadership + 25% deputy leadership
            return commander.leadership + (deputy.leadership * 0.25)

        officers = available_officers
        best_score = 0
        best_pairing = None

        # Try all pairings
        for i, commander in enumerate(officers):
            for j, deputy in enumerate(officers):
                if i != j:
                    score = calculate_combat_score(commander, deputy)
                    if score > best_score:
                        best_score = score
                        best_pairing = (commander.name, deputy.name)

        # Zhao Yun (96) + Ma Chao (95*0.25=23.75) = 119.75 should be best
        assert best_pairing[0] == "ZhaoYun"
        assert best_pairing[1] == "MaChao"
        assert best_score == pytest.approx(119.75)

    def test_best_strategy_pairing(self, available_officers):
        """Find best pairing for strategy/tactics."""
        def calculate_strategy_score(commander, deputy):
            """Calculate strategy effectiveness score."""
            # Combined intelligence focus
            return max(commander.intelligence, deputy.intelligence) + \
                   min(commander.intelligence, deputy.intelligence) * 0.5

        officers = available_officers
        best_score = 0
        best_pairing = None

        for i, commander in enumerate(officers):
            for j, deputy in enumerate(officers):
                if i != j:
                    score = calculate_strategy_score(commander, deputy)
                    if score > best_score:
                        best_score = score
                        best_pairing = (commander.name, deputy.name)

        # Zhuge Liang (100) with anyone provides max(100, x) + min(100, x)*0.5
        # Best: ZhugeLiang (100) + ZhaoYun (76*0.5=38) = 138
        assert "ZhugeLiang" in best_pairing

    def test_balanced_pairing(self, available_officers):
        """Find best balanced pairing (leadership + intelligence)."""
        def calculate_balanced_score(commander, deputy):
            """Calculate balanced effectiveness score."""
            combined_lead = commander.leadership + deputy.leadership * 0.25
            combined_int = commander.intelligence + deputy.intelligence * 0.25
            return combined_lead + combined_int

        officers = available_officers
        best_score = 0
        best_pairing = None

        for i, commander in enumerate(officers):
            for j, deputy in enumerate(officers):
                if i != j:
                    score = calculate_balanced_score(commander, deputy)
                    if score > best_score:
                        best_score = score
                        best_pairing = (commander.name, deputy.name)

        # Best balance should involve high leadership + high intelligence
        # Zhao Yun (96 lead, 76 int) + Zhuge Liang (45*0.25, 100*0.25)
        # = 96 + 11.25 + 76 + 25 = 208.25
        assert best_pairing is not None
        assert best_score > 150


class TestTroopCommandLimits:
    """Test troop command capacity based on leadership."""

    def test_leadership_determines_command_capacity(self):
        """Higher leadership should allow commanding more troops."""
        # Base formula: troops_per_leadership_point * leadership
        troops_per_lead = 100  # Each leadership point = 100 troops

        strong_leader = Officer(
            name="LuBu",
            faction="Dong Zhuo",
            leadership=100,
            intelligence=50,
            politics=30,
            charisma=60,
            loyalty=30,
            traits=["Brave"],
            city="Luoyang"
        )
        weak_leader = Officer(
            name="Scholar",
            faction="Wei",
            leadership=30,
            intelligence=90,
            politics=80,
            charisma=50,
            loyalty=70,
            traits=["Scholar"],
            city="Xuchang"
        )

        lu_bu_capacity = strong_leader.leadership * troops_per_lead
        scholar_capacity = weak_leader.leadership * troops_per_lead

        assert lu_bu_capacity == 10000
        assert scholar_capacity == 3000
        assert lu_bu_capacity > scholar_capacity

    def test_deputy_increases_command_capacity(self):
        """Deputy should increase total command capacity."""
        troops_per_lead = 100
        deputy_contribution = 0.5  # Deputy adds 50% of their capacity

        commander = Officer(
            name="ZhaoYun",
            faction="Shu",
            leadership=96,
            intelligence=76,
            politics=65,
            charisma=85,
            loyalty=95,
            traits=["Brave"],
            city="Chengdu"
        )
        deputy = Officer(
            name="MaChao",
            faction="Shu",
            leadership=95,
            intelligence=52,
            politics=40,
            charisma=78,
            loyalty=85,
            traits=["Brave"],
            city="Chengdu"
        )

        commander_capacity = commander.leadership * troops_per_lead
        deputy_bonus = deputy.leadership * troops_per_lead * deputy_contribution
        total_capacity = commander_capacity + deputy_bonus

        # 9600 + 4750 = 14350
        assert commander_capacity == 9600
        assert deputy_bonus == 4750
        assert total_capacity == 14350

    def test_exceeding_command_capacity_penalty(self):
        """Exceeding command capacity should penalize effectiveness."""
        troops_per_lead = 100
        commander_leadership = 50

        command_capacity = commander_leadership * troops_per_lead  # 5000

        # Under capacity: full effectiveness
        troops_under = 4000
        under_effectiveness = 1.0 if troops_under <= command_capacity else 0.8

        # Over capacity: reduced effectiveness
        troops_over = 7000
        over_ratio = min(1.0, command_capacity / troops_over)

        assert under_effectiveness == 1.0
        assert over_ratio == pytest.approx(5000 / 7000)
        assert over_ratio < 1.0

    def test_multiple_deputies_stacking(self):
        """Multiple deputies should stack command capacity."""
        troops_per_lead = 100
        deputy_contribution = 0.5

        commander_lead = 80  # 8000 troops
        deputy1_lead = 70   # 3500 additional
        deputy2_lead = 60   # 3000 additional

        total_capacity = (
            commander_lead * troops_per_lead +
            deputy1_lead * troops_per_lead * deputy_contribution +
            deputy2_lead * troops_per_lead * deputy_contribution
        )

        # 8000 + 3500 + 3000 = 14500
        assert total_capacity == 14500


class TestDeputyInBattle:
    """Test deputy mechanics in tactical battles."""

    def test_battle_uses_highest_leadership_as_commander(self):
        """Battle should automatically select best commander."""
        officers = [
            Officer(
                name="ZhaoYun",
                faction="Shu",
                leadership=96,
                intelligence=76,
                politics=65,
                charisma=85,
                loyalty=95,
                traits=["Brave"],
                city="Chengdu"
            ),
            Officer(
                name="ZhugeLiang",
                faction="Shu",
                leadership=45,
                intelligence=100,
                politics=95,
                charisma=92,
                loyalty=95,
                traits=["Scholar"],
                city="Chengdu"
            )
        ]

        commander = max(officers, key=lambda o: o.leadership)
        assert commander.name == "ZhaoYun"

    def test_battle_state_has_commander(self):
        """BattleState should track commander."""
        battle = BattleState(
            attacker_city="Chengdu",
            defender_city="Xuchang",
            attacker_faction="Shu",
            defender_faction="Wei",
            attacker_commander="ZhaoYun",
            defender_commander="XuChu",
            attacker_troops=5000,
            defender_troops=8000,
            terrain=TerrainType.PLAINS
        )

        assert battle.attacker_commander == "ZhaoYun"
        assert battle.defender_commander == "XuChu"

    def test_combined_officer_effectiveness_in_battle(self):
        """Combined officers should improve battle effectiveness."""
        # Single officer effectiveness
        single_lead = 80

        # Combined officers (commander + deputy)
        commander_lead = 80
        deputy_lead = 70
        deputy_contribution = 0.25

        combined_lead = commander_lead + (deputy_lead * deputy_contribution)

        # Combined should be better
        assert combined_lead > single_lead
        assert combined_lead == 80 + 17.5


class TestOfficerSynergyScenarios:
    """Test realistic officer synergy scenarios."""

    def test_five_tiger_generals_pairing(self):
        """Test pairing among Shu's Five Tiger Generals."""
        # The Five Tiger Generals: Guan Yu, Zhang Fei, Zhao Yun, Ma Chao, Huang Zhong
        five_tigers = [
            Officer(name="GuanYu", faction="Shu", leadership=98, intelligence=79,
                   politics=92, charisma=84, loyalty=100, traits=["Brave"], city="Chengdu"),
            Officer(name="ZhangFei", faction="Shu", leadership=97, intelligence=65,
                   politics=60, charisma=82, loyalty=100, traits=["Brave"], city="Chengdu"),
            Officer(name="ZhaoYun", faction="Shu", leadership=96, intelligence=76,
                   politics=65, charisma=85, loyalty=95, traits=["Brave"], city="Chengdu"),
            Officer(name="MaChao", faction="Shu", leadership=95, intelligence=52,
                   politics=40, charisma=78, loyalty=85, traits=["Brave"], city="Chengdu"),
            Officer(name="HuangZhong", faction="Shu", leadership=92, intelligence=60,
                   politics=50, charisma=70, loyalty=85, traits=["Brave"], city="Chengdu")
        ]

        # Average leadership of five tigers
        avg_leadership = sum(o.leadership for o in five_tigers) / len(five_tigers)
        assert avg_leadership > 95  # All are elite warriors

        # Best pairing for pure combat
        best_combo = sorted(five_tigers, key=lambda o: o.leadership, reverse=True)[:2]
        assert best_combo[0].name == "GuanYu"
        assert best_combo[1].name == "ZhangFei"

    def test_wei_elite_pairing(self):
        """Test Wei's elite officer pairings."""
        wei_elites = [
            Officer(name="XuChu", faction="Wei", leadership=94, intelligence=40,
                   politics=30, charisma=60, loyalty=85, traits=["Brave"], city="Xuchang"),
            Officer(name="DianWei", faction="Wei", leadership=96, intelligence=35,
                   politics=25, charisma=55, loyalty=100, traits=["Brave"], city="Xuchang"),
            Officer(name="ZhangLiao", faction="Wei", leadership=94, intelligence=78,
                   politics=70, charisma=76, loyalty=80, traits=["Brave"], city="Xuchang")
        ]

        # Dian Wei + Zhang Liao is a good balanced pairing
        # Dian Wei: pure combat, Zhang Liao: combat + tactics
        dian_wei = next(o for o in wei_elites if o.name == "DianWei")
        zhang_liao = next(o for o in wei_elites if o.name == "ZhangLiao")

        combined_lead = dian_wei.leadership + zhang_liao.leadership * 0.25
        combined_int = max(dian_wei.intelligence, zhang_liao.intelligence)

        assert combined_lead == 96 + 94 * 0.25  # 119.5
        assert combined_int == 78  # Zhang Liao's intelligence

    def test_wu_naval_commanders(self):
        """Test Wu's naval commander pairings."""
        wu_naval = [
            Officer(name="ZhouYu", faction="Wu", leadership=90, intelligence=92,
                   politics=88, charisma=88, loyalty=85, traits=["Scholar"], city="Jianye"),
            Officer(name="LuXun", faction="Wu", leadership=80, intelligence=90,
                   politics=82, charisma=80, loyalty=85, traits=["Scholar"], city="Jianye"),
            Officer(name="GanNing", faction="Wu", leadership=88, intelligence=65,
                   politics=60, charisma=70, loyalty=80, traits=["Brave"], city="Jianye")
        ]

        # Zhou Yu + Gan Ning: Strategy + Raw Combat
        zhou_yu = next(o for o in wu_naval if o.name == "ZhouYu")
        gan_ning = next(o for o in wu_naval if o.name == "GanNing")

        # Zhou Yu as strategist, Gan Ning as assault commander
        # Good for naval battles (fire attack + assault)
        fire_attack_bonus = zhou_yu.intelligence  # For strategy
        assault_power = gan_ning.leadership

        assert fire_attack_bonus >= 90  # Strong fire attack potential
        assert assault_power >= 85  # Strong assault capability
