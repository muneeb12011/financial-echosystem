import logging
from datetime import datetime, timedelta

class EscrowManager:
    def __init__(self):
        self.escrowed_funds = []  # List to hold escrowed funds

    def manage_escrow(self, amount, hold_time_seconds):
        """Manage escrow by holding the specified amount for a certain duration."""
        escrow_entry = {
            'amount': amount,
            'release_time': datetime.now() + timedelta(seconds=hold_time_seconds)
        }
        self.escrowed_funds.append(escrow_entry)
        logging.info(f"Managed escrow: {amount} held for {hold_time_seconds} seconds.")

    def release_funds(self):
        """Release funds from escrow after their hold time expires."""
        logging.info("Attempting to release funds from escrow.")
        current_time = datetime.now()
        released_funds = []

        for escrow_entry in self.escrowed_funds[:]:  # Iterate over a copy of the list
            if current_time >= escrow_entry['release_time']:
                released_funds.append(escrow_entry['amount'])
                logging.debug(f"Released {escrow_entry['amount']} from escrow.")
                self.escrowed_funds.remove(escrow_entry)  # Remove the released fund

        if released_funds:
            logging.info(f"Released funds: {released_funds}")
        else:
            logging.info("No funds to release from escrow.")

    def get_escrow_balance(self):
        """Return the total balance of escrowed funds."""
        total_balance = sum(entry['amount'] for entry in self.escrowed_funds)
        logging.info(f"Current escrow balance: {total_balance}")
        return total_balance

    def can_release(self):
        """Check if any funds can be released."""
        current_time = datetime.now()
        can_release_funds = [entry for entry in self.escrowed_funds if current_time >= entry['release_time']]
        return len(can_release_funds) > 0
