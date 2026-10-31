"""Page Object for the authenticated account overview."""
from decimal import Decimal
from selenium.webdriver.common.by import By

from conftest import logger
from pages.base_page import BasePage
from utilities.money import parse_money


class DashboardPage(BasePage) :
    ACCOUNTS_TABLE = (By.ID , "accountTable")
    OPEN_ACCOUNT_LINK = (By.LINK_TEXT , "Open New Account")
    TRANSFER_LINK = (By.LINK_TEXT , "Transfer Funds")
    LOGOUT_LINK = (By.LINK_TEXT , "Log Out")

    def wait_until_loaded ( self ) :
        self.visible(self.ACCOUNTS_TABLE)
        self.wait.until(
            lambda driver : len(
                driver.find_elements(
                    By.XPATH ,
                    "//table[@id='accountTable']//a[contains(@href, 'activity.htm')]"
                )
            ) > 0
        )

    def account_rows ( self ) :
        """Read account IDs and balances from the overview table."""

        table = self.visible(self.ACCOUNTS_TABLE)

        # Read all rows directly from the table
        rows = table.find_elements(By.XPATH , ".//tr")

        accounts = []

        for row in rows :
            cells = row.find_elements(By.XPATH , "./td")

            if len(cells) < 2 :
                continue

            account_links = row.find_elements(
                By.XPATH , ".//a[contains(@href, 'activity.htm')]"
            )

            if not account_links :
                continue

            account_id = account_links[0].get_attribute("textContent").strip()
            balance_text = cells[1].get_attribute("textContent").strip()

            accounts.append({
                "id" : account_id ,
                "balance" : parse_money(balance_text)
            })

        logger.info("Accounts found: %s" , accounts)

        return accounts

    def get_account ( self , account_id ) :
        """Find account by ID, ignoring accidental whitespace."""
        expected_id = str(account_id).strip()
        accounts = self.account_rows()
        matches = [account for account in accounts if account["id"].strip() == expected_id]
        assert matches , (
            f"Account {expected_id!r} not found. "
            f"Available account IDs: {[a['id'] for a in accounts]}"
        )
        return matches[0]

    def open_account_page ( self ) :
        self.click(self.OPEN_ACCOUNT_LINK)

    def open_transfer_page ( self ) :
        self.click(self.TRANSFER_LINK)

    def open_account_history ( self , account_id ) :
        """Open the requested account history and verify the account number."""

        locator = (
            By.XPATH ,
            f"//table[@id='accountTable']//a[normalize-space()='{account_id}']"
        )

        self.click(locator)

        self.wait_for_url_contains("activity.htm")

        # Verify that the requested account's history actually opened
        self.wait.until(
            lambda driver : str(account_id) in driver.find_element(
                By.TAG_NAME , "body"
            ).text
        )

        logger.info(
            "Successfully opened transaction history for account %s" ,
            account_id
        )
