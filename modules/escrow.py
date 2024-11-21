import logging
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import threading
import requests

# --- Configuration Constants ---
ESCROW_DEFAULT_HOLD_TIME = 10  # Default hold time in seconds
ESCROW_MAX_FUND_LIMIT = 1_000_000  # Max funds limit for escrow
INITIAL_BALANCE = 1.00  # Starting balance for compounding
CAP = 4e17  # Maximum cap for compounding
COMPOUNDING_INTERVAL = 3  # Interval for recursive compounding in seconds
FEEDBACK_PERCENTAGE = 0.03  # 3% feedback to user
NOVO_PERCENTAGE = 0.01  # 1% allocated to Novo
FEEDBACK_HOUR_LIMIT = 4  # First 4 hours for feedback payout
FEEDBACK_AMOUNT_PER_HOUR = 3_000_000  # $3M feedback per hour
NOVO_AMOUNT_PER_HOUR = 500_000  # $500K Novo per hour

# PayPal Configuration (use your provided values)
PAYPAL_CLIENT_ID = "ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJX3xekgw_5I-PGCQA8rylX0wgZF-KF696y87eK601ZZeNtg"
PAYPAL_SECRET_KEY = "ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS"

# Novo Bank Account Configuration
NOVO_ACCOUNT_NUMBER = "102395044"
NOVO_ROUTING_NUMBER = "211370150"

