"""Page Object for fund transfers."""
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException


class TransferPage(BasePage) :
    AMOUNT = (By.ID , "amount")
    FROM_ACCOUNT = (By.ID , "fromAccountId")
    TO_ACCOUNT = (By.ID , "toAccountId")
    SUBMIT = (By.XPATH , "//input[@value='Transfer']")
    RESULT = (By.ID , "showResult")
    SUCCESS = (By.ID , "showResult")
    ERROR = (By.ID , "showError")

    def transfer ( self , amount , source_account , destination_account ) :
        """Submit a transfer between dynamically discovered account IDs."""

        # Wait until source account is available
        self.wait.until(
            lambda driver : str(source_account) in [
                option.get_attribute("value")
                for option in Select(
                    driver.find_element(*self.FROM_ACCOUNT)
                ).options
            ]
        )

        # Wait until destination account is available
        self.wait.until(
            lambda driver : str(destination_account) in [
                option.get_attribute("value")
                for option in Select(
                    driver.find_element(*self.TO_ACCOUNT)
                ).options
            ]
        )

        # Select source and destination accounts
        Select(self.visible(self.FROM_ACCOUNT)).select_by_value(
            str(source_account)
        )

        Select(self.visible(self.TO_ACCOUNT)).select_by_value(
            str(destination_account)
        )

        # Enter transfer amount and submit
        self.type_text(self.AMOUNT , str(amount))
        self.click(self.SUBMIT)

        return self._wait_for_transfer_response()

    def _wait_for_transfer_response ( self ) :
        """Wait for either the success or error result without fixed sleeps."""

        try :
            self.wait.until(
                lambda driver : (
                                        driver.find_elements(*self.SUCCESS)
                                        and driver.find_element(*self.SUCCESS).is_displayed()
                                        and bool(driver.find_element(*self.SUCCESS).text.strip())
                                ) or (
                                        driver.find_elements(*self.ERROR)
                                        and driver.find_element(*self.ERROR).is_displayed()
                                        and bool(driver.find_element(*self.ERROR).text.strip())
                                )
            )
        except TimeoutException as exc :
            raise AssertionError("No transfer success or error response appeared.") from exc
        success_text = self.optional_text(self.SUCCESS)
        error_text = self.optional_text(self.ERROR)
        return {"success" : success_text , "error" : error_text}

    def transfer_was_successful ( self , response ) :
        return bool(response["success"]) and "complete" in response["success"].lower()
