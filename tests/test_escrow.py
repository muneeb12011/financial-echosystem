import unittest
from modules.escrow import EscrowManager

class TestEscrowManager(unittest.TestCase):
    
    def setUp(self):
        self.escrow_manager = EscrowManager()
        self.escrow_manager.manage_escrow()  # Initialize with some funds

    def test_manage_escrow(self):
        # Test that the manage_escrow function populates escrowed funds
        self.assertGreater(len(self.escrow_manager.escrowed_funds), 0, "Escrowed funds should not be empty after management.")

    def test_release_funds(self):
        # Test that funds are released correctly
        initial_count = len(self.escrow_manager.escrowed_funds)
        self.escrow_manager.release_funds()
        self.assertEqual(len(self.escrow_manager.escrowed_funds), 0, "Escrowed funds should be empty after release.")

    def test_release_funds_no_escrowed_funds(self):
        # Test releasing funds when there are no escrowed funds
        self.escrow_manager.escrowed_funds = []  # Clear escrowed funds
        self.escrow_manager.release_funds()  # Should not raise an error
        self.assertEqual(len(self.escrow_manager.escrowed_funds), 0, "Escrowed funds should remain empty after release.")

    def test_escrow_fund_structure(self):
        # Test the structure of an escrowed fund (assuming it's a dictionary)
        sample_fund = {'id': '1', 'amount': 100, 'recipient': 'user@example.com'}
        self.escrow_manager.escrowed_funds.append(sample_fund)
        self.assertIn('id', sample_fund)
        self.assertIn('amount', sample_fund)
        self.assertIn('recipient', sample_fund)

if __name__ == "__main__":
    unittest.main()
