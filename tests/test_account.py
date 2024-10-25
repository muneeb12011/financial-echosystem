import unittest
from modules.account import AccountManager

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.api_keys = {
            'VENMO_USER_ID': "venmo_access_token_here",
            'CASHAPP_ACCOUNT_NUMBER': "cashapp_secret_key_here",
            'PAYPAL_EMAIL': "paypal_secret_here"
        }
        self.account_manager = AccountManager(self.api_keys)
        self.account_manager.initialize_accounts()  # Initialize accounts here

    def test_initialize_accounts(self):
        self.assertEqual(len(self.account_manager.accounts), 4)  # Adjusted to 4

    def test_update_balance(self):
        self.account_manager.update_balance('venmo', 50)
        self.assertEqual(self.account_manager.get_account_balance('venmo'), 50)

    def test_update_balance_invalid_account(self):
        with self.assertRaises(ValueError):
            self.account_manager.update_balance('invalid_account', 50)

    def test_get_venmo_account_number(self):
        self.assertEqual(self.account_manager.get_venmo_account_number(), "venmo_access_token_here")

    def test_get_cashapp_account_number(self):
        self.assertEqual(self.account_manager.get_cashapp_account_number(), "cashapp_secret_key_here")

    def test_get_paypal_account_email(self):
        self.assertEqual(self.account_manager.get_paypal_account_email(), "paypal_secret_here")

    def test_update_balance_exceed_limit(self):
        # Setting a balance limit and testing exceeding it
        self.account_manager = AccountManager(self.api_keys, max_balance=5000)  # Set a balance limit for testing
        self.account_manager.update_balance('venmo', 5000)  # Update to the limit
        with self.assertRaises(ValueError):
            self.account_manager.update_balance('venmo', 1)  # Exceeds limit by 1

    def test_balance_initialization(self):
        self.assertEqual(self.account_manager.get_account_balance('venmo'), 0)
        self.assertEqual(self.account_manager.get_account_balance('cashapp'), 0)
        self.assertEqual(self.account_manager.get_account_balance('paypal'), 0)
        self.assertEqual(self.account_manager.get_account_balance('nova'), 0)  # Check nova as well

if __name__ == "__main__":
    unittest.main()
