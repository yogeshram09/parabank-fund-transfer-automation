"""Page Object for opening new bank accounts."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC


class OpenAccountPage(BasePage) :
    ACCOUNT_TYPE = (By.ID , "type")
    FUNDING_ACCOUNT = (By.ID , "fromAccountId")
    OPEN_BUTTON = (By.XPATH , "//input[@value='Open New Account']")
    NEW_ACCOUNT_LINK = (By.ID , "newAccountId")
    RESULT = (By.ID , "openAccountResult")

    def open_new_account ( self , account_type ) :
        """Open a new account using an available funding account."""

        # Select account type using visible text
        type_select = Select(self.visible(self.ACCOUNT_TYPE))

        available_types = [
            option.text.strip()
            for option in type_select.options
            if option.text.strip()
        ]

        matching_type = next(
            (t for t in available_types if t.upper() == account_type.upper()) ,
            None
        )

        assert matching_type , (
            f"Account type {account_type!r} is unavailable. "
            f"Available types: {available_types}"
        )

        type_select.select_by_visible_text(matching_type)

        # Wait until the funding dropdown has at least one selectable account
        self.wait.until(
            lambda driver : any(
                option.get_attribute("value")
                for option in Select(
                    driver.find_element(*self.FUNDING_ACCOUNT)
                ).options
            )
        )

        funding_select = Select(self.visible(self.FUNDING_ACCOUNT))

        funding_options = [
            option.get_attribute("value")
            for option in funding_select.options
            if option.get_attribute("value")
        ]

        assert funding_options , "No funding account is available."

        # Automatically select the first available funding account
        funding_select.select_by_value(funding_options[0])

        # Open the new account
        self.click(self.OPEN_BUTTON)

        new_account = self.visible(self.NEW_ACCOUNT_LINK).text.strip()
        assert new_account , "ParaBank did not return a new account number."
        return new_account
