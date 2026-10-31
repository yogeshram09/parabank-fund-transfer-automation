"""Shared pytest fixtures, browser lifecycle, and failure attachments."""
import os
from pathlib import Path
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utilities.config_reader import load_config , load_test_data
from utilities.logger import get_logger

logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def config () :
    return load_config()


@pytest.fixture(scope="session")
def test_data () :
    return load_test_data()


@pytest.fixture
def driver ( config ) :
    """Create a fresh browser for each test and always close it afterwards."""
    browser = config["browser"].lower()
    if browser == "chrome" :
        options = ChromeOptions()
        # Disable Chrome Save Address and Autofill popup
        prefs = {
            "autofill.profile_enabled" : False ,
            "autofill.address_enabled" : False ,
            "autofill.credit_card_enabled" : False ,
            "credentials_enable_service" : False ,
            "profile.password_manager_enabled" : False
        }

        options.add_experimental_option("prefs" , prefs)
        if config.get("headless") :
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        browser_driver = webdriver.Chrome(options=options)  # Selenium Manager resolves driver.
    elif browser == "firefox" :
        options = FirefoxOptions()
        if config.get("headless") :
            options.add_argument("-headless")
        browser_driver = webdriver.Firefox(options=options)
    else :
        raise ValueError(f"Unsupported browser configured: {browser}")

    browser_driver.set_page_load_timeout(config["page_load_timeout"])
    browser_driver.implicitly_wait(0)  # Explicit waits are used throughout the framework.
    yield browser_driver
    browser_driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport ( item , call ) :
    """Attach screenshot and browser URL to Allure whenever a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed :
        browser_driver = item.funcargs.get("driver")
        if browser_driver :
            try :
                allure.attach(
                    browser_driver.get_screenshot_as_png() ,
                    name=f"{item.name}-failure" ,
                    attachment_type=allure.attachment_type.PNG ,
                )
                allure.attach(
                    browser_driver.current_url ,
                    name="failure-url" ,
                    attachment_type=allure.attachment_type.TEXT ,
                )
            except Exception :
                logger.exception("Unable to attach browser diagnostics to Allure.")
