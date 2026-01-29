"""Playwright fixtures for browser integration tests."""
import pytest
import socket
import subprocess
import sys
import time
from contextlib import closing


def find_free_port():
    """Find a free port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def wait_for_server(url, timeout=30):
    """Wait for server to respond to health check."""
    import urllib.request
    import urllib.error

    start = time.time()
    while time.time() - start < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=1)
            if response.status == 200:
                return True
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            pass
        time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server on a dynamic port for testing."""
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"

    # Start the Flask server as a subprocess
    process = subprocess.Popen(
        [sys.executable, "web_server.py"],
        env={**dict(__import__('os').environ), 'PORT': str(port)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    health_url = f"{base_url}/health"
    if not wait_for_server(health_url, timeout=30):
        process.terminate()
        process.wait()
        stdout, stderr = process.communicate(timeout=5)
        raise RuntimeError(
            f"Server failed to start within 30 seconds.\n"
            f"stdout: {stdout.decode()}\n"
            f"stderr: {stderr.decode()}"
        )

    yield base_url

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture(scope="session")
def browser_instance(playwright):
    """Create a shared browser instance for all tests."""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser_instance, flask_server):
    """Create a fresh browser context and page for each test."""
    context = browser_instance.new_context()
    page = context.new_page()
    page.set_default_timeout(10000)  # 10 second default timeout
    yield page
    context.close()


@pytest.fixture
def game_page(page, flask_server):
    """Page pre-loaded with the game."""
    page.goto(flask_server)
    # Wait for the page to fully load
    page.wait_for_selector('.game-output')
    return page
