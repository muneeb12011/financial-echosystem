import unittest
from modules.penny import PennyManager

class TestPennyManager(unittest.TestCase):
    
    def setUp(self):
        self.penny_manager = PennyManager()

    def test_initialize_pennies(self):
        # Test initialization of pennies
        self.penny_manager.initialize_pennies()
        self.assertEqual(len(self.penny_manager.pennies), 100, "Penny manager should initialize with 100 pennies.")

    def test_amplification(self):
        # Test that amplification increases the penny values
        self.penny_manager.initialize_pennies()
        initial_value = self.penny_manager.pennies[0]
        self.penny_manager.start_amplification()
        self.assertGreater(self.penny_manager.pennies[0], initial_value, "Penny value should increase after amplification.")

    def test_penny_value_bounds(self):
        # Test that penny values do not exceed a certain threshold (e.g., max cap)
        self.penny_manager.initialize_pennies()
        self.penny_manager.start_amplification()
        for penny in self.penny_manager.pennies:
            self.assertLessEqual(penny, 550000000000000, "Penny value should not exceed $550 trillion.")

    def test_amplification_state(self):
        # Test the state of pennies after multiple amplifications
        self.penny_manager.initialize_pennies()
        self.penny_manager.start_amplification()
        self.penny_manager.start_amplification()  # Simulate another round of amplification
        for penny in self.penny_manager.pennies:
            self.assertGreaterEqual(penny, 0.01, "Penny value should be at least $0.01 after amplification.")

    def test_amplification_effect_on_all_pennies(self):
        # Test that all pennies are amplified during the amplification process
        self.penny_manager.initialize_pennies()
        original_values = self.penny_manager.pennies.copy()
        self.penny_manager.start_amplification()
        for original_value, amplified_value in zip(original_values, self.penny_manager.pennies):
            self.assertGreater(amplified_value, original_value, "All penny values should increase after amplification.")

if __name__ == "__main__":
    unittest.main()
