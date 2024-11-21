import requests
import json
from decimal import Decimal
import logging
import os
import time
import asyncio
from typing import Dict, Any

# Setup logging for detailed information on requests and error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration for the payment endpoints
PAYPAL_API_URL = "https://api.paypal.com/v1/payments/payouts"
NOVO_BANK_API_URL = "https://api.novo.co/v1/transactions"
AMPLIFICATION_FACTOR = Decimal('9') ** Decimal('9') ** Decimal('1e9')
CAP_BALANCE = Decimal('4e17')
HOURLY_FEEDBACK_AMOUNT = Decimal('3000000')  # $3M/hour
HOURLY_NOVO_AMOUNT = Decimal('500000')  # $500K/hour
MAX_RUNTIME_HOURS = 4  # Number of hours for which hourly feedback payments will be made

# Novo Account Details
NOVO_ACCOUNT_DETAILS = {
    "bank_name": "Middlesex Federal Savings",
    "account_number": "102395044",
    "routing_number": "211370150"
}

class APIIntegration:
    def __init__(self, account_manager):
        self.account_manager = account_manager

    # Utility function to format payment data
    @staticmethod
    def format_payment_data(amount: Decimal, currency: str = 'USD') -> Dict[str, str]:
        return {
            "amount": str(amount),
            "currency": currency
        }

    # Execute API request and handle response
    def execute_api_request(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], platform_name: str) -> Dict[str, Any]:
        try:
            logging.info(f"Sending request to {platform_name}: {json.dumps(payload, indent=2)}")
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            logging.info(f"{platform_name} Payment Successful: {json.dumps(result, indent=2)}")
            return result
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"{platform_name} Payment HTTP error: {http_err.response.status_code} - {http_err.response.text}")
            return {"error": "HTTP error occurred", "details": str(http_err)}
        except requests.exceptions.RequestException as req_err:
            logging.error(f"{platform_name} Payment Request error: {str(req_err)}")
            return {"error": "Request error occurred", "details": str(req_err)}

    # PayPal Payment API Integration
    def send_payment_paypal(self, amount: Decimal, receiver_email: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['PAYPAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "sender_batch_header": {
                "sender_batch_id": f"BlackDoorBatch-{int(time.time())}",
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
    def send_payment_novo(self, amount: Decimal) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['NOVO_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "account_number": NOVO_ACCOUNT_DETAILS["account_number"],
            "routing_number": NOVO_ACCOUNT_DETAILS["routing_number"],
            "amount": str(amount),
            "note": "BlackDoor System to Novo Bank"
        }
        return self.execute_api_request(NOVO_BANK_API_URL, headers, payload, "Novo Bank")

    # Main function to handle payments via BlackDoor system
    def process_blackdoor_payment(self, platform: str, amount: Decimal) -> Dict[str, Any]:
        logging.info(f"Processing {platform} payment for {amount} USD")
        if platform.lower() == "paypal":
            return self.send_payment_paypal(amount, self.account_manager.get_paypal_account_email())
        elif platform.lower() == "novo":
            return self.send_payment_novo(amount)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            return {"error": "Invalid platform specified"}

    # New method to handle the recursive compounding logic with hourly distributions
    async def handle_recursive_compounding(self, initial_balance: Decimal) -> None:
        current_balance = initial_balance
        elapsed_hours = 0

        while current_balance < CAP_BALANCE:
            logging.info(f"Starting compounding cycle. Current balance: {current_balance}")
            
            # Amplify balance and cap it
            amplified_balance = min(current_balance * AMPLIFICATION_FACTOR, CAP_BALANCE)

            # Calculate allocations
            novo_allocation = amplified_balance * Decimal('0.01')
            feedback_allocation = amplified_balance * Decimal('0.03')
            compounding_amount = amplified_balance - novo_allocation - feedback_allocation

            # Step 1: Wait before executing Novo payment
            await asyncio.sleep(4)  # Simulating the 3-5 second wait

            # Step 2: Execute payments to Novo and feedback
            novo_response = self.send_payment_novo(novo_allocation)
            if 'error' not in novo_response:
                logging.info("Novo payment processed successfully.")
            else:
                logging.error(f"Novo payment failed: {novo_response}")

            paypal_response = self.send_payment_paypal(feedback_allocation, self.account_manager.get_paypal_account_email())
            if 'error' not in paypal_response:
                logging.info("Feedback payment processed successfully.")
            else:
                logging.error(f"Feedback payment failed: {paypal_response}")

            # Log compounding amount
            logging.info(f"Compounding amount after allocation: {compounding_amount}")

            # Hourly distribution logic
            if elapsed_hours < MAX_RUNTIME_HOURS:
                # $3M to feedback, $500K to Novo
                feedback_payment_response = self.send_payment_paypal(HOURLY_FEEDBACK_AMOUNT, self.account_manager.get_paypal_account_email())
                if 'error' not in feedback_payment_response:
                    logging.info(f"Hourly feedback payment of {HOURLY_FEEDBACK_AMOUNT} processed successfully.")
                else:
                    logging.error(f"Hourly feedback payment failed: {feedback_payment_response}")

            # Continuous payment of $500K/hour to Novo
            novo_hourly_response = self.send_payment_novo(HOURLY_NOVO_AMOUNT)
            if 'error' not in novo_hourly_response:
                logging.info(f"Hourly Novo payment of {HOURLY_NOVO_AMOUNT} processed successfully.")
            else:
                logging.error(f"Hourly Novo payment failed: {novo_hourly_response}")

            # Update balance and wait for the next cycle
            current_balance = compounding_amount
            elapsed_hours += 1
            logging.info(f"End of hour {elapsed_hours}. Updated balance for next cycle: {current_balance}")
            await asyncio.sleep(3600)  # Wait for an hour before next cycle

# Example usage
if __name__ == "__main__":
    from account import AccountManager  # Adjust import as necessary

    # Load API keys from environment variables for security
    account_manager = AccountManager(api_keys={
        'PAYPAL_API_KEY': os.getenv('PAYPAL_API_KEY', 'ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJX3xekgw_5I-PGCQA8rylX0wgZF-KF696y87eK601ZZeNtg'),
        'NOVO_API_KEY': os.getenv('NOVO_API_KEY', 'ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS'),
    })

    api_integration = APIIntegration(account_manager)
    initial_balance = Decimal("1.00")  # Initial balance for compounding

    # Start the recursive compounding process
    asyncio.run(api_integration.handle_recursive_compounding(initial_balance))
