import logging
from decimal import Decimal
import random

class PennyManager:
    def __init__(self):
        self.pennies = []
        self.amplification_rate = Decimal('2.0')
        self.amplification_history = []  # To track amplification history

    def initialize_pennies(self, count=100):
        """Initialize pennies with a given count, each worth $0.01."""
        logging.info(f"Initializing {count} pennies.")
        self.pennies = [Decimal('0.01')] * count

    def start_amplification(self):
        """Start the amplification process for all pennies."""
        logging.info("Starting amplification process.")
        try:
            for i in range(len(self.pennies)):
                # Optionally use a dynamic amplification rate based on some criteria
                dynamic_rate = self.get_dynamic_amplification_rate(i)
                self.pennies[i] *= dynamic_rate
                self.amplification_history.append((self.pennies[i], dynamic_rate))  # Track the history
                logging.debug(f"Amplified penny {i}: {self.pennies[i]} using rate {dynamic_rate}")
            logging.info("Amplification process completed.")
        except Exception as e:
            logging.error(f"Error during amplification: {e}")

    def get_dynamic_amplification_rate(self, index):
        """Get a dynamic amplification rate based on index or other criteria."""
        # Here you could introduce randomness or other logic
        return self.amplification_rate * Decimal(random.uniform(0.9, 1.1))  # ±10% variation

    def set_amplification_rate(self, new_rate):
        """Set a new amplification rate."""
        if new_rate <= 0:
            logging.error("Amplification rate must be greater than zero.")
            raise ValueError("Amplification rate must be greater than zero.")
        logging.info(f"Setting amplification rate from {self.amplification_rate} to {new_rate}.")
        self.amplification_rate = Decimal(new_rate)

    def total_value(self):
        """Return the total value of all pennies."""
        total = sum(self.pennies)
        logging.info(f"Total value of pennies: {total}")
        return total

    def reset_pennies(self):
        """Reset the pennies to their initial state."""
        logging.info("Resetting pennies to initial state.")
        self.initialize_pennies()

    def get_amplification_history(self):
        """Return the history of amplification for auditing purposes."""
        return self.amplification_history
