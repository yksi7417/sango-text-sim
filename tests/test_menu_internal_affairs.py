"""
Tests for the Internal Affairs menu functionality.

These tests ensure that the menu-based internal development system works correctly,
allowing players to develop their cities through agriculture, commerce, and technology.
"""
import pytest
from src.models import GameState, Officer, City, Faction
from src import world, utils, engine
import web_server


def perform_internal_action(gs, session_state, option, selection='1'):
    """Helper to select an internal affairs option and choose an officer."""
    prompt = web_server.handle_menu_input(gs, session_state, option)
    assert prompt  # Should prompt for officer selection
    result = web_server.handle_menu_input(gs, session_state, selection)
    return prompt, result


def current_assignment_officer(gs, faction_name, city_name):
    """Return the officer currently assigned to work in the specified city."""
    faction = gs.factions[faction_name]
    for off_name in faction.officers:
        officer = gs.officers[off_name]
        if officer.busy and officer.task_city == city_name:
            return officer
    return None


class TestInternalAffairsMenuNavigation:
    """Test navigation to and within the Internal Affairs menu."""
    
    def test_navigate_to_internal_menu(self):
        """Test navigating from main menu to internal affairs menu."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'main',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Navigate to internal affairs (option 5)
        output = web_server.handle_menu_input(gs, session_state, '5')
        
        assert session_state['current_menu'] == 'internal'
        # Menu navigation returns empty string, buttons handle the UI
        assert output == ''
    
    def test_internal_menu_requires_current_city(self):
        """Test that internal affairs menu defaults to first city when current city is None."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': None,  # No city set
            'language': 'en'
        }
        
        # Try to use internal affairs without a current city - should default to first city
        prompt = web_server.handle_menu_input(gs, session_state, '1')
        assert 'Select an officer' in prompt or '請選擇' in prompt

        # Choose the first officer to complete the assignment setup
        result = web_server.handle_menu_input(gs, session_state, '1')
        assert '[OK]' in result
        # Current city should now be set to the first city
        assert session_state['current_city'] is not None
        assert session_state['current_city'] in gs.factions['Shu'].cities
    
    def test_internal_menu_validates_city_ownership(self):
        """Test that internal affairs menu validates you own the city."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Luoyang',  # Not owned by Shu
            'language': 'en'
        }
        
        # Try to develop a city you don't own
        output = web_server.handle_menu_input(gs, session_state, '1')
        
        assert 'no longer under your control' in output.lower()
        assert session_state['current_menu'] == 'main'
    
    def test_back_from_internal_menu(self):
        """Test going back from internal affairs to main menu."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Press 0 or 'back'
        output = web_server.handle_menu_input(gs, session_state, '0')
        
        assert session_state['current_menu'] == 'main'
        # Menu navigation returns empty string, buttons handle the UI
        assert output == ''


