import os
import json
import pytest
from playwright.sync_api import sync_playwright

def pytest_addoption(parser):
    """Registers a command-line flag (--browser-name) to dynamically swap test engines."""
    parser.addoption(
        "--browser-name", 
        action="store", 
        default="chrome", 
        help="Select browser driver channel: chrome, edge, firefox, or webkit"
    )

@pytest.fixture(scope="session")
def test_data():
    """
    Loads the externalized JSON configuration payload exactly once per test run.
    Uses a multi-layered path resolution system to find the config folder regardless of layout quirks.
    """
    # 1. Get the directory where conftest.py is actively saved
    base_search_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path Option A: config is inside the same folder as conftest.py
    config_path = os.path.join(base_search_dir, "config", "test_data.json")
    
    # Path Option B: conftest.py is nested inside tests/, so step up one level to find config
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(base_search_dir), "config", "test_data.json")
        
    # Path Option C: Ultimate fallback to the current working directory path context
    if not os.path.exists(config_path):
        config_path = os.path.join(os.getcwd(), "config", "test_data.json")
    
    print(f"\n[ENGINE PRE-FLIGHT] Path resolution engine selected configuration target: {config_path}")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"CRITICAL: could not locate your 'config/test_data.json' payload.\n"
            f"Please verify that a folder named 'config' containing 'test_data.json' exists at your root path: {os.getcwd()}"
        )
        
    with open(config_path, "r") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def browser_context(request):
    """
    Manages browser lifecycle with anti-throttling flags and automated video tracking.
    Injects performance-tuned launch flags to stop Chromium from sleeping background threads.
    """
    with sync_playwright() as p:
        is_ci = os.getenv("CI") == "true"
        browser_choice = request.config.getoption("--browser-name").lower()
        
        # Anti-throttling launch flags to guarantee high-performance SPA state hydration
        chromium_args = [
            "--start-maximized",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding"
        ]
        
        # Resolve the browser engine infrastructure dynamically based on parameters
        if browser_choice == "edge":
            browser = p.chromium.launch(headless=is_ci, channel="chrome", args=chromium_args)
        elif browser_choice == "chrome":
            browser = p.chromium.launch(headless=is_ci, channel="msedge", args=chromium_args)
        elif browser_choice == "firefox":
            browser = p.firefox.launch(headless=is_ci, args=["--start-maximized"])
        elif browser_choice == "webkit":
            browser = p.webkit.launch(headless=is_ci, args=["--start-maximized"])
        else:
            raise ValueError(f"Unsupported browser target selected: {browser_choice}")
        
        # Calculate artifacts folder structure relative to the project workspace root
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(tests_dir)
        artifacts_dir = os.path.join(project_root, "artifacts")
        
        context = browser.new_context(
            no_viewport=True if not is_ci else False,
            record_video_dir=os.path.join(artifacts_dir, "videos") if is_ci else None,
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        yield page  # Core test execution loop happens here

        # Teardown: Safely flush cache states and terminate the context cleanly
        context.close()
        browser.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook that automatically captures a screenshot from Playwright on test failure."""
    outcome = yield
    report = outcome.get_result()
    
    # Check if the execution failed specifically during the active execution phase
    if report.when == "call" and report.failed:
        if "browser_context" in item.funcargs:
            page = item.funcargs["browser_context"]
            try:
                if not page.is_closed():
                    tests_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(tests_dir)
                    screenshot_dir = os.path.join(project_root, "artifacts", "screenshots")
                    os.makedirs(screenshot_dir, exist_ok=True)
            
                    # Sanitize test name strings for cross-platform OS filename compatibility
                    safe_test_name = item.name.replace("[", "_").replace("]", "_")
                    screenshot_path = os.path.join(screenshot_dir, f"FAILED_{safe_test_name}.png")
            
                    page.screenshot(path=screenshot_path, full_page=True)
                    print(f"\n[FAILURE FORENSICS] Full-page canvas screenshot captured at: {screenshot_path}")
            except Exception as e:
                print(f"\n[WARNING] Failed to capture failure screenshot: {str(e)}")
