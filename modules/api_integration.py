import requests
import json
from decimal import Decimal
import logging

# Setup logging for detailed information on requests and error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration for the payment endpoints
VENMO_API_URL = "https://api.venmo.com/v1/payments"
PAYPAL_API_URL = "https://api.paypal.com/v1/payments/payment"
CASHAPP_API_URL = "https://api.cash.app/v1/payments"
NOVO_BANK_API_URL = "https://api.novo.co/v1/transactions"

class APIIntegration:
    def __init__(self, account_manager):
        self.account_manager = account_manager

    # Utility function to format payment data for all APIs
    def format_payment_data(self, amount: Decimal, currency: str = 'USD'):
        return {
            "amount": str(amount),
            "currency": currency
        }

    # Execute API request and handle response
    def execute_api_request(self, url, headers, payload, platform_name):
        try:
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

    # Venmo Payment API Integration
    def send_payment_venmo(self, amount: Decimal, recipient_id: str):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['VENMO_SECRET_ID']}",
            "Content-Type": "application/json"
        }
        payload = {
            "user_id": recipient_id,
            "amount": self.format_payment_data(amount)['amount'],
            "note": "Payment via BlackDoor system"
        }
        return self.execute_api_request(VENMO_API_URL, headers, payload, "Venmo")

    # PayPal Payment API Integration
    def send_payment_paypal(self, amount: Decimal):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['PAYPAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "sender_batch_header": {
                "sender_batch_id": "BlackDoorBatch",
                "email_subject": "You have received a payment"
            },
            "items": [{
                "recipient_type": "EMAIL",
                "amount": {
                    "value": self.format_payment_data(amount)['amount'],
                    "currency": self.format_payment_data(amount)['currency']
                },
                "note": "Payment via BlackDoor system",
                "sender_item_id": "item_1",
                "receiver": self.account_manager.get_paypal_account_email()
            }]
        }
        return self.execute_api_request(PAYPAL_API_URL, headers, payload, "PayPal")

    # CashApp Payment API Integration
    def send_payment_cashapp(self, amount: Decimal, recipient_id: str):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['CASHAPP_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "account_number": recipient_id,  # dynamic recipient account number
            "routing_number": self.account_manager.api_keys['CASHAPP_ROUTING_NUMBER'],
            "amount": self.format_payment_data(amount)['amount'],
            "note": "Payment via BlackDoor system"
        }
        return self.execute_api_request(CASHAPP_API_URL, headers, payload, "CashApp")

    # Novo Bank Payment API Integration
    def send_payment_novo(self, amount: Decimal):
        headers = {
            "Authorization": f"Bearer {self.account_manager.api_keys['NOVO_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "account_number": self.account_manager.get_nova_account_details()["account_number"],
            "routing_number": self.account_manager.get_nova_account_details()["routing_number"],
            "amount": self.format_payment_data(amount)['amount'],
            "note": "BlackDoor System to Novo Bank"
        }
        return self.execute_api_request(NOVO_BANK_API_URL, headers, payload, "Novo Bank")

    # Main function to handle payments via BlackDoor system
    def process_blackdoor_payment(self, platform: str, amount: Decimal, recipient_id: str = None):
        logging.info(f"Processing {platform} payment for {amount} USD")
        if platform == "venmo":
            return self.send_payment_venmo(amount, recipient_id)
        elif platform == "paypal":
            return self.send_payment_paypal(amount)
        elif platform == "cashapp":
            return self.send_payment_cashapp(amount, recipient_id)
        elif platform == "novo":
            return self.send_payment_novo(amount)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            return {"error": "Invalid platform specified"}

# Example usage
if __name__ == "__main__":
    from account import AccountManager  # Adjust import as necessary
    account_manager = AccountManager(api_keys={
        'VENMO_SECRET_ID': '1869872816455680572',
        'CASHAPP_API_KEY': 'your_cashapp_api_key',
        'PAYPAL_API_KEY': 'your_paypal_api_key',
        'NOVO_API_KEY': 'your_novo_api_key',
        'CASHAPP_ROUTING_NUMBER': '121000248',
        'PAYPAL_EMAIL': 'flight.right@gmail.com'
    })
    api_integration = APIIntegration(account_manager)

    platform = "venmo"  # Replace with the platform you want to test (venmo, paypal, cashapp, novo)
    amount = Decimal("100.00")  # Example amount
    recipient_id = 'recipient_user_id'  # Replace with actual recipient ID for Venmo/CashApp
    response = api_integration.process_blackdoor_payment(platform, amount, recipient_id)
    print(response)