class TestAgricultureDevelopment:
    """Test agriculture development through the menu."""
    
    def test_develop_agriculture_success(self):
        """Test successfully developing agriculture in a city."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_agri = city.agri
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop agriculture (option 1) and choose the first officer
        prompt, output = perform_internal_action(gs, session_state, '1')

        assert 'Agriculture' in prompt or '農業' in prompt
        assert 'Results will apply' in output or '成果將於月底結算' in output
        assert session_state['current_menu'] == 'internal'

        assigned = current_assignment_officer(gs, 'Shu', 'Chengdu')
        assert assigned is not None
        assert assigned.task == 'farm'

        # Process month-end to apply the effect
        engine.process_assignments(gs)

        assert city.agri > initial_agri
    
    def test_agriculture_requires_available_officer(self):
        """Test that agriculture development needs an available officer."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        # Exhaust all officers in Chengdu
        faction = gs.factions['Shu']
        for off_name in faction.officers:
            off = gs.officers[off_name]
            if off.city == 'Chengdu':
                off.energy = 10  # Below threshold
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Try to develop agriculture
        output = web_server.handle_menu_input(gs, session_state, '1')
        
        assert 'no available officers' in output.lower() or '無可用武將' in output
    
    def test_flood_management_improves_agriculture(self):
        """Test that flood management also improves agriculture."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_agri = city.agri
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Flood management (option 2)
        prompt, output = perform_internal_action(gs, session_state, '2')

        assert 'Flood' in prompt or '治水' in prompt

        # Process month-end to apply the effect
        engine.process_assignments(gs)

        assert city.agri > initial_agri


class TestCommerceDevelopment:
    """Test commerce development through the menu."""
    
    def test_develop_commerce_success(self):
        """Test successfully developing commerce in a city."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_commerce = city.commerce
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop commerce (option 3)
        prompt, output = perform_internal_action(gs, session_state, '3')

        assert 'Commerce' in prompt or '商業' in prompt
        assert 'Results will apply' in output or '成果將於月底結算' in output

        engine.process_assignments(gs)

        assert city.commerce > initial_commerce
    
    def test_commerce_shown_in_status(self):
        """Test that commerce level is shown in the output."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        _, output = perform_internal_action(gs, session_state, '3')

        # Should show commerce stat in the confirmation output
        assert 'Commerce:' in output


class TestTechnologyDevelopment:
    """Test technology development through the menu."""
    
    def test_develop_technology_success(self):
        """Test successfully developing technology in a city."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_tech = city.tech
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop technology (option 4)
        prompt, output = perform_internal_action(gs, session_state, '4')

        assert 'Technology' in prompt or '科技' in prompt
        assert 'Results will apply' in output or '成果將於月底結算' in output

        engine.process_assignments(gs)

        assert city.tech > initial_tech


class TestOfficerSelection:
    """Test automatic officer selection for tasks."""
    
    def test_selects_best_officer_for_agriculture(self):
        """Test that the system selects the best officer for agriculture."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        # Create officers with different politics skills
        faction = gs.factions['Shu']
        
        # Add a high-politics officer
        high_pol_officer = Officer(
            name="HighPolitics", faction="Shu", city="Chengdu",
            leadership=50, intelligence=50, politics=90, charisma=50,
            energy=100, loyalty=80, traits=["Benevolent"]
        )
        gs.officers["HighPolitics"] = high_pol_officer
        faction.officers.append("HighPolitics")
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop agriculture - prompt should list HighPolitics first
        prompt = web_server.handle_menu_input(gs, session_state, '1')
        first_option = next(
            (line.strip() for line in prompt.splitlines() if line.strip().startswith('1.')),
            ""
        )
        assert 'HighPolitics' in first_option

        # Cancel to avoid locking assignment for other tests
        cancel_output = web_server.handle_menu_input(gs, session_state, 'cancel')
        assert 'cancel' in cancel_output.lower()
    
    def test_selects_officer_with_beneficial_trait(self):
        """Test that officers with beneficial traits are preferred."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        faction = gs.factions['Shu']
        
        # Add a Merchant officer (good for commerce)
        merchant = Officer(
            name="Merchant", faction="Shu", city="Chengdu",
            leadership=50, intelligence=50, politics=70, charisma=50,
            energy=100, loyalty=80, traits=["Merchant"]
        )
        gs.officers["Merchant"] = merchant
        faction.officers.append("Merchant")
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop commerce - prompt should include Merchant officer as an option
        prompt = web_server.handle_menu_input(gs, session_state, '3')
        assert 'Merchant' in prompt

        web_server.handle_menu_input(gs, session_state, 'cancel')


class TestMenuContinuity:
    """Test that the menu stays in Internal Affairs after actions."""
    
    def test_stays_in_internal_menu_after_action(self):
        """Test that after completing an action, menu stays in Internal Affairs."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Perform an action (Agriculture)
        _, output = perform_internal_action(gs, session_state, '1')

        # Should still be in internal menu
        assert session_state['current_menu'] == 'internal'
        # Action feedback is returned after officer selection
        assert '[OK]' in output

    def test_multiple_consecutive_actions(self):
        """Test performing multiple internal affairs actions in sequence."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop agriculture and resolve the assignment
        _, output1 = perform_internal_action(gs, session_state, '1')
        assert 'Agriculture' in output1
        engine.process_assignments(gs)

        # Develop commerce and resolve
        _, output2 = perform_internal_action(gs, session_state, '3')
        assert 'Commerce' in output2
        engine.process_assignments(gs)

        # Develop technology and resolve
        _, output3 = perform_internal_action(gs, session_state, '4')
        assert 'Technology' in output3
        engine.process_assignments(gs)

        assert session_state['current_menu'] == 'internal'


