"""Page Object for ParaBank customer registration."""
from selenium.webdriver.common.by import By

from conftest import logger
from pages.base_page import BasePage


class RegistrationPage(BasePage) :
    REGISTER_LINK = (By.LINK_TEXT , "Register")
    FIRST_NAME = (By.ID , "customer.firstName")
    LAST_NAME = (By.ID , "customer.lastName")
    STREET = (By.ID , "customer.address.street")
    CITY = (By.ID , "customer.address.city")
    STATE = (By.ID , "customer.address.state")
    ZIP = (By.ID , "customer.address.zipCode")
    PHONE = (By.ID , "customer.phoneNumber")
    SSN = (By.ID , "customer.ssn")
    USERNAME = (By.ID , "customer.username")
    PASSWORD = (By.ID , "customer.password")
    CONFIRM_PASSWORD = (By.ID , "repeatedPassword")
    SUBMIT = (By.XPATH , "//input[@value='Register']")
    SUCCESS_HEADING = (By.XPATH , "//*[contains(normalize-space(.), 'Welcome')]")

    def open ( self , base_url ) :
        self.driver.get(f"{base_url.rstrip('/')}/register.htm")
        self.visible(self.FIRST_NAME)

    def register ( self , customer ) :
        """Fill every registration field from generated/configurable data."""
        fields = [
            (self.FIRST_NAME , customer["first_name"]) ,
            (self.LAST_NAME , customer["last_name"]) ,
            (self.STREET , customer["street"]) ,
            (self.CITY , customer["city"]) ,
            (self.STATE , customer["state"]) ,
            (self.ZIP , customer["zip_code"]) ,
            (self.PHONE , customer["phone"]) ,
            (self.SSN , customer["ssn"]) ,
            (self.USERNAME , customer["username"]) ,
            (self.PASSWORD , customer["password"]) ,
            (self.CONFIRM_PASSWORD , customer["password"]) ,
        ]
        for locator , value in fields :
            self.type_text(locator , value)
        self.click(self.SUBMIT)
        # ParaBank redirects to the authenticated welcome page after registration.
        # Wait for successful registration message
        self.wait_for_text((By.TAG_NAME , "body") , "Your account was created successfully")
        logger.info("Customer registration completed successfully")