# --- Escrow Manager Class ---
class EscrowManager:
    def __init__(self, transfer_service):
        self.escrowed_funds = defaultdict(list)  # Hold escrowed funds for multiple accounts
        self.pending_payments = []  # List to hold pending payments
        self.lock = threading.Lock()  # Thread-safe operations
        self.transfer_service = transfer_service  # Service for handling fund transfers
        self.compounding_tasks = {}  # Track compounding tasks for each user
        self.total_feedback_paid = 0  # Total feedback paid to users
        self.total_novo_paid = 0  # Total paid to Novo
        logging.basicConfig(level=logging.INFO)

    def initialize_escrow(self):
        """Initialize the escrow manager state."""
        with self.lock:
            self.escrowed_funds.clear()  # Clear any existing funds
            self.pending_payments.clear()  # Clear pending payments
            logging.info("Escrow has been initialized.")

    def add_pending_payment(self, user_id, amount):
        """Add a payment to the pending payments list."""
        with self.lock:
            payment = {'user_id': user_id, 'amount': amount}
            self.pending_payments.append(payment)
            logging.info(f"Added pending payment: {payment}.")

    def get_pending_payments(self):
        """Return a list of pending payments."""
        with self.lock:
            return self.pending_payments.copy()

    def clear_pending_payments(self):
        """Clear the list of pending payments after processing."""
        with self.lock:
            self.pending_payments.clear()
            logging.info("Cleared pending payments.")

    def manage_escrow(self, user_id, amount, hold_time_seconds=ESCROW_DEFAULT_HOLD_TIME):
        """Manage escrow by holding the specified amount for a certain duration."""
        with self.lock:
            if not self._is_valid_amount(amount):
                logging.error(f"Invalid escrow amount for user {user_id}: {amount}. Must be > 0 and <= {ESCROW_MAX_FUND_LIMIT}.")
                return False

            escrow_entry = {
                'amount': amount,
                'release_time': datetime.now() + timedelta(seconds=hold_time_seconds),
                'user_id': user_id
            }
            self.escrowed_funds[user_id].append(escrow_entry)
            logging.info(f"Managed escrow for {user_id}: {amount} held for {hold_time_seconds} seconds.")
            return True

    async def release_funds(self):
        """Release funds from escrow after their hold time expires."""
        logging.info("Attempting to release funds from escrow.")
        current_time = datetime.now()
        released_funds = []

        with self.lock:
            for user_id, escrow_entries in self.escrowed_funds.items():
                for escrow_entry in escrow_entries[:]:  # Iterate over a copy
                    if current_time >= escrow_entry['release_time']:
                        released_funds.append((user_id, escrow_entry['amount']))
                        logging.debug(f"Released {escrow_entry['amount']} from escrow for user {user_id}.")
                        escrow_entries.remove(escrow_entry)  # Remove the released fund

        if released_funds:
            logging.info(f"Released funds: {released_funds}")
            await self.transfer_funds(released_funds)  # Transfer released funds
        else:
            logging.info("No funds to release from escrow.")

    async def transfer_funds(self, released_funds):
        """Transfer the released funds to the specified account."""
        for user_id, amount in released_funds:
            transfer_success = await self.transfer_service.transfer_to_account(NOVO_ACCOUNT_NUMBER, NOVO_ROUTING_NUMBER, amount)
            if transfer_success:
                logging.info(f"Transferred {amount} to Novo account for user {user_id}.")
                self.handle_compounding(user_id, amount)  # Manage compounding after transfer
            else:
                logging.error(f"Failed to transfer {amount} to Novo account for user {user_id}.")

    def handle_compounding(self, user_id, amount):
        """Handle the recursive compounding of funds after transfer."""
        feedback_amount = amount * FEEDBACK_PERCENTAGE  # 3% feedback to user
        novo_amount = amount * NOVO_PERCENTAGE  # 1% allocated to Novo
        compounded_amount = amount - (feedback_amount + novo_amount)

        logging.info(f"Compounding for user {user_id}: Novo allocation = {novo_amount}, Feedback = {feedback_amount}, Compounded = {compounded_amount}")
        
        # Handle payouts
        self.total_feedback_paid += feedback_amount
        self.total_novo_paid += novo_amount
        
        if self.total_feedback_paid <= FEEDBACK_HOUR_LIMIT * FEEDBACK_AMOUNT_PER_HOUR:
            self.manage_escrow(user_id, feedback_amount)
        else:
            logging.warning(f"Feedback payout limit exceeded for user {user_id}.")

        if self.total_novo_paid <= float('inf'):  # No strict limit, just continuous payout
            self.manage_escrow(user_id, novo_amount)

        # Continue compounding
        if compounded_amount > 0:
            self.manage_escrow(user_id, compounded_amount)

    async def compound_funds(self, user_id):
        """Recursively compound funds every COMPOUNDING_INTERVAL seconds."""
        while True:
            await asyncio.sleep(COMPOUNDING_INTERVAL)
            current_balance = self.get_escrow_balance(user_id)
            compounded_balance = min(current_balance * 9 ** (9 ** 1e9), CAP)
            self.handle_compounding(user_id, compounded_balance)

    def receive_payment(self, user_id, amount):
        """Receive a payment and add it to escrow."""
        if self._is_valid_amount(amount):
            self.manage_escrow(user_id, amount)
            logging.info(f"Received payment of {amount} for user {user_id} and added to escrow.")
            self.add_pending_payment(user_id, amount)
            if user_id not in self.compounding_tasks:  # Start compounding task if not already running
                self.compounding_tasks[user_id] = asyncio.create_task(self.compound_funds(user_id))
        else:
            logging.error(f"Invalid amount {amount} for user {user_id}. Cannot receive payment.")

    def get_escrow_balance(self, user_id):
        """Return the total balance of escrowed funds for a specific user."""
        with self.lock:
            total_balance = sum(entry['amount'] for entry in self.escrowed_funds[user_id])
        logging.info(f"Current escrow balance for {user_id}: {total_balance}")
        return total_balance

    def can_release(self, user_id):
        """Check if any funds can be released for a specific user."""
        current_time = datetime.now()
        with self.lock:
            can_release_funds = [entry for entry in self.escrowed_funds[user_id] if current_time >= entry['release_time']]
        return len(can_release_funds) > 0

    async def manage_releases(self):
        """Continuously check for funds that can be released."""
        try:
            while True:
                await self.release_funds()
                await asyncio.sleep(1)  # Wait before checking again
        except Exception as e:
            logging.error(f"Error in manage_releases: {e}")

    def remove_escrow(self, user_id, amount):
        """Remove a specific amount from escrow for a user."""
        with self.lock:
            for entry in self.escrowed_funds[user_id]:
                if entry['amount'] == amount:
                    self.escrowed_funds[user_id].remove(entry)
                    logging.info(f"Removed {amount} from escrow for {user_id}.")
                    break

    def _is_valid_amount(self, amount):
        """Check if the amount is valid for escrow."""
        return amount > 0 and amount <= ESCROW_MAX_FUND_LIMIT

# --- Example Usage ---
# Uncomment to run the escrow manager as a standalone service
# if __name__ == "__main__":
#     escrow_manager = EscrowManager(transfer_service=YourTransferServiceImplementation())
#     asyncio.run(escrow_manager.manage_releases())
