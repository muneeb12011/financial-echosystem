import logging
from modules.api_integration import APIIntegration
from decimal import Decimal

class TransactionManager:
    def __init__(self, account_manager):
        self.account_manager = account_manager

    def handle_transactions(self):
        """Handle a list of transactions."""
        logging.info("Handling transactions.")
        transactions = [
            {'account_id': 'venmo', 'amount': Decimal('100.00')},
            {'account_id': 'paypal', 'amount': Decimal('-50.00')},
            {'account_id': 'cashapp', 'amount': Decimal('150.00')},
            {'account_id': 'nova', 'amount': Decimal('200.00')},  # Nova Bank transaction
        ]
        
        for transaction in transactions:
            self.process_payment(transaction['account_id'], transaction['amount'])

    def process_payment(self, account_id, amount):
        """Process individual payment for a specified account."""
        logging.info(f"Processing payment for {account_id}: {amount}")
        try:
            new_balance = self.account_manager.get_account_balance(account_id) + amount
            
            # Validate new balance
            if new_balance < 0:
                logging.warning(f"Insufficient balance for {account_id}. Transaction aborted.")
                return
            
            # Update account balance
            self.account_manager.update_balance(account_id, amount)
            logging.info(f"Payment processed for {account_id}. Amount: {amount}")
            
            # Send payment through API
            self.send_payment(account_id, amount)
        except Exception as e:
            logging.error(f"Transaction failed for {account_id}: {e}")

    def send_payment(self, account_id, amount):
        """Send payment using the API and log the response."""
        try:
            logging.info(f"Sending payment of {amount} to {account_id}.")
            response = APIIntegration.send_payment(account_id, amount)
            
            if response.get('status') == 'success':
                logging.info(f"Payment of {amount} sent successfully to {account_id}.")
            else:
                logging.error(f"Failed to send payment to {account_id}. Response: {response}")
        except Exception as e:
            logging.error(f"Error sending payment to {account_id}: {e}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Assuming account_manager is already instantiated
    # account_manager = AccountManager()  # Example instantiation
    # transaction_manager = TransactionManager(account_manager)
    # transaction_manager.handle_transactions()