class TestResourceDisplay:
    """Test that resources are displayed correctly."""
    
    def test_displays_city_resources(self):
        """Test that gold and food are shown in the output."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        _, output = perform_internal_action(gs, session_state, '1')

        assert 'Gold:' in output
        assert 'Food:' in output
    
    def test_displays_development_stats(self):
        """Test that agriculture, commerce, tech stats are shown."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        _, output = perform_internal_action(gs, session_state, '1')

        assert 'Agriculture:' in output
        assert 'Commerce:' in output
        assert 'Technology:' in output


class TestChineseLanguageSupport:
    """Test Chinese language support for Internal Affairs menu."""
    
    def test_internal_menu_in_chinese(self):
        """Test that internal affairs menu displays correctly in Chinese."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'zh'
        }
        
        # Navigate to show menu
        output = web_server.format_menu('internal', gs, session_state)
        
        # format_menu now returns empty string, buttons handle the UI
        assert output == ''
    
    def test_action_feedback_in_chinese(self):
        """Test that action feedback is in Chinese when language is set to zh."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'zh'
        }
        
        prompt = web_server.handle_menu_input(gs, session_state, '1')
        result = web_server.handle_menu_input(gs, session_state, '1')

        # Should contain Chinese text in either prompt or result
        combined = prompt + result
        assert any('\u4e00' <= char <= '\u9fff' for char in combined)


class TestIntegrationWithGameMechanics:
    """Integration tests with core game mechanics."""
    
    def test_agriculture_improves_food_production_long_term(self):
        """Test that developing agriculture assigns officers correctly."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_agri = city.agri
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop agriculture multiple times
        for _ in range(3):
            faction = gs.factions['Shu']
            for off_name in faction.officers:
                off = gs.officers[off_name]
                if off.city == 'Chengdu':
                    off.energy = 100

            perform_internal_action(gs, session_state, '1')
            engine.process_assignments(gs)

        # Agriculture should have improved from the accumulated effects
        assert city.agri > initial_agri
    
    def test_commerce_improves_gold_production(self):
        """Test that developing commerce assigns officers correctly."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_commerce = city.commerce
        initial_gold = city.gold
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        city.troops = 0  # Remove upkeep for clarity

        # Develop commerce
        perform_internal_action(gs, session_state, '3')
        engine.process_assignments(gs)

        before_economy_gold = city.gold
        engine.monthly_economy(gs)

        assert city.commerce > initial_commerce
        assert city.gold > before_economy_gold
    
    def test_technology_provides_combat_bonus(self):
        """Test that technology development improves tech level."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        city = gs.cities['Chengdu']
        initial_tech = city.tech
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Develop technology
        perform_internal_action(gs, session_state, '4')
        engine.process_assignments(gs)

        assert city.tech > initial_tech
    
    def test_officer_energy_depletes(self):
        """Test that officers lose energy when performing tasks."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        # Get an officer in Chengdu
        faction = gs.factions['Shu']
        officer = None
        for off_name in faction.officers:
            off = gs.officers[off_name]
            if off.city == 'Chengdu':
                officer = off
                break
        
        assert officer is not None
        initial_energy = officer.energy
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        # Perform an action
        perform_internal_action(gs, session_state, '1')

        # Energy should have decreased
        assert officer.energy < initial_energy


class TestBuildSchool:
    """Test school building feature (placeholder for future)."""
    
    def test_build_school_not_yet_implemented(self):
        """Test that build school shows not implemented message."""
        gs = GameState()
        world.init_world(gs, player_choice="Shu", seed=42)
        
        session_state = {
            'current_menu': 'internal',
            'current_city': 'Chengdu',
            'language': 'en'
        }
        
        output = web_server.handle_menu_input(gs, session_state, '5')
        
        assert 'not yet implemented' in output.lower() or '尚未實裝' in output
