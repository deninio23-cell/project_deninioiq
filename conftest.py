import pytest
import json
import os
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def test_data():
    config_path = os.path.join(os.path.dirname(__file__), "config", "test_data.json")
    with open(config_path, "r") as f:
        return json.load(f)
    

@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        # Running visible (headed=True) helps you visualize structural executions locally
        is_ci = os.getenv("CI") == "true"
        browser = p.chromium.launch(headless=is_ci, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True if not is_ci else False)
        page = context.new_page()

        yield page

        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path=f"screenshots/final_state_{os.getpid()}.png")
        context.close()
        browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook that automatically captures a screenshot from Playwright on test failure."""
    # Execute all other hooks to get the actual report object
    outcome = yield
    report = outcome.get_result()
    
    # Check if the test failed during its execution phase
    if report.when == "call" and report.failed:
        # Check if our page instance is available inside the test arguments
        if "browser_context" in item.funcargs:
            page = item.funcargs["browser_context"]
            try:
                if not page.is_closed():
                
                    # Ensure the screenshots folder exists
                    screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
                    os.makedirs(screenshot_dir, exist_ok=True)
            
                    # Clean up the test name to create a safe file name
                    safe_test_name = item.name.replace("[", "_").replace("]", "_")
                    screenshot_path = os.path.join(screenshot_dir, f"FAILED_{safe_test_name}.png")
            
                    # Take a full-page screenshot so you can see the entire browser viewport state
                    page.screenshot(path=screenshot_path, full_page=True)
                    print(f"\n[FAILURE SCREENSHOT SAVED] Trace captured at: {screenshot_path}")
            except Exception as e:
                print(f"\n[WARNING] Could not save screenshot: {str(e)}")