"""
Sanity test for Flask app import and basic functionality
"""
import pytest


def test_app_import():
    """Test that app module can be imported"""
    import app
    assert app is not None


def test_app_object_exists():
    """Test that Flask app object is created"""
    import app
    assert hasattr(app, 'app')
    assert app.app is not None


def test_app_has_routes():
    """Test that app has expected routes"""
    import app
    
    # Get all registered routes
    routes = [rule.rule for rule in app.app.url_map.iter_rules()]
    
    # Check for expected routes
    assert '/' in routes
    assert '/api/init' in routes
    assert '/api/echo' in routes
    assert '/api/save' in routes
    assert '/api/load' in routes


def test_app_static_folder():
    """Test that app has static folder configured"""
    import app
    assert app.app.static_folder is not None
    assert 'static' in app.app.static_folder


def test_api_init_endpoint():
    """Test /api/init endpoint returns valid JSON"""
    import app
    
    client = app.app.test_client()
    response = client.get('/api/init')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert 'version' in data
    assert 'factions' in data
    assert 'cities' in data
    assert 'officers' in data
    assert 'turn' in data


def test_api_echo_endpoint():
    """Test /api/echo endpoint echoes command"""
    import app
    
    client = app.app.test_client()
    response = client.post('/api/echo', json={'command': 'test'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data['ok'] is True
    assert data['command'] == 'test'
    assert 'message' in data


def test_api_save_endpoint():
    """Test /api/save endpoint saves state to cookie"""
    import app
    
    client = app.app.test_client()
    test_state = {'version': '0.1', 'test': 'data'}
    response = client.post('/api/save', json=test_state)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data['ok'] is True
    
    # Check that cookie was set (Flask test client stores cookies)
    assert any('sango_state' in header for header in response.headers.getlist('Set-Cookie'))


def test_api_load_endpoint_no_cookie():
    """Test /api/load endpoint returns error when no cookie"""
    import app
    
    client = app.app.test_client()
    response = client.get('/api/load')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data['ok'] is False
    assert data['error'] == 'no_state'


def test_api_save_and_load_roundtrip():
    """Test save and load roundtrip preserves state"""
    import app
    
    client = app.app.test_client()
    test_state = {
        'version': '0.1',
        'factions': ['Wei', 'Shu', 'Wu'],
        'cities': ['Xuchang', 'Chengdu'],
        'turn': {'year': 190, 'month': 1}
    }
    
    # Save state
    save_response = client.post('/api/save', json=test_state)
    assert save_response.status_code == 200
    
    # Load state
    load_response = client.get('/api/load')
    assert load_response.status_code == 200
    
    data = load_response.get_json()
    assert data['ok'] is True
    assert data['state'] == test_state
