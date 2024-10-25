import unittest
from unittest.mock import patch, MagicMock
from modules.scheduler import Scheduler
from modules.transaction import TransactionManager
from modules.account import AccountManager
from modules.escrow import EscrowManager

class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = Scheduler()
        self.account_manager = AccountManager({})
        self.escrow_manager = EscrowManager()
        self.transaction_manager = TransactionManager(self.account_manager)
        self.account_manager.initialize_accounts()
        self.escrow_manager.manage_escrow()

    @patch('modules.scheduler.Timer')
    def test_schedule_releases(self, mock_timer):
        # Mock the Timer to simulate time passing without actual waiting
        mock_timer.return_value.start = MagicMock()
        mock_timer.return_value.cancel = MagicMock()

        # Schedule releases
        self.scheduler.schedule_releases(self.transaction_manager, self.escrow_manager)

        # Assert that the Timer was started
        mock_timer.assert_called_once()
        self.assertTrue(mock_timer.return_value.start.called, "The Timer should have started.")

    def test_release_funds(self):
        # Manually call the release method and check if funds are released
        initial_funds = len(self.escrow_manager.escrowed_funds)
        self.escrow_manager.release_funds()  # Call the release method
        self.assertLess(len(self.escrow_manager.escrowed_funds), initial_funds, "Funds should be released from escrow.")

    def test_transaction_processing(self):
        # Test if the transaction manager processes a transaction correctly
        self.transaction_manager.process_transaction({'amount': 1000, 'account_id': 'venmo'})  # Simulate a transaction
        # Add assertions to check if the transaction was successful
        # (This assumes you have a way to verify that the transaction was processed)

if __name__ == "__main__":
    unittest.main()
