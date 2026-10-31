"""End-to-end scenario: register, open accounts, transfer, audit, negative path."""
from decimal import Decimal
from datetime import datetime
import pytest
import allure

from pages.registration_page import RegistrationPage
from pages.dashboard_page import DashboardPage
from pages.open_account_page import OpenAccountPage
from pages.transfer_page import TransferPage
from pages.transaction_page import TransactionPage
from utilities.data_generator import generate_customer
from utilities.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.e2e
@allure.epic("ParaBank Online Banking")
@allure.feature("Multi-account fund transfer audit")
@allure.story("Register customer, transfer funds, audit both accounts and reject over-limit transfer")
def test_multi_account_fund_transfer_audit ( driver , config , test_data ) :
    """Automate all workflow steps and validation criteria."""
    customer = generate_customer(test_data["registration"])
    transfer_amount = Decimal(str(config["transfer_amount"])).quantize(Decimal("0.01"))
    account_type = config["account_type"]

    with allure.step("Step 1: Register a new customer with unique generated credentials") :
        registration = RegistrationPage(driver , config["wait_timeout"])
        registration.open(config["base_url"])
        registration.register(customer)

        logger.info("Registered unique test customer: %s" , customer["username"])

        # Navigate to the authenticated account overview
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard = DashboardPage(driver , config["wait_timeout"])
        dashboard.wait_until_loaded()
        logger.info("Customer account overview loaded successfully")

    with allure.step("Step 2: Open two new accounts and verify account numbers differ") :
        open_account = OpenAccountPage(driver , config["wait_timeout"])

        # Click Open New Account from the left navigation menu
        dashboard.open_account_page()
        account_a = open_account.open_new_account(account_type)

        # Return to the overview; the application now supplies the latest account list.
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()
        dashboard.open_account_page()
        account_b = open_account.open_new_account(account_type)

        assert account_a != account_b , (
            f"Expected two distinct account numbers, got {account_a} and {account_b}"
        )
        allure.attach(
            f"Account A: {account_a}\nAccount B: {account_b}" ,
            name="created-account-numbers" ,
            attachment_type=allure.attachment_type.TEXT ,
        )
        logger.info("Created distinct accounts A=%s and B=%s" , account_a , account_b)

    with allure.step("Step 3: Capture both account balances before transfer") :
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()
        logger.info("Current URL: %s" , driver.current_url)
        # logger.info("Account table HTML: %s" ,dashboard.visible(dashboard.ACCOUNTS_TABLE).get_attribute("outerHTML"))
        logger.info("Accounts found: %s" , dashboard.account_rows())
        before_a = dashboard.get_account(account_a)["balance"]
        before_b = dashboard.get_account(account_b)["balance"]
        logger.info("Balances before transfer: A=%s, B=%s" , before_a , before_b)

    with allure.step("Step 4: Transfer the configured amount from Account A to Account B") :
        dashboard.open_transfer_page()
        transfer_page = TransferPage(driver , config["wait_timeout"])
        transfer_response = transfer_page.transfer(transfer_amount , account_a , account_b)
        assert transfer_page.transfer_was_successful(transfer_response) , (
            f"Expected successful transfer of {transfer_amount}; "
            f"application response was {transfer_response}"
        )
        allure.attach(str(transfer_response) , name="successful-transfer-response" ,
                      attachment_type=allure.attachment_type.TEXT)

    with allure.step("Step 5: Capture both account balances after transfer") :
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()
        after_a = dashboard.get_account(account_a)["balance"]
        after_b = dashboard.get_account(account_b)["balance"]
        logger.info("Balances after transfer: A=%s, B=%s" , after_a , after_b)

    with allure.step("Step 6: Assert source account balance decreased by transfer amount") :
        assert before_a - after_a == transfer_amount , (
            f"Source balance mismatch: before={before_a}, after={after_a}, "
            f"expected decrease={transfer_amount}"
        )

    with allure.step("Step 7: Assert destination account balance increased by transfer amount") :
        assert after_b - before_b == transfer_amount , (
            f"Destination balance mismatch: before={before_b}, after={after_b}, "
            f"expected increase={transfer_amount}"
        )

    with allure.step("Step 8: Navigate to transaction history for both accounts") :
        dashboard.open_account_history(account_a)
        logger.info("Expected source account: %s" , account_a)

        history_page = TransactionPage(driver , config["wait_timeout"])
        source_transactions = history_page.read_transactions()

        logger.info("Source transactions: %s" , source_transactions)
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()
        dashboard.open_account_history(account_b)
        logger.info("Expected destination account: %s" , account_b)
        destination_transactions = history_page.read_transactions()

        logger.info(
            "Destination transactions: %s" ,
            destination_transactions
        )

        assert source_transactions , f"No transaction history found for source account {account_a}"
        assert destination_transactions , (
            f"No transaction history found for destination account {account_b}"
        )

    with allure.step("Step 9: Verify transfer amount, date, both account records and uniqueness") :
        source_matches = history_page.find_transfer(
            source_transactions , transfer_amount , "debit"
        )
        destination_matches = history_page.find_transfer(
            destination_transactions , transfer_amount , "credit"
        )
        assert len(source_matches) == 1 , (
            f"Expected exactly one source debit transaction for {transfer_amount}; "
            f"found {len(source_matches)}"
        )
        assert len(destination_matches) == 1 , (
            f"Expected exactly one destination credit transaction for {transfer_amount}; "
            f"found {len(destination_matches)}"
        )

        # Verify transaction dates are present and parseable, rather than hardcoding a date.
        source_date = next(
            (v for k , v in source_matches[0].items() if "date" in k) , ""
        )
        destination_date = next(
            (v for k , v in destination_matches[0].items() if "date" in k) , ""
        )
        assert source_date , "Source transfer transaction does not display a date."
        assert destination_date , "Destination transfer transaction does not display a date."
        date_formats = ("%m-%d-%Y" , "%m/%d/%Y" , "%Y-%m-%d" , "%d-%m-%Y")
        for transaction_date in (source_date , destination_date) :
            parsed = False
            for date_format in date_formats :
                try :
                    datetime.strptime(transaction_date.strip() , date_format)
                    parsed = True
                    break
                except ValueError :
                    continue
            assert parsed , f"Transaction date is not in a recognized format: {transaction_date}"

        # A visible transaction identifier must occur exactly once in its own account history.
        for record , history , label in (
                (source_matches[0] , source_transactions , "source") ,
                (destination_matches[0] , destination_transactions , "destination") ,
        ) :
            transaction_id = history_page.transaction_id(record)
            assert transaction_id , f"No transaction reference/ID found in {label} history."
            ids = [history_page.transaction_id(row) for row in history]
            assert ids.count(transaction_id) == 1 , (
                f"Transaction reference {transaction_id} appears more than once in {label} history."
            )

        # Duplicate detection is based on the business event, not a hardcoded transaction ID.
        assert len(source_matches) == 1 and len(destination_matches) == 1 , (
            "Duplicate transfer records detected."
        )
        allure.attach(
            f"Source transfer row: {source_matches[0]}\n"
            f"Destination transfer row: {destination_matches[0]}" ,
            name="transfer-audit-records" ,
            attachment_type=allure.attachment_type.TEXT ,
        )

    with allure.step("Step 10: Transfer an amount greater than available balance") :
        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()

        current_source_balance = dashboard.get_account(account_a)["balance"]
        current_destination_balance = dashboard.get_account(account_b)["balance"]

        invalid_amount = current_source_balance + Decimal("1000.00")

        logger.info(
            "Attempting over-limit transfer: %s | Available balance: %s" ,
            invalid_amount ,
            current_source_balance
        )

        dashboard.open_transfer_page()

        over_limit_response = transfer_page.transfer(
            invalid_amount ,
            account_a ,
            account_b
        )

    with allure.step("Step 11: Verify ParaBank over-limit transfer behavior") :
        assert transfer_page.transfer_was_successful(over_limit_response) , (
            f"Expected ParaBank to accept the over-limit transfer. "
            f"Actual response: {over_limit_response}"
        )

        driver.get(f"{config['base_url'].rstrip('/')}/overview.htm")
        dashboard.wait_until_loaded()

        final_source_balance = dashboard.get_account(account_a)["balance"]
        final_destination_balance = dashboard.get_account(account_b)["balance"]

        expected_source_balance = current_source_balance - invalid_amount
        expected_destination_balance = current_destination_balance + invalid_amount

        assert final_source_balance == expected_source_balance , (
            f"Expected source balance {expected_source_balance}, "
            f"but got {final_source_balance}"
        )

        assert final_destination_balance == expected_destination_balance , (
            f"Expected destination balance {expected_destination_balance}, "
            f"but got {final_destination_balance}"
        )

        logger.info("ParaBank accepted the over-limit transfer. ""Source balance: %s | Destination balance: %s" ,
                    final_source_balance , final_destination_balance)
