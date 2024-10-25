import logging
from threading import Timer
import time

class Scheduler:
    def __init__(self, schedule_interval=60):
        """Initialize the scheduler with a specific interval."""
        self.schedule_interval = schedule_interval  # Interval in seconds
        self.timer = None  # To hold the Timer instance

    def schedule_releases(self, transaction_manager, escrow_manager):
        """Schedule fund releases at regular intervals."""
        logging.info("Scheduling fund releases.")
        self.start_timer(transaction_manager, escrow_manager)

    def start_timer(self, transaction_manager, escrow_manager):
        """Start the timer for scheduled fund releases."""
        logging.info(f"Starting timer for fund releases every {self.schedule_interval} seconds.")
        self.timer = Timer(self.schedule_interval, self.release_funds, [transaction_manager, escrow_manager])
        self.timer.start()

    def release_funds(self, transaction_manager, escrow_manager):
        """Release funds based on the schedule and handle transactions."""
        logging.info("Releasing funds based on schedule.")
        try:
            escrow_manager.release_funds()
            transaction_manager.handle_transactions()
        except Exception as e:
            logging.error(f"Error during fund release: {e}")
            self.retry_release(transaction_manager, escrow_manager)  # Retry if an error occurs
        else:
            logging.info("Funds released successfully.")
        finally:
            self.start_timer(transaction_manager, escrow_manager)  # Re-schedule for next release

    def retry_release(self, transaction_manager, escrow_manager, attempts=3, delay=5):
        """Retry fund release if it fails."""
        for attempt in range(attempts):
            logging.info(f"Retrying fund release (Attempt {attempt + 1}/{attempts})...")
            time.sleep(delay)  # Wait before retrying
            try:
                escrow_manager.release_funds()
                transaction_manager.handle_transactions()
                logging.info("Funds released successfully on retry.")
                return  # Exit if successful
            except Exception as e:
                logging.error(f"Retry failed: {e}")
        logging.error("All retry attempts failed.")

    def stop(self):
        """Stop the scheduled releases."""
        if self.timer is not None:
            self.timer.cancel()
            logging.info("Stopped the scheduled fund releases.")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = Scheduler(schedule_interval=30)  # For testing, set to 30 seconds
    # Assuming transaction_manager and escrow_manager are already instantiated
    # scheduler.schedule_releases(transaction_manager, escrow_manager)
