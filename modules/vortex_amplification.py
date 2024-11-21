from decimal import Decimal, getcontext
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

# --- Constants ---
getcontext().prec = 100  # High precision for calculations
MAX_AMOUNT = Decimal('4e17')  # $400 quadrillion cap
ESCROW_THRESHOLD = Decimal('3000000')  # $3 million threshold for escrow
RELEASE_RATE = Decimal('0.01')  # 1% release rate for Novo
CENTS_IN_A_DOLLAR = Decimal('100')
PENNIES_PER_DOLLAR = Decimal('100')
AMPLIFICATION_DURATION = 5  # Duration in seconds for amplification
COMPOUNDING_INTERVAL = 3  # Interval for compounding in seconds
NOVA_EMAIL = "novo_account@example.com"  # Novo account email
FEEDBACK_EMAIL = "flight.right@gmail.com"  # Feedback email
NOVA_AMOUNT = Decimal('500000')  # Amount to send to Novo
FEEDBACK_AMOUNT = Decimal('3000000')  # Amount to send as feedback

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PayPal Credentials ---
PAYPAL_CLIENT_ID = 'ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJX3xekgw_5I-PGCQA8rylX0wgZF-KF696y87eK601ZZeNtg'
PAYPAL_SECRET = 'ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS'
PAYPAL_API_URL = "https://api-m.paypal.com/v1/payments/payouts"
PAYPAL_TOKEN_URL = "https://api-m.paypal.com/v1/oauth2/token"

# Define the Flask app for webhook handling
app = Flask(__name__)

# --- Escrow Manager Class ---
class EscrowManager:
    def __init__(self):
        self.escrow_balance = Decimal('0')

    def add_to_escrow(self, amount: Decimal):
        self.escrow_balance += amount
        self.escrow_balance = min(self.escrow_balance, MAX_AMOUNT)

    def release_funds(self):
        if self.escrow_balance > ESCROW_THRESHOLD:
            release_amount = self.escrow_balance * RELEASE_RATE
            self.escrow_balance -= release_amount
            return release_amount
        return Decimal('0')

# --- Recursive Compounding Function ---
def recursive_compound(amount: Decimal):
    novo_amount = amount * Decimal('0.01')  # 1% to Novo
    feedback_amount = amount * Decimal('0.03')  # 3% feedback
    remaining_amount = amount - (novo_amount + feedback_amount)  # Remaining for compounding
    return novo_amount, feedback_amount, remaining_amount

# --- Vortex Amplification Function ---
def vortex_amplification(initial_contribution: Decimal):
    escrow_manager = EscrowManager()  # Initialize escrow manager
    viral_factor = Decimal('1') + (initial_contribution / (CENTS_IN_A_DOLLAR * PENNIES_PER_DOLLAR))
    access_token = get_paypal_access_token()  # Initial token fetch

    with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced workers for clarity
        start_time = time.time()
        
        while (time.time() - start_time) < AMPLIFICATION_DURATION:
            amplified_amount = initial_contribution * (viral_factor ** ((time.time() - start_time)))
            escrow_manager.add_to_escrow(max(amplified_amount - ESCROW_THRESHOLD, 0))

            # Payouts every 3 seconds until the maximum amount is reached
            while escrow_manager.escrow_balance >= ESCROW_THRESHOLD:
                time.sleep(COMPOUNDING_INTERVAL)

                escrow_release = escrow_manager.release_funds()
                if escrow_release > 0:
                    # Implement recursive compounding logic
                    novo_amount, feedback_amount, compounding_amount = recursive_compound(escrow_release)

                    # Send payment to Novo account
                    executor.submit(send_payment, "paypal", NOVA_EMAIL, float(novo_amount), access_token)

                    # Send feedback payment
                    executor.submit(send_payment, "paypal", FEEDBACK_EMAIL, float(feedback_amount), access_token)

                    # Log the payouts
                    logging.info(f"Released ${escrow_release:.2f} to Novo and Feedback accounts.")

                    # Update the initial contribution for further amplification
                    initial_contribution += compounding_amount

# --- Payment Function with Retry Logic ---
def send_payment(platform: str, user_id: str, amount: float, access_token: str, retries: int = 3):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "sender_batch_header": {
            "sender_batch_id": f"batch_{int(time.time())}",
            "email_subject": "You have a payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "USD"
                },
                "receiver": user_id,
                "note": "Payment via BlackDoor System",
                "sender_item_id": f"item_{int(time.time())}"
            }
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(PAYPAL_API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Payment of ${amount:.2f} successfully sent to {user_id} via {platform}.")
            return
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send payment via {platform} to {user_id} on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

# --- Receive Payment Function via Webhook ---
@app.route('/webhook', methods=['POST'])
def receive_payment():
    """Listen for incoming PayPal payments via webhook."""
    # Validate webhook request
    if not validate_paypal_webhook(request):
        return jsonify({"error": "Invalid webhook request"}), 400

    data = request.json
    logging.info(f"Webhook received: {data}")

    # Process the received payment (e.g., update balance, notify user, etc.)
    if data.get('event_type') == 'PAYMENT.SALE.COMPLETED':
        sale_amount = data['resource']['amount']['total']
        payer_email = data['resource']['payer']['payer_info']['email']
        logging.info(f"Received payment of ${sale_amount} from {payer_email}.")

        # Trigger the vortex amplification process based on received payment
        vortex_amplification(Decimal(sale_amount))

    return jsonify({"status": "success"}), 200

def validate_paypal_webhook(req):
    """Validates incoming webhook requests from PayPal."""
    # Note: You would typically validate the incoming request using the PayPal SDK or API
    return True  # For the sake of this example, always return True

# --- PayPal Access Token with Auto Refresh ---
def get_paypal_access_token() -> str:
    try:
        response = requests.post(
            PAYPAL_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        response.raise_for_status()
        access_token = response.json().get('access_token')
        if not access_token:
            raise ValueError("Access token not found in response.")
        logging.info("Successfully obtained PayPal access token.")
        return access_token
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to obtain PayPal access token: {e}")
        raise
    except ValueError as ve:
        logging.error(f"Error retrieving access token: {ve}")
        raise

# --- Main Execution ---
if __name__ == "__main__":
    initial_contribution = Decimal('1.00')  # Change the initial contribution to $1.00
    vortex_amplification(initial_contribution)

    # Start the Flask app to listen for incoming webhooks
    app.run(port=5000, debug=True)  # Make sure to use a port that is open and accessible
