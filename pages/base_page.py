"""Base page with reusable Selenium interactions and explicit waits."""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage :
    def __init__ ( self , driver , timeout=15 ) :
        self.driver = driver
        self.wait = WebDriverWait(driver , timeout)

    def visible ( self , locator ) :
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable ( self , locator ) :
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click ( self , locator ) :
        self.clickable(locator).click()

    def type_text ( self , locator , value , clear=True ) :
        element = self.visible(locator)
        if clear :
            element.clear()
        element.send_keys(str(value))

    def text ( self , locator ) :
        return self.visible(locator).text.strip()

    def wait_for_url_contains ( self , value ) :
        self.wait.until(EC.url_contains(value))

    def wait_for_text ( self , locator , expected_text ) :
        """Wait until expected text appears in an element."""
        return self.wait.until(EC.text_to_be_present_in_element(locator , expected_text))

    def optional_text ( self , locator ) :
        """Return visible text when present, otherwise an empty string."""
        try :
            return self.visible(locator).text.strip()
        except TimeoutException :
            return ""
