import unittest
import asyncio
from modules.escrow import EscrowManager

class TestEscrowManager(unittest.TestCase):
    
    def setUp(self):
        """Set up a new EscrowManager instance for each test."""
        self.escrow_manager = EscrowManager()

    def test_manage_escrow_valid(self):
        """Test managing escrow with valid parameters."""
        result = self.escrow_manager.manage_escrow("user_123", 300, hold_time_seconds=1)
        self.assertTrue(result)
        self.assertGreater(len(self.escrow_manager.escrowed_funds["user_123"]), 0)

    def test_manage_escrow_invalid_amount(self):
        """Test managing escrow with an invalid amount (exceeds max limit)."""
        result = self.escrow_manager.manage_escrow("user_123", 1_500_000)  # Exceeds max limit
        self.assertFalse(result)

    def test_manage_escrow_zero_amount(self):
        """Test managing escrow with a zero amount."""
        result = self.escrow_manager.manage_escrow("user_123", 0)
        self.assertFalse(result)

    def test_release_funds(self):
        """Test that funds are released after their hold time expires."""
        asyncio.run(self.escrow_manager.manage_escrow("user_123", 300, hold_time_seconds=1))  # Hold for 1 second
        asyncio.run(asyncio.sleep(1))  # Wait for hold time to pass
        asyncio.run(self.escrow_manager.release_funds())  # Release funds
        self.assertEqual(self.escrow_manager.get_escrow_balance("user_123"), 0)

    def test_get_escrow_balance(self):
        """Test getting the escrow balance for a user."""
        asyncio.run(self.escrow_manager.manage_escrow("user_123", 300))
        balance = self.escrow_manager.get_escrow_balance("user_123")
        self.assertEqual(balance, 300)

    def test_get_escrow_balance_no_funds(self):
        """Test getting escrow balance when no funds are held."""
        balance = self.escrow_manager.get_escrow_balance("user_123")
        self.assertEqual(balance, 0)

    def test_can_release(self):
        """Test the can_release method."""
        asyncio.run(self.escrow_manager.manage_escrow("user_123", 300, hold_time_seconds=1))
        asyncio.run(asyncio.sleep(1))  # Wait for hold time to pass
        self.assertTrue(self.escrow_manager.can_release("user_123"))

    def test_can_release_no_funds(self):
        """Test can_release method when no funds are held."""
        self.assertFalse(self.escrow_manager.can_release("user_123"))

    def test_remove_escrow(self):
        """Test removing an escrow entry."""
        self.escrow_manager.manage_escrow("user_123", 300)
        result = self.escrow_manager.remove_escrow("user_123", 300)
        self.assertTrue(result)
        self.assertEqual(self.escrow_manager.get_escrow_balance("user_123"), 0)

    def test_remove_nonexistent_escrow(self):
        """Test removing a non-existent escrow entry."""
        result = self.escrow_manager.remove_escrow("user_123", 500)  # Non-existent entry
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
