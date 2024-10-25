import unittest
from unittest.mock import patch
from modules.transaction import TransactionManager
from modules.account import AccountManager

class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.api_keys = {
            'venmo': "venmo_access_token_here",
            'cashapp': "cashapp_secret_key_here",
            'paypal': "paypal_secret_here"
        }
        self.account_manager = AccountManager(self.api_keys)
        self.transaction_manager = TransactionManager(self.account_manager)
        self.account_manager.initialize_accounts()

    def test_process_payment_success(self):
        initial_balance = self.account_manager.get_account_balance('venmo')
        self.transaction_manager.process_payment('venmo', 100)  # Simulate a payment of $100
        self.assertEqual(self.account_manager.get_account_balance('venmo'), initial_balance + 100)

    def test_process_payment_invalid_account(self):
        with self.assertRaises(ValueError):
            self.transaction_manager.process_payment('invalid_account', 100)

    @patch('modules.transaction.requests.post')
    def test_process_payment_venmo(self, mock_post):
        # Mock the response from the Venmo API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'success'}

        self.transaction_manager.process_payment('venmo', 100)
        self.assertTrue(mock_post.called)
        self.assertEqual(mock_post.call_count, 1)

    @patch('modules.transaction.requests.post')
    def test_process_payment_paypal(self, mock_post):
        # Mock the response from the PayPal API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'success'}

        self.transaction_manager.process_payment('paypal', 100)
        self.assertTrue(mock_post.called)
        self.assertEqual(mock_post.call_count, 1)

    @patch('modules.transaction.requests.post')
    def test_process_payment_cashapp(self, mock_post):
        # Mock the response from the CashApp API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'status': 'success'}

        self.transaction_manager.process_payment('cashapp', 100)
        self.assertTrue(mock_post.called)
        self.assertEqual(mock_post.call_count, 1)

if __name__ == "__main__":
    unittest.main()
