# ParaBank – Multi-Account Fund Transfer Audit



## What this project automates

1. Registers a unique customer for each execution.
2. Opens two new accounts and asserts that their account numbers differ.
3. Captures both balances before the transfer.
4. Transfers a configurable amount from Account A to Account B.
5. Captures balances after the transfer and asserts exact debit/credit arithmetic.
6. Opens both account histories.
7. Verifies one matching debit and one matching credit, with visible and parseable dates.
8. Checks transaction identifiers for uniqueness in each account history.
9. Attempts an over-limit transfer and verifies that it is not accepted and neither balance changes.

The six assessment validation criteria are implemented as assertions in the end-to-end test.

## Technology

- Python 3.10+
- Selenium 4 (Selenium Manager resolves browser drivers)
- Pytest
- Page Object Model (POM)
- Allure Pytest reporting
- PyYAML configuration
- Faker for unique synthetic customer data
- Python logging

## PyCharm setup

1. Extract/clone this repository and open the project root in PyCharm.
2. Configure a Python 3.10+ interpreter (a project virtual environment is recommended).
3. Open the PyCharm terminal and run:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Install Google Chrome or Firefox. Selenium Manager will attempt to obtain the matching driver automatically.
5. Copy `.env.example` to `.env` if you want environment-specific overrides.

## Configuration and dynamic data

Default values live in `config/config.yaml`; registration defaults live in `data/test_data.yaml`.
The customer name, username, and synthetic SSN are generated for every run. Account numbers and balances are always read from the application UI.

Environment variables override YAML configuration:

| Variable | Purpose | Example |
|---|---|---|
| `BASE_URL` | ParaBank base URL | `https://parabank.parasoft.com/parabank` |
| `BROWSER` | Browser | `chrome` / `firefox` |
| `HEADLESS` | Headless execution | `true` / `false` |
| `TRANSFER_AMOUNT` | Transfer amount | `250.00` |
| `ACCOUNT_TYPE` | Account type exposed by app | `CHECKING` / `SAVINGS` |
| `WAIT_TIMEOUT` | Explicit wait seconds | `15` |

The transfer amount is configurable and defaults to `$50.00` as a conservative demo value. You can set `$250.00` (or another amount) in YAML or `TRANSFER_AMOUNT` when the selected source account has sufficient funds. The test never assumes the expected post-transfer balance; it calculates it from the live before/after UI values using `Decimal`.

## Run tests

Run the end-to-end assignment:

```bash
pytest -m e2e
```

Run in headless mode:

```bash
HEADLESS=true pytest -m e2e
```

Override the transfer amount:

```bash
TRANSFER_AMOUNT=125.50 pytest -m e2e
```

Windows PowerShell example:

```powershell
$env:TRANSFER_AMOUNT="125.50"
$env:HEADLESS="false"
pytest -m e2e
```

## Allure report

Generate raw results:

```bash
pytest -m e2e --alluredir=allure-results
```

Install the Allure command-line tool separately, then create and open the HTML report:

```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

The pytest fixture attaches a screenshot and current URL when a test fails. Allure steps describe each assessment phase.

## Logs and diagnostics

- `logs/automation.log` contains timestamped execution logs.
- Allure contains step-level results and failure screenshots.
- Pytest output shows assertion messages for failed validations.

## Design decisions and assumptions

- The test creates a new customer every run to avoid dependence on pre-existing credentials.
- The account numbers are read from the ParaBank response and asserted to be distinct.
- The first available funding account exposed by ParaBank is selected when opening each new account. The application owns the actual account IDs and starting balances.
- Account A and Account B are the two newly opened accounts. The configured transfer amount is transferred from A to B.
- Currency calculations use `Decimal`, not binary floating point.
- Transaction history is interpreted using its visible column headers. The test expects a debit entry for the source account and a credit entry for the destination account.
- ParaBank's UI may not expose a shared transfer-reference field or transaction-ID column in the account-history table. The test extracts the application-generated transaction ID from a transaction-details link when available; otherwise it creates a deterministic fingerprint from the visible row and asserts that the matching transfer row occurs only once in that account history. If the live UI exposes a separate shared reference, extend the audit to assert that exact reference.
- Transaction dates are checked for presence and parseability instead of hardcoding the execution date or locale.
- An over-limit transfer must not be reported as successful and must not change either account balance.
- This is a demo banking site. Use synthetic data only; never enter real SSNs, passwords, or financial information.

## Important pre-submission verification

The public registration page can be inspected without logging in, but account creation, transfers, and histories require an authenticated browser session. Run the suite against the live site before submission. If the site's DOM or business behavior differs from the assumptions above, update the corresponding Page Object locators and assertions based on the observed UI, then rerun until the report is clean.

## Git workflow

Make incremental commits rather than one large final commit:

```bash
git init
git add README.md requirements.txt pytest.ini .gitignore config data
git commit -m "Add project configuration and test documentation"

git add pages
git commit -m "Add ParaBank page objects using Selenium"

git add utilities conftest.py
git commit -m "Add dynamic data, logging and browser fixtures"

git add tests
git commit -m "Implement multi-account transfer audit scenario"

git add .
git commit -m "Finalize Allure reporting and execution setup"
```

Add your own remote and push:

```bash
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Do not commit `.env`, real credentials, `allure-results`, screenshots, logs, or generated reports.
