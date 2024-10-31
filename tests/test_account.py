import unittest
from modules.account import AccountManager

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.api_keys = {
            'PAYPAL_EMAIL': "flight.right@gmail.com",  # Updated to reflect actual usage
            'NOVA_ACCOUNT_NUMBER': "102395044",  # Novo account number
            'NOVA_ROUTING_NUMBER': "211370150"  # Novo routing number
        }
        self.account_manager = AccountManager(self.api_keys)
        self.account_manager.initialize_accounts()  # Initialize accounts here

    def test_initialize_accounts(self):
        self.assertEqual(len(self.account_manager.accounts), 2)  # Adjusted to 2 for PayPal and Novo

    def test_update_balance(self):
        self.account_manager.update_balance('paypal', 50)
        self.assertEqual(self.account_manager.get_account_balance('paypal'), 50)

    def test_update_balance_invalid_account(self):
        with self.assertRaises(ValueError):
            self.account_manager.update_balance('invalid_account', 50)

    def test_get_paypal_account_email(self):
        self.assertEqual(self.account_manager.get_paypal_account_email(), "flight.right@gmail.com")

    def test_get_nova_account_number(self):
        self.assertEqual(self.account_manager.get_nova_account_number(), "102395044")

    def test_update_balance_exceed_limit(self):
        # Setting a balance limit and testing exceeding it
        self.account_manager = AccountManager(self.api_keys, max_balance=5000)  # Set a balance limit for testing
        self.account_manager.update_balance('paypal', 5000)  # Update to the limit
        with self.assertRaises(ValueError):
            self.account_manager.update_balance('paypal', 1)  # Exceeds limit by 1

    def test_balance_initialization(self):
        self.assertEqual(self.account_manager.get_account_balance('paypal'), 0)
        self.assertEqual(self.account_manager.get_account_balance('nova'), 0)  # Check nova as well

if __name__ == "__main__":
    unittest.main()
