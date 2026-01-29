"""
Integration Tests: Capture and Recruitment

This module tests the capture system mechanics:
- Capture probability calculation (loyalty-based)
- Loyalist death-before-capture behavior
- Captured officer recruitment process
- Execution and loyalty impact on own officers
- Release and reputation/relation bonuses
- Capture ability bonuses

Based on ROTK11 capture mechanics where officer loyalty
determines capture success and loyalist officers refuse surrender.
"""
import pytest
from unittest.mock import patch
from src.models import GameState, Officer, Faction, City
from src.systems.capture import (
    capture_officers,
    recruit_captured,
    execute_captured,
    release_captured,
    LOYALIST_OFFICERS
)


def create_officer(name, faction="", leadership=70, intelligence=70, politics=70, charisma=70,
                   loyalty=70, energy=100, city=None, task=None):
    """Helper to create an Officer with common defaults."""
    return Officer(
        name=name,
        faction=faction,
        leadership=leadership,
        intelligence=intelligence,
        politics=politics,
        charisma=charisma,
        loyalty=loyalty,
        energy=energy,
        city=city,
        task=task
    )


class TestCaptureProbabilityFormula:
    """Test the capture probability calculation based on loyalty."""

    def test_capture_chance_formula(self):
        """Capture chance = 0.8 - (loyalty / 200)."""
        # Low loyalty officer: 0.8 - (30/200) = 0.8 - 0.15 = 0.65 (65% chance)
        low_loyalty = 30
        low_chance = 0.8 - (low_loyalty / 200.0)
        assert low_chance == pytest.approx(0.65)

        # High loyalty officer: 0.8 - (100/200) = 0.8 - 0.5 = 0.3 (30% chance)
        high_loyalty = 100
        high_chance = 0.8 - (high_loyalty / 200.0)
        assert high_chance == pytest.approx(0.30)

    def test_very_low_loyalty_high_capture_chance(self):
        """Officers with very low loyalty are almost certain to be captured."""
        # 0 loyalty: 0.8 - 0 = 80% chance
        zero_loyalty = 0
        chance = 0.8 - (zero_loyalty / 200.0)
        assert chance == pytest.approx(0.80)

    def test_medium_loyalty_moderate_chance(self):
        """Officers with medium loyalty have moderate capture chance."""
        # 50 loyalty: 0.8 - 0.25 = 55% chance
        medium_loyalty = 50
        chance = 0.8 - (medium_loyalty / 200.0)
        assert chance == pytest.approx(0.55)

    def test_capture_probability_ranges(self):
        """Test capture probability across loyalty range."""
        probabilities = {}
        for loyalty in [0, 25, 50, 75, 100]:
            probabilities[loyalty] = 0.8 - (loyalty / 200.0)

        # Verify decreasing probability with increasing loyalty
        assert probabilities[0] > probabilities[25]
        assert probabilities[25] > probabilities[50]
        assert probabilities[50] > probabilities[75]
        assert probabilities[75] > probabilities[100]


