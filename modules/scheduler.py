import logging
import asyncio
from datetime import datetime
from decimal import Decimal
from .transaction import TransactionManager  # Use relative import
from .escrow import EscrowManager  # Use relative import

# --- Scheduler Configuration Constants ---
COMPOUNDING_INTERVAL = 3  # Interval for compounding in seconds
NOVO_TRANSFER_INTERVAL = 45  # Interval for Novo transfers in seconds
DEFAULT_MAX_ATTEMPTS = 3  # Default maximum attempts for retrying fund releases
RETRY_DELAY = 5  # Delay between retry attempts in seconds

class Scheduler:
    def __init__(self, transaction_manager, escrow_manager, compounding_interval=COMPOUNDING_INTERVAL, novo_transfer_interval=NOVO_TRANSFER_INTERVAL, max_attempts=DEFAULT_MAX_ATTEMPTS):
        """Initialize the scheduler with specified intervals and retry settings."""
        self.transaction_manager = transaction_manager
        self.escrow_manager = escrow_manager
        self.compounding_interval = compounding_interval
        self.novo_transfer_interval = novo_transfer_interval
        self.max_attempts = max_attempts
        self.running = False

    async def start(self):
        """Start the scheduler and manage fund releases based on intervals."""
        logging.info("Starting scheduler for fund releases with real-time logging.")
        self.running = True
        compounding_task = asyncio.create_task(self.run_compounding())
        novo_transfer_task = asyncio.create_task(self.run_novo_transfers())
        await asyncio.gather(compounding_task, novo_transfer_task)

    async def run_compounding(self):
        """Run compounding every 3 seconds as specified by client requirements."""
        while self.running:
            try:
                timestamp = datetime.now().isoformat()
                logging.info(f"Running compounding process at {timestamp}")
                # Handle compounding logic in the transaction manager
                await self.transaction_manager.handle_recursive_compounding(Decimal("1.00"))  # Starting with $1.00 for compounding
                logging.info(f"Compounding completed at {datetime.now().isoformat()}")
            except Exception as e:
                logging.error(f"Error during compounding: {e}")
                await self.retry_operation(self.transaction_manager.handle_recursive_compounding, "Compounding")
            await asyncio.sleep(self.compounding_interval)

    async def run_novo_transfers(self):
        """Transfer funds to Novo every 45 seconds as specified by client requirements."""
        while self.running:
            try:
                timestamp = datetime.now().isoformat()
                logging.info(f"Initiating Novo transfer at {timestamp}")
                await self.escrow_manager.release_funds_to_novo()
                logging.info(f"Novo transfer completed at {datetime.now().isoformat()}")
            except Exception as e:
                logging.error(f"Error during Novo transfer: {e}")
                await self.retry_operation(self.escrow_manager.release_funds_to_novo, "Novo Transfer")
            await asyncio.sleep(self.novo_transfer_interval)

    async def retry_operation(self, operation, operation_name):
        """Retry a failed operation for a set number of attempts with delay."""
        for attempt in range(1, self.max_attempts + 1):
            logging.info(f"Retrying {operation_name} (Attempt {attempt}/{self.max_attempts})")
            await asyncio.sleep(RETRY_DELAY)
            try:
                await operation()
                logging.info(f"{operation_name} succeeded on retry.")
                return
            except Exception as e:
                logging.error(f"{operation_name} retry {attempt} failed: {e}")
        logging.error(f"All retry attempts for {operation_name} failed.")

    def stop(self):
        """Stop the scheduled fund releases."""
        self.running = False
        logging.info("Scheduler stopped.")

# Example usage
async def main():
    logging.basicConfig(level=logging.INFO)

    # Instantiate the transaction manager with relevant details
    transaction_manager = TransactionManager(
        paypal_client_id='ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJX3xekgw_5I-PGCQA8rylX0wgZF-KF696y87eK601ZZeNtg',
        paypal_secret_key='ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS',
        novo_account_number='102395044',
        novo_routing_number='211370150'
    )

    # Instantiate the escrow manager
    escrow_manager = EscrowManager(transaction_manager)

    # Initialize and start the scheduler with configured intervals
    scheduler = Scheduler(transaction_manager, escrow_manager)
    await scheduler.start()

# Uncomment to run the example
# asyncio.run(main())
