import logging

class AccountManager:
    def __init__(self, api_keys, max_balance=10000.0):  # Added max_balance parameter
        self.api_keys = api_keys
        self.accounts = {}
        self.max_balance = max_balance  # Set the max balance limit
        self.initialize_accounts()

    def initialize_accounts(self):
        logging.info("Initializing accounts.")
        # Set initial balances for the accounts
        self.accounts = {
            'venmo': 0.0,
            'paypal': 0.0,
            'cashapp': 0.0,
            'nova': 0.0  # Added Nova account
        }
        logging.info(f"Accounts initialized: {self.accounts}")

    def get_account_balance(self, account_id):
        balance = self.accounts.get(account_id, 0.0)
        logging.info(f"Retrieved balance for {account_id}: {balance}")
        return balance

    def update_balance(self, account_id, amount):
        if account_id in self.accounts:
            new_balance = self.accounts[account_id] + amount
            if new_balance < 0:
                logging.error(f"Insufficient balance for {account_id}. Current balance: {self.accounts[account_id]}, Attempted update: {amount}")
                raise ValueError(f"Insufficient funds in account {account_id}.")
            if new_balance > self.max_balance:  # Check for balance exceeding the cap
                logging.error(f"Balance exceeds the limit for {account_id}. Current balance: {self.accounts[account_id]}, Attempted update: {amount}")
                raise ValueError(f"Balance exceeds the limit for {account_id}.")
            self.accounts[account_id] = new_balance
            logging.info(f"Updated {account_id} balance: {self.accounts[account_id]}")
        else:
            logging.error(f"Account {account_id} does not exist.")
            raise ValueError(f"Account {account_id} not found.")

    # Nova-specific account details
    def get_nova_account_details(self):
        return {
            "account_number": "102395044",  # Nova account number
            "routing_number": "211370150",  # Nova routing number
        }

    # Venmo account details (from API keys)
    def get_venmo_account_number(self):
        return self.api_keys['VENMO_USER_ID']  # Fetch Venmo account ID from API keys

    # CashApp account details (from API keys)
    def get_cashapp_account_number(self):
        return self.api_keys['CASHAPP_ACCOUNT_NUMBER']  # Fetch CashApp account number from API keys

    # PayPal account details (from API keys)
    def get_paypal_account_email(self):
        return self.api_keys['PAYPAL_EMAIL']  # Fetch PayPal email from API keys