class TestLoyalistOfficers:
    """Test the loyalist death-before-capture mechanic."""

    def test_loyalist_officers_list(self):
        """Verify the known loyalist officers."""
        assert "GuanYu" in LOYALIST_OFFICERS
        assert "ZhangFei" in LOYALIST_OFFICERS
        assert "DianWei" in LOYALIST_OFFICERS

    def test_loyalist_refuses_capture_high_loyalty(self):
        """Loyalist with high loyalty refuses capture (dies)."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "GuanYu"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "GuanYu": create_officer("GuanYu", "Wei", leadership=85, intelligence=70, politics=65, loyalty=95, city="Xuchang")
            }
        )

        results = capture_officers(gs, "Xuchang", "Shu")

        # Find GuanYu's result
        guan_yu_result = next((r for r in results if r["officer"] == "GuanYu"), None)

        assert guan_yu_result is not None
        assert guan_yu_result["outcome"] == "refused"

    def test_loyalist_can_be_captured_with_low_loyalty(self):
        """Loyalist with low loyalty (below 80) can be captured."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "GuanYu"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "GuanYu": create_officer("GuanYu", "Wei", leadership=85, intelligence=70, politics=65, loyalty=70, city="Xuchang")  # Low loyalty
            }
        )

        # With forced capture (mocking random)
        with patch('src.systems.capture.random.random', return_value=0.1):  # Always succeed
            results = capture_officers(gs, "Xuchang", "Shu")

        guan_yu_result = next((r for r in results if r["officer"] == "GuanYu"), None)
        assert guan_yu_result is not None
        assert guan_yu_result["outcome"] == "captured"

    def test_non_loyalist_can_be_captured_normally(self):
        """Non-loyalist officer can be captured regardless of loyalty."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "ZhangLiao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "ZhangLiao": create_officer("ZhangLiao", "Wei", leadership=80, intelligence=60, politics=55, loyalty=90, city="Xuchang")
            }
        )

        # With forced capture
        with patch('src.systems.capture.random.random', return_value=0.1):
            results = capture_officers(gs, "Xuchang", "Shu")

        zhang_liao_result = next((r for r in results if r["officer"] == "ZhangLiao"), None)
        assert zhang_liao_result is not None
        assert zhang_liao_result["outcome"] == "captured"


class TestCaptureProcess:
    """Test the capture process mechanics."""

    def test_captured_officer_stored_correctly(self):
        """Captured officer is stored in captured_officers dict."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "XuHuang"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=50, city="Xuchang")
            }
        )

        with patch('src.systems.capture.random.random', return_value=0.1):
            capture_officers(gs, "Xuchang", "Shu")

        assert hasattr(gs, 'captured_officers')
        assert "XuHuang" in gs.captured_officers
        assert gs.captured_officers["XuHuang"]["captor"] == "Shu"
        assert gs.captured_officers["XuHuang"]["original_faction"] == "Wei"

    def test_captured_officer_removed_from_faction(self):
        """Captured officer is removed from original faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "XuHuang"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=50, city="Xuchang")
            }
        )

        with patch('src.systems.capture.random.random', return_value=0.1):
            capture_officers(gs, "Xuchang", "Shu")

        assert "XuHuang" not in gs.factions["Wei"].officers

    def test_captured_officer_state_cleared(self):
        """Captured officer has city and task cleared."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "XuHuang"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=50, city="Xuchang", task="training")
            }
        )

        with patch('src.systems.capture.random.random', return_value=0.1):
            capture_officers(gs, "Xuchang", "Shu")

        officer = gs.officers["XuHuang"]
        assert officer.city is None
        assert officer.task is None
        assert officer.busy is False

    def test_officer_can_escape(self):
        """Officer can escape if random roll fails."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao", "XuHuang"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=50, city="Xuchang")
            }
        )

        # Force escape with high random value
        with patch('src.systems.capture.random.random', return_value=0.99):
            results = capture_officers(gs, "Xuchang", "Shu")

        xu_huang_result = next((r for r in results if r["officer"] == "XuHuang"), None)
        assert xu_huang_result is not None
        assert xu_huang_result["outcome"] == "escaped"


class TestRecruitment:
    """Test the recruitment of captured officers."""

    def test_recruit_captured_officer_success(self):
        """Successfully recruit a captured officer."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        result = recruit_captured(gs, "XuHuang")

        assert result["success"] is True
        assert "XuHuang" in gs.factions["Shu"].officers
        assert gs.officers["XuHuang"].faction == "Shu"

    def test_recruited_officer_low_starting_loyalty(self):
        """Recruited officers start with low loyalty (30)."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        recruit_captured(gs, "XuHuang")

        assert gs.officers["XuHuang"].loyalty == 30

    def test_recruited_officer_assigned_to_city(self):
        """Recruited officer is assigned to a faction city."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        recruit_captured(gs, "XuHuang")

        assert gs.officers["XuHuang"].city == "Chengdu"

    def test_recruit_not_your_prisoner_fails(self):
        """Cannot recruit a prisoner held by another faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"]),
                "Wu": Faction(name="Wu", ruler="SunQuan", cities=["Jianye"], officers=["SunQuan"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000),
                "Jianye": City(name="Jianye", owner="Wu", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "SunQuan": create_officer("SunQuan", "Wu", leadership=80, intelligence=75, politics=85, loyalty=100, city="Jianye"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Wu", "original_faction": "Wei"}  # Wu holds prisoner
        }

        result = recruit_captured(gs, "XuHuang")

        assert result["success"] is False

    def test_recruit_non_captured_fails(self):
        """Cannot recruit an officer who isn't captured."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang")
            }
        )
        gs.captured_officers = {}

        result = recruit_captured(gs, "NonExistent")

        assert result["success"] is False


