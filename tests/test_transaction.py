import os
import unittest
from modules.transaction import TransactionManager
from modules.account import AccountManager
import requests

class TestTransactionManagerIntegration(unittest.TestCase):

    def setUp(self):
        # Use PayPal sandbox credentials for testing
        self.api_keys = {
            'paypal_client_id': os.getenv("PAYPAL_SANDBOX_CLIENT_ID"),  # Use environment variable
            'paypal_secret': os.getenv("PAYPAL_SANDBOX_SECRET"),  # Use environment variable
            'paypal_email': "your_sandbox_email@example.com",  # Your PayPal sandbox email
            'novo_account_number': "102395044",  # Novo account number
            'novo_routing_number': "211370150"  # Novo bank routing number
        }
        self.account_manager = AccountManager(self.api_keys)
        self.transaction_manager = TransactionManager(self.account_manager)
        self.account_manager.initialize_accounts()

    def test_process_payment_success(self):
        """Test processing a payment successfully."""
        initial_balance = self.account_manager.get_account_balance('paypal')
        self.transaction_manager.process_payment('paypal', 10)  # Simulate a payment of $10
        self.assertEqual(self.account_manager.get_account_balance('paypal'), initial_balance + 10)

    def test_process_payment_invalid_account(self):
        """Test processing payment for an invalid account."""
        with self.assertRaises(ValueError):
            self.transaction_manager.process_payment('invalid_account', 100)

    def test_process_payment_paypal_real(self):
        """Test processing payment through PayPal with real integration."""
        response = self.transaction_manager.process_payment('paypal', 10)  # Simulate a payment of $10
        self.assertEqual(response['status'], 'success')

    def test_process_payment_invalid_amount(self):
        """Test processing payment with an invalid amount (negative)."""
        with self.assertRaises(ValueError):
            self.transaction_manager.process_payment('paypal', -50)

    def test_account_balance_after_transaction(self):
        """Test account balance after a payment transaction."""
        initial_balance = self.account_manager.get_account_balance('paypal')
        self.transaction_manager.process_payment('paypal', 5)  # Simulate a payment of $5
        self.assertEqual(self.account_manager.get_account_balance('paypal'), initial_balance + 5)

if __name__ == "__main__":
    unittest.main()
