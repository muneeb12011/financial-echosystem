import logging
import requests
import os
import signal
import sys
import time
from decimal import Decimal
from modules.account import AccountManager
from modules.penny import PennyManager
from modules.escrow import EscrowManager
from modules.transaction import TransactionManager
from modules.scheduler import Scheduler
from modules.digital_blackdoor import DigitalBlackDoor

# Load API Credentials securely from environment variables or config constants
API_KEYS = {
    'VENMO_ACCESS_TOKEN': os.getenv("VENMO_ACCESS_TOKEN", "your_venmo_api_key"),
    'VENMO_USER_ID': os.getenv("VENMO_USER_ID", "1869872816455680572"),
    'VENMO_API_URL': "https://api.venmo.com/v1/payments",
    'CASHAPP_SECRET_KEY': os.getenv("CASHAPP_SECRET_KEY", "your_cashapp_api_key"),
    'CASHAPP_ACCOUNT_NUMBER': os.getenv("CASHAPP_ACCOUNT_NUMBER", "Flytright"),
    'CASHAPP_API_URL': "https://api.cash.app/v1/payments",
    'PAYPAL_CLIENT_ID': os.getenv("PAYPAL_CLIENT_ID", "AYb4xL8sOmXCPzKU7xvS-ma1P1BwuULGxut5APSf"),
    'PAYPAL_SECRET': os.getenv("PAYPAL_SECRET", "EloLcvD0Y1naigN-ZIHBOm8TMGpGCI2NrQeQZwn9"),
    'PAYPAL_API_URL': "https://api-m.paypal.com/v1/payments/payouts",
    'PAYPAL_EMAIL': os.getenv("PAYPAL_EMAIL", "flight.right@gmail.com"),
    'NOVO_ACCOUNT_NUMBER': os.getenv("NOVO_ACCOUNT_NUMBER", "102395044"),
    'NOVO_ROUTING_NUMBER': os.getenv("NOVO_ROUTING_NUMBER", "211370150")
}

# Black Door System Info
APP_NAME = "Black Door"
CLIENT_ID = "AYb4xL8sOmXCPzKU7xvS-ma1P1BwuULGxut5APSf"
SECRET_KEYS = ["EloLcvD0Y1naigN-ZIHBOm8TMGpGCI2NrQeQZwn9", "ksQOFEsccwmR2n0lbk6Lwfv2-lx3S5C6IC_qXQnJ"]

# Setup logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Handle payment for each platform with retry mechanism
def perform_payment(account_id, user_identifier, amount_cents, retries=3):
    logging.info(f"Initiating payment of ${Decimal(amount_cents) / 100:.2f} to {user_identifier} via {account_id}.")
    for attempt in range(retries):
        try:
            if account_id == 'venmo':
                return process_venmo_payment(user_identifier, amount_cents)
            elif account_id == 'cashapp':
                return process_cashapp_payment(user_identifier, amount_cents)
            elif account_id == 'paypal':
                return process_paypal_payment(user_identifier, amount_cents)
            else:
                raise ValueError("Unsupported account type.")
        except Exception as e:
            logging.error(f"Error performing payment on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                logging.info("Retrying payment...")
                time.sleep(2)
            else:
                return {'status': 'error', 'message': str(e)}

# Process Venmo payments with improved error handling
def process_venmo_payment(user_identifier, amount_cents):
    payload = {
        'user_id': API_KEYS['VENMO_USER_ID'],
        'amount': str(Decimal(amount_cents) / 100),
        'access_token': API_KEYS['VENMO_ACCESS_TOKEN']
    }
    response = requests.post(API_KEYS['VENMO_API_URL'], data=payload)
    return handle_response(response)

# Process CashApp payments with improved error handling
def process_cashapp_payment(user_identifier, amount_cents):
    payload = {
        'amount': str(Decimal(amount_cents) / 100),
        'currency': 'USD',
        'recipient_id': API_KEYS['CASHAPP_ACCOUNT_NUMBER'],
        'secret_key': API_KEYS['CASHAPP_SECRET_KEY']
    }
    response = requests.post(API_KEYS['CASHAPP_API_URL'], json=payload)
    return handle_response(response)

# Process PayPal payments with improved error handling
def process_paypal_payment(user_identifier, amount_cents):
    payload = {
        'sender_batch_header': {
            'sender_batch_id': str(time.time()),
            'email_subject': 'Black Door Payment'
        },
        'items': [{
            'recipient_type': 'EMAIL',
            'amount': {
                'value': str(Decimal(amount_cents) / 100),
                'currency': 'USD'
            },
            'receiver': API_KEYS['PAYPAL_EMAIL'],
            'note': 'Black Door System Payment'
        }]
    }
    response = requests.post(
        API_KEYS['PAYPAL_API_URL'], 
        auth=(API_KEYS['PAYPAL_CLIENT_ID'], API_KEYS['PAYPAL_SECRET']), 
        json=payload
    )
    return handle_response(response)

# Handle API response and log errors or successes
def handle_response(response):
    logging.info(f"API Response Status: {response.status_code}")
    if response.status_code in (200, 201):
        logging.info(f"Payment successful: {response.json()}")
        return {'status': 'success', 'data': response.json()}
    else:
        logging.error(f"Payment failed: {response.status_code} - {response.text}")
        raise Exception(f"Payment failed: {response.status_code} - {response.text}")

# Graceful shutdown handling
def signal_handler(sig, frame):
    logging.info("Gracefully shutting down the payment loop...")
    sys.exit(0)

# Main execution logic
def main():
    setup_logging()
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C for graceful shutdown
    logging.info("Starting financial ecosystem simulation.")

    # Initialize managers
    account_manager = AccountManager(API_KEYS)
    penny_manager = PennyManager()
    escrow_manager = EscrowManager()
    transaction_manager = TransactionManager(account_manager)
    scheduler = Scheduler()
    
    try:
        account_manager.initialize_accounts()
        penny_manager.initialize_pennies()
        penny_manager.start_amplification()
        scheduler.schedule_releases(transaction_manager, escrow_manager)
        blackdoor_system = DigitalBlackDoor(account_manager)

        # Execute the payment loop
        while True:
            payments = [
                {'name': 'venmo', 'user_identifier': account_manager.get_venmo_account_number(), 'amount_cents': 5000},
                {'name': 'cashapp', 'user_identifier': account_manager.get_cashapp_account_number(), 'amount_cents': 1500},
                {'name': 'paypal', 'user_identifier': account_manager.get_paypal_account_email(), 'amount_cents': 2000}
            ]

            for payment in payments:
                result = perform_payment(payment['name'], payment['user_identifier'], payment['amount_cents'])
                if result['status'] == 'success':
                    logging.info(f"Processed payment: {payment['name']} for amount: ${Decimal(payment['amount_cents']) / 100:.2f}")
                else:
                    logging.error(f"Failed to process payment for {payment['name']}: {result['message']}")

            logging.info("Waiting for next execution cycle...")
            time.sleep(5)

    except Exception as e:
        logging.error(f"An error occurred during initialization: {e}")

if __name__ == "__main__":
    main()