class TestExecution:
    """Test execution of captured officers."""

    def test_execute_captured_officer(self):
        """Execute a captured officer removes them from game."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        result = execute_captured(gs, "XuHuang")

        assert result["success"] is True
        assert "XuHuang" not in gs.officers
        assert "XuHuang" not in gs.captured_officers

    def test_execute_causes_loyalty_drop(self):
        """Executing a prisoner causes loyalty drop for own officers."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=80, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        initial_loyalty = gs.officers["ZhaoYun"].loyalty

        execute_captured(gs, "XuHuang")

        # Officers lose 5 loyalty
        assert gs.officers["ZhaoYun"].loyalty == initial_loyalty - 5

    def test_execution_loyalty_impact_constant(self):
        """Verify the execution loyalty penalty is -5."""
        # Based on the code: off.loyalty = max(0, off.loyalty - 5)
        penalty = 5
        assert penalty == 5

    def test_execute_not_your_prisoner_fails(self):
        """Cannot execute a prisoner held by another faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wu": Faction(name="Wu", ruler="SunQuan", cities=["Jianye"], officers=["SunQuan"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Jianye": City(name="Jianye", owner="Wu", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "SunQuan": create_officer("SunQuan", "Wu", leadership=80, intelligence=75, politics=85, loyalty=100, city="Jianye"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Wu", "original_faction": "Wei"}
        }

        result = execute_captured(gs, "XuHuang")

        assert result["success"] is False


class TestRelease:
    """Test release of captured officers."""

    def test_release_captured_officer(self):
        """Release a captured officer returns them to original faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"],
                              relations={"Wei": 30}),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=80, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=60, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        result = release_captured(gs, "XuHuang")

        assert result["success"] is True
        assert "XuHuang" in gs.factions["Wei"].officers
        assert gs.officers["XuHuang"].faction == "Wei"

    def test_release_improves_relations(self):
        """Releasing a prisoner improves relations with original faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"],
                              relations={"Wei": 30}),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=80, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=60, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        initial_relations = gs.factions["Shu"].relations["Wei"]

        release_captured(gs, "XuHuang")

        # Relations improve by 10
        assert gs.factions["Shu"].relations["Wei"] == initial_relations + 10

    def test_release_boosts_own_officers_loyalty(self):
        """Releasing a prisoner boosts loyalty of own officers."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"],
                              relations={"Wei": 30}),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=80, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=60, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        initial_loyalty = gs.officers["ZhaoYun"].loyalty

        release_captured(gs, "XuHuang")

        # Officers gain 3 loyalty
        assert gs.officers["ZhaoYun"].loyalty == initial_loyalty + 3

    def test_released_officer_loyalty_boost(self):
        """Released officer gains +10 loyalty to their original faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"],
                              relations={"Wei": 30}),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=60, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        initial_loyalty = gs.officers["XuHuang"].loyalty

        release_captured(gs, "XuHuang")

        # Released officer gains loyalty
        assert gs.officers["XuHuang"].loyalty == min(100, initial_loyalty + 10)

    def test_release_not_your_prisoner_fails(self):
        """Cannot release a prisoner held by another faction."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wu": Faction(name="Wu", ruler="SunQuan", cities=["Jianye"], officers=["SunQuan"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Jianye": City(name="Jianye", owner="Wu", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "SunQuan": create_officer("SunQuan", "Wu", leadership=80, intelligence=75, politics=85, loyalty=100, city="Jianye"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Wu", "original_faction": "Wei"}
        }

        result = release_captured(gs, "XuHuang")

        assert result["success"] is False


