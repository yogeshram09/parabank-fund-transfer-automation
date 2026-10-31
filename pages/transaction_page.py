"""Page Object for transaction history and row-level audit data."""
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utilities.money import parse_money


class TransactionPage(BasePage) :
    TRANSACTION_TABLE = (By.ID , "transactionTable")

    def read_transactions ( self ) :
        """Read transaction rows using actual table column headings."""

        table = self.visible(self.TRANSACTION_TABLE)

        # Read only actual TH elements, never transaction TD elements.
        header_cells = table.find_elements(
            By.XPATH , ".//tr/th"
        )

        headers = [cell.text.strip().lower() for cell in header_cells]

        # ParaBank normally has these four transaction columns.
        if not headers :
            headers = ["date" , "transaction" , "debit (-)" , "credit (+)"]

        # Wait until transaction data is available.
        self.wait.until(
            lambda driver : len(
                driver.find_elements(
                    By.XPATH ,
                    "//table[@id='transactionTable']//tr[td]"
                )
            ) > 0
        )

        rows = table.find_elements(By.XPATH , ".//tr[td]")

        transactions = []

        for row in rows :
            cells = row.find_elements(By.TAG_NAME , "td")
            values = [cell.text.strip() for cell in cells]

            if not values :
                continue

            if len(values) != len(headers) :
                print("Header count:" , len(headers))
                print("Row values:" , values)
                continue

            record = dict(zip(headers , values))

            # Capture transaction reference from its link, if available.
            links = row.find_elements(By.CSS_SELECTOR , "a[href]")
            reference = ""

            if links :
                href = links[0].get_attribute("href") or ""

                if "id=" in href :
                    reference = href.split("id=" , 1)[1].split("&" , 1)[0]

            record["_reference"] = reference
            record["_raw"] = values

            transactions.append(record)

        print("Transaction headers:" , headers)
        print("Transactions extracted:" , transactions)

        return transactions

    @staticmethod
    def find_transfer ( transactions , amount , direction ) :
        """Find one matching debit/credit row; direction is 'debit' or 'credit'."""
        amount_columns = [
            key for key in transactions[0].keys()
            if key == direction or direction in key
        ] if transactions else []
        target_columns = amount_columns or [
            key for key in transactions[0].keys()
            if ("debit" in key if direction == "debit" else "credit" in key)
        ] if transactions else []

        matches = []
        for record in transactions :
            description = " ".join(
                str(value) for key , value in record.items() if not key.startswith("_")
            ).lower()
            amount_match = False
            for key in target_columns :
                try :
                    amount_match = parse_money(record[key]) == amount
                except (ValueError , KeyError) :
                    continue
            if amount_match and any(word in description for word in ("transfer" , "sent" , "received")) :
                matches.append(record)
        return matches

    @staticmethod
    def transaction_id ( record ) :
        """Return the UI transaction ID, or a deterministic row fingerprint.

        Some ParaBank builds do not expose a transaction ID column in the history
        table. In that case the visible row fingerprint still lets us assert that
        the matching transfer row is not duplicated in that account history.
        """
        if record.get("_reference") :
            return str(record["_reference"]).strip()
        for key , value in record.items() :
            if "id" in key and not key.startswith("_") and str(value).strip() :
                return str(value).strip()
        visible_values = [
            f"{key}={value}" for key , value in record.items()
            if not key.startswith("_") and str(value).strip()
        ]
        return "|".join(visible_values)
