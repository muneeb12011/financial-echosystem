import logging
import os
import time
import requests
from decimal import Decimal

# --- Constants and Parameters ---
ESCROW_MIN_HOLD_TIME = 10  # Hold time in seconds for each cent
CENTS_IN_A_DOLLAR = 100  # Conversion factor
REQUEST_TIMEOUT = 10  # API request timeout in seconds

# --- API Credentials and Endpoints ---
# Venmo configuration
VENMO_ACCESS_TOKEN = os.getenv("VENMO_ACCESS_TOKEN")
VENMO_API_URL = "https://api.venmo.com/v1/payments"
VENMO_ACCOUNT_NUMBER = os.getenv("VENMO_ACCOUNT_NUMBER", "222164973891")

# CashApp configuration
CASHAPP_SECRET_KEY = os.getenv("CASHAPP_SECRET_KEY")
CASHAPP_API_URL = "https://api.cash.app/v1/payments"
CASHAPP_ACCOUNT_NUMBER = os.getenv("CASHAPP_ACCOUNT_NUMBER", "98971128727551668")

# PayPal configuration
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_URL = "https://api-m.paypal.com/v1/payments/payouts"
PAYPAL_EMAIL = os.getenv("PAYPAL_EMAIL", "flight.right@gmail.com")

# --- Payment System Class ---
class DigitalPaymentSystem:
    def __init__(self, name, user_identifier):
        self.name = name
        self.user_identifier = user_identifier

    def send_payment(self, amount_cents):
        amount_usd = Decimal(amount_cents) / CENTS_IN_A_DOLLAR
        logging.info(f"Sending ${amount_usd:.2f} to {self.user_identifier} via {self.name}.")
        self.hold_escrow(amount_cents)

        if self.name.lower() == 'venmo':
            return self.send_venmo_payment(amount_usd)
        elif self.name.lower() == 'cashapp':
            return self.send_cashapp_payment(amount_usd)
        elif self.name.lower() == 'paypal':
            return self.send_paypal_payment(amount_usd)
        logging.error(f"Payment method '{self.name}' is not supported.")
        return False

    def hold_escrow(self, amount_cents):
        hold_time = ESCROW_MIN_HOLD_TIME * (amount_cents / CENTS_IN_A_DOLLAR)
        logging.info(f"Holding ${Decimal(amount_cents) / CENTS_IN_A_DOLLAR:.2f} in escrow for {hold_time:.1f} seconds.")
        time.sleep(hold_time)

    def send_venmo_payment(self, amount_usd):
        headers = {
            "Authorization": f"Bearer {VENMO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "user_id": self.user_identifier,
            "amount": str(amount_usd),
            "note": "Payment via Digital BlackDoor System"
        }
        try:
            response = requests.post(VENMO_API_URL, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            logging.info(f"Venmo payment successful: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Venmo payment failed: {e}")
            return {"error": str(e)}

    def send_cashapp_payment(self, amount_usd):
        headers = {
            "Authorization": f"Bearer {CASHAPP_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "amount": int(amount_usd * CENTS_IN_A_DOLLAR),
            "recipient": self.user_identifier,
            "note": "Payment via Digital BlackDoor System"
        }
        try:
            response = requests.post(CASHAPP_API_URL, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            logging.info(f"CashApp payment successful: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"CashApp payment failed: {e}")
            return {"error": str(e)}

    def send_paypal_payment(self, amount_usd):
        access_token = self.get_paypal_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data = {
            "sender_batch_header": {
                "sender_batch_id": str(int(time.time())),
                "email_subject": "You have a payment"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{amount_usd:.2f}",
                        "currency": "USD"
                    },
                    "receiver": PAYPAL_EMAIL,
                    "note": "Payment via Digital BlackDoor System",
                    "sender_item_id": "item_1"
                }
            ]
        }
        try:
            response = requests.post(PAYPAL_API_URL, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            logging.info(f"PayPal payment successful: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"PayPal payment failed: {e}")
            return {"error": str(e)}

    def get_paypal_access_token(self):
        try:
            response = requests.post(
                "https://api-m.paypal.com/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()['access_token']
        except requests.RequestException as e:
            logging.error(f"Failed to get PayPal access token: {e}")
            return None