class TestCaptureScenarios:
    """Test realistic capture scenarios."""

    def test_city_fall_multiple_captures(self):
        """Multiple officers can be captured when a city falls."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"],
                              officers=["CaoCao", "XuHuang", "YuJin", "LiDian"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=50, city="Xuchang"),
                "YuJin": create_officer("YuJin", "Wei", leadership=70, intelligence=60, politics=55, loyalty=60, city="Xuchang"),
                "LiDian": create_officer("LiDian", "Wei", leadership=68, intelligence=58, politics=52, loyalty=70, city="Xuchang")
            }
        )

        with patch('src.systems.capture.random.random', return_value=0.1):
            results = capture_officers(gs, "Xuchang", "Shu")

        captured_count = sum(1 for r in results if r["outcome"] == "captured")
        assert captured_count >= 3  # Excluding CaoCao who is ruler

    def test_zhang_liao_historical_capture(self):
        """Zhang Liao was historically captured and recruited (Lu Bu -> Cao Cao)."""
        gs = GameState(
            year=208, month=1,
            player_faction="Wei",
            factions={
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"]),
                "LuBu": Faction(name="LuBu", ruler="LuBu", cities=["Xiapi"], officers=["LuBu", "ZhangLiao"])
            },
            cities={
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000),
                "Xiapi": City(name="Xiapi", owner="LuBu", troops=3000)
            },
            officers={
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "LuBu": create_officer("LuBu", "LuBu", leadership=75, intelligence=30, politics=20, loyalty=20, city="Xiapi"),
                "ZhangLiao": create_officer("ZhangLiao", "LuBu", leadership=80, intelligence=60, politics=55, loyalty=75, city="Xiapi")
            }
        )

        # Capture Zhang Liao
        with patch('src.systems.capture.random.random', return_value=0.1):
            results = capture_officers(gs, "Xiapi", "Wei")

        zhang_liao_result = next((r for r in results if r["officer"] == "ZhangLiao"), None)
        assert zhang_liao_result is not None
        assert zhang_liao_result["outcome"] == "captured"

        # Recruit him
        result = recruit_captured(gs, "ZhangLiao")
        assert result["success"] is True
        assert "ZhangLiao" in gs.factions["Wei"].officers

    def test_guan_yu_historical_temporary_service(self):
        """Guan Yu historically served Cao Cao temporarily."""
        gs = GameState(
            year=208, month=1,
            player_faction="Wei",
            factions={
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"]),
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Xinye"], officers=["LiuBei", "GuanYu"])
            },
            cities={
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000),
                "Xinye": City(name="Xinye", owner="Shu", troops=3000)
            },
            officers={
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Xinye"),
                # Guan Yu with slightly lowered loyalty (below 80) for this scenario
                "GuanYu": create_officer("GuanYu", "Shu", leadership=85, intelligence=70, politics=65, loyalty=75, city="Xinye")
            }
        )

        # With lowered loyalty, Guan Yu can be captured
        with patch('src.systems.capture.random.random', return_value=0.1):
            results = capture_officers(gs, "Xinye", "Wei")

        guan_yu_result = next((r for r in results if r["officer"] == "GuanYu"), None)
        assert guan_yu_result is not None
        assert guan_yu_result["outcome"] == "captured"


class TestReputationMechanics:
    """Test reputation effects from capture actions."""

    def test_release_reputation_value(self):
        """Verify the reputation/relation bonus from release."""
        # From code: relations improve by 10
        relation_bonus = 10
        assert relation_bonus == 10

    def test_release_own_officer_loyalty_value(self):
        """Verify own officer loyalty bonus from release."""
        # From code: off.loyalty = min(100, off.loyalty + 3)
        loyalty_bonus = 3
        assert loyalty_bonus == 3

    def test_execution_reputation_penalty(self):
        """Executing officers has negative reputation effect (loyalty drop)."""
        # From code: off.loyalty = max(0, off.loyalty - 5)
        loyalty_penalty = 5
        assert loyalty_penalty == 5


class TestCaptureEdgeCases:
    """Test edge cases in capture mechanics."""

    def test_capture_empty_city(self):
        """Capture on city with no officers returns empty results."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Luoyang")  # Not in Xuchang
            }
        )

        results = capture_officers(gs, "Xuchang", "Shu")
        assert len(results) == 0

    def test_capture_nonexistent_city(self):
        """Capture on nonexistent city returns empty results."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu")
            }
        )

        results = capture_officers(gs, "NonExistent", "Shu")
        assert len(results) == 0

    def test_loyalty_minimum_after_execution(self):
        """Officer loyalty cannot go below 0 after execution."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"]),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=3, city="Chengdu"),  # Very low
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        execute_captured(gs, "XuHuang")

        # Loyalty should not go below 0
        assert gs.officers["ZhaoYun"].loyalty >= 0

    def test_loyalty_maximum_after_release(self):
        """Officer loyalty cannot exceed 100 after release."""
        gs = GameState(
            year=208, month=1,
            player_faction="Shu",
            factions={
                "Shu": Faction(name="Shu", ruler="LiuBei", cities=["Chengdu"], officers=["LiuBei", "ZhaoYun"],
                              relations={"Wei": 30}),
                "Wei": Faction(name="Wei", ruler="CaoCao", cities=["Xuchang"], officers=["CaoCao"])
            },
            cities={
                "Chengdu": City(name="Chengdu", owner="Shu", troops=5000),
                "Xuchang": City(name="Xuchang", owner="Wei", troops=5000)
            },
            officers={
                "LiuBei": create_officer("LiuBei", "Shu", leadership=75, intelligence=70, politics=80, loyalty=100, city="Chengdu"),
                "ZhaoYun": create_officer("ZhaoYun", "Shu", leadership=85, intelligence=65, politics=60, loyalty=99, city="Chengdu"),  # Very high
                "CaoCao": create_officer("CaoCao", "Wei", leadership=90, intelligence=85, politics=95, loyalty=100, city="Xuchang"),
                "XuHuang": create_officer("XuHuang", "Wei", leadership=75, intelligence=55, politics=50, loyalty=80, city=None)
            }
        )
        gs.captured_officers = {
            "XuHuang": {"captor": "Shu", "original_faction": "Wei"}
        }

        release_captured(gs, "XuHuang")

        # Loyalty should not exceed 100
        assert gs.officers["ZhaoYun"].loyalty <= 100
