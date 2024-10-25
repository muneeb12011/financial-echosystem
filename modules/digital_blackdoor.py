import logging
from modules.account import AccountManager
from modules.api_integration import APIIntegration  # Import the APIIntegration class
from config import API_KEYS  # Ensure API keys are configured correctly
from decimal import Decimal

class DigitalBlackDoor:
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.api_integration = APIIntegration(account_manager)  # Initialize API integration with the account manager

    def execute_payment(self, payment_details):
        try:
            # Log the payment processing step
            logging.info(f"Processing payment through {payment_details['name']} for {payment_details['amount_cents']} cents.")

            # Call the appropriate platform to process the payment
            platform = payment_details['name']
            amount = Decimal(payment_details['amount_cents']) / 100  # Convert cents to dollars
            recipient_id = payment_details.get('user_identifier', None)  # Get the recipient ID (if applicable)

            response = self.api_integration.process_blackdoor_payment(platform, amount, recipient_id)
            logging.info(f"Payment executed successfully for {platform}: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to execute payment for {payment_details['name']}: {e}")
            return {"error": str(e)}

    def process_payments(self, payment_list):
        for payment in payment_list:
            response = self.execute_payment(payment)
            # Log the response for each payment
            logging.info(f"Payment Response for {payment['name']}: {response}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the account manager with provided API keys
    account_manager = AccountManager(API_KEYS)
    
    # Create an instance of DigitalBlackDoor
    blackdoor_system = DigitalBlackDoor(account_manager)
    
    payments = [
        {'name': 'venmo', 'user_identifier': account_manager.get_venmo_account_number(), 'amount_cents': 5000},  # $50.00
        {'name': 'cashapp', 'user_identifier': account_manager.get_cashapp_account_number(), 'amount_cents': 1500},  # $15.00
        {'name': 'paypal', 'user_identifier': account_manager.get_paypal_account_email(), 'amount_cents': 2000},  # $20.00
        {'name': 'novo', 'user_identifier': account_manager.get_nova_account_details()['account_number'], 'amount_cents': 3000}  # $30.00 to Nova Bank
    ]
    
    # Process all payments
    blackdoor_system.process_payments(payments)
