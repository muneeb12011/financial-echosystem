import requests
import json
from decimal import Decimal
import logging
import os
import time
import asyncio

# Setup logging for detailed information on requests and error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration for the payment endpoints
PAYPAL_API_URL = "https://api.paypal.com/v1/payments/payouts"
NOVO_BANK_API_URL = "https://api.novo.co/v1/transactions"

class APIIntegration:
    def __init__(self, account_manager):
        self.account_manager = account_manager

    # Utility function to format payment data
    def format_payment_data(self, amount: Decimal, currency: str = 'USD'):
        return {
            "amount": str(amount),
            "currency": currency
        }

    # Execute API request and handle response
    def execute_api_request(self, url, headers, payload, platform_name):
        try:
            logging.info(f"Sending request to {platform_name}: {payload}")
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise exception for bad HTTP codes
            logging.info(f"{platform_name} Payment Successful: {response.json()}")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"{platform_name} Payment HTTP error: {http_err.response.status_code} - {http_err.response.text}")
            return {"error": "HTTP error occurred", "details": str(http_err)}
        except requests.exceptions.RequestException as req_err:
            logging.error(f"{platform_name} Payment Request error: {str(req_err)}")
            return {"error": "Request error occurred", "details": str(req_err)}

    # PayPal Payment API Integration
    def send_payment_paypal(self, amount: Decimal, receiver_email: str):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['PAYPAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "sender_batch_header": {
                "sender_batch_id": f"BlackDoorBatch-{int(time.time())}",  # Unique batch ID
                "email_subject": "You have received a payment"
            },
            "items": [{
                "recipient_type": "EMAIL",
                "amount": {
                    "value": str(amount),
                    "currency": "USD"
                },
                "note": "Payment via BlackDoor system",
                "sender_item_id": "item_1",
                "receiver": receiver_email
            }]
        }
        return self.execute_api_request(PAYPAL_API_URL, headers, payload, "PayPal")

    # Novo Bank Payment API Integration
    def send_payment_novo(self, amount: Decimal):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['NOVO_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "account_number": self.account_manager.get_nova_account_details()["account_number"],
            "routing_number": self.account_manager.get_nova_account_details()["routing_number"],
            "amount": str(amount),
            "note": "BlackDoor System to Novo Bank"
        }
        return self.execute_api_request(NOVO_BANK_API_URL, headers, payload, "Novo Bank")

    # Main function to handle payments via BlackDoor system
    def process_blackdoor_payment(self, platform: str, amount: Decimal):
        logging.info(f"Processing {platform} payment for {amount} USD")
        if platform.lower() == "paypal":
            return self.send_payment_paypal(amount, self.account_manager.get_paypal_account_email())
        elif platform.lower() == "novo":
            return self.send_payment_novo(amount)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            return {"error": "Invalid platform specified"}

    # New method to handle the compounding logic
    async def handle_recursive_compounding(self, total_amount: Decimal):
        """
        Handle recursive compounding by allocating funds:
        - 1% to Novo
        - 3% as feedback to the PayPal email
        - Remaining balance for further compounding
        """
        # Step 1: Allocate percentages
        novo_allocation = total_amount * Decimal('0.01')
        feedback_allocation = total_amount * Decimal('0.03')
        compounding_amount = total_amount - novo_allocation - feedback_allocation

        # Log allocation details
        logging.info(f"Allocating {novo_allocation} to Novo, {feedback_allocation} for feedback, and {compounding_amount} for compounding.")

        # Step 2: Wait for 4 seconds before executing Novo payment
        await asyncio.sleep(4)  # Simulating the 3-5 second wait

        # Step 3: Send payment to Novo
        novo_response = self.send_payment_novo(novo_allocation)
        if 'error' not in novo_response:
            logging.info("Novo payment processed successfully.")
        else:
            logging.error(f"Novo payment failed: {novo_response}")

        # Step 4: Send feedback payment to PayPal
        paypal_response = self.send_payment_paypal(feedback_allocation, self.account_manager.get_paypal_account_email())
        if 'error' not in paypal_response:
            logging.info("Feedback payment processed successfully.")
        else:
            logging.error(f"Feedback payment failed: {paypal_response}")

        # Step 5: Log the compounding amount
        logging.info(f"Total compounding amount: {compounding_amount}")

        # Optionally: You could continue to recursively call this method
        # if you want to continuously compound.
        return {
            "novo_response": novo_response,
            "paypal_response": paypal_response,
            "compounding_amount": compounding_amount
        }

# Example usage
if __name__ == "__main__":
    from account import AccountManager  # Adjust import as necessary

    # Load API keys from environment variables for security
    account_manager = AccountManager(api_keys={
        'PAYPAL_API_KEY': os.getenv('PAYPAL_API_KEY'),
        'NOVO_API_KEY': os.getenv('NOVO_API_KEY'),
    })

    api_integration = APIIntegration(account_manager)
    platform = "paypal"  # Replace with "novo" if testing Novo Bank payments
    amount = Decimal("1.00")  # Example amount for testing

    # Process a payment via the BlackDoor system
    response = api_integration.process_blackdoor_payment(platform, amount)
    print(response)

    # Handle recursive compounding for a total amount asynchronously
    compounding_response = asyncio.run(api_integration.handle_recursive_compounding(amount))
    print(compounding_response)
