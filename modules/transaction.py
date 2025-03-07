import logging
import requests
from decimal import Decimal, getcontext
import time
from paypalrestsdk import Payment  # Ensure you have the PayPal SDK installed
from config import API_KEYS

PAYPAL_CLIENT_ID = API_KEYS['PAYPAL_CLIENT_ID']
PAYPAL_SECRET = API_KEYS['PAYPAL_SECRET']
NOVO_ACCOUNT_NUMBER = API_KEYS['NOVO_ACCOUNT_NUMBER']
NOVO_ROUTING_NUMBER = API_KEYS['NOVO_ROUTING_NUMBER']

# Set high precision for Decimal calculations
getcontext().prec = 10000

class TransactionManager:
    def __init__(self, paypal_client_id, paypal_secret_key, novo_account_number, novo_routing_number):
        """Initialize the Transaction Manager with account details."""
        self.paypal_client_id = paypal_client_id
        self.paypal_secret_key = paypal_secret_key
        self.novo_account_number = novo_account_number
        self.novo_routing_number = novo_routing_number
        self.paypal_api_url = "https://api.paypal.com/v1/payments/payment"  # Use live URL for deployment
        self.account_manager = None  # Placeholder for the account manager instance

    async def set_account_manager(self, account_manager):
        """Set the account manager for handling balances."""
        self.account_manager = account_manager

    async def check_for_payments(self):
        """Check for new payments in the PayPal account."""
        logging.info("Checking for new payments...")
        pending_payments = await self.get_pending_payments()
        for payment in pending_payments:
            amount = Decimal(payment['amount'])
            await self.handle_transactions(amount)

    async def get_pending_payments(self):
        """Fetch pending payments from PayPal."""
        try:
            logging.info("Fetching pending payments from PayPal...")
            access_token = self.get_paypal_access_token()
            response = requests.get(
                "https://api.paypal.com/v1/payments/payment?count=10",  # Adjust count as needed
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )

            if response.status_code == 200:
                payments = response.json().get('payments', [])
                # Filter for pending payments
                pending_payments = [{'amount': payment['transactions'][0]['amount']['total']} for payment in payments if payment['state'] == 'created']
                logging.info(f"Pending payments fetched: {pending_payments}")
                return pending_payments
            else:
                logging.error(f"Failed to fetch payments. Response: {response.json()}")
                return []

        except Exception as e:
            logging.error(f"Error fetching pending payments: {e}")
            return []

    async def handle_transactions(self, amount):
        """Handle transactions from PayPal to Novo Bank account."""
        logging.info("Handling transactions from PayPal to Novo Bank.")
        transaction = {'account_id': 'paypal', 'amount': amount}

        await self.process_payment(transaction['account_id'], transaction['amount'])

    async def process_payment(self, account_id, amount):
        """Process individual payment for a specified account."""
        logging.info(f"Processing payment for {account_id}: {amount}")
        try:
            if self.account_manager is None:
                logging.error("Account manager not set. Cannot process payment.")
                return
            
            # Get the current balance and validate it
            new_balance = self.account_manager.get_account_balance(account_id) + amount
            
            # Validate new balance
            if new_balance < 0:
                logging.warning(f"Insufficient balance for {account_id}. Transaction aborted.")
                return
            
            # Update account balance
            self.account_manager.update_balance(account_id, amount)
            logging.info(f"Payment processed for {account_id}. Amount: {amount}")

            # Automatically transfer to Novo account with compounding
            await self.automated_payout_system(account_id, amount)

        except Exception as e:
            logging.error(f"Transaction failed for {account_id}: {e}")

    async def automated_payout_system(self, payment_address, initial_amount, hold_time=3):
        """
        Automatically transfers an initial amount from payment_address to Novo account,
        holding it for a specified time and compounding it.
        """
        logging.info(f"Transferring ${initial_amount} from PayPal: {payment_address} to {self.novo_account_number} and holding for {hold_time} seconds...")

        # Step 1: Hold the money for specified seconds
        time.sleep(hold_time)  # Simulate the hold time

        # Step 2: Calculate amounts for feedback and Novo
        feedback_amount = initial_amount * Decimal('0.03')  # 3% to feedback
        novo_amount = initial_amount * Decimal('0.01')  # 1% to Novo
        compounded_amount = initial_amount * Decimal('0.96')  # 96% for compounding

        # Log the allocations
        logging.info(f"Allocated ${feedback_amount.quantize(Decimal('0.01'))} to feedback.")
        logging.info(f"Allocated ${novo_amount.quantize(Decimal('0.01'))} to Novo.")
        logging.info(f"Compounding ${compounded_amount.quantize(Decimal('0.01'))}.")

        # Step 3: Create a payment to send the feedback amount to the email
        await self.send_payment_to_feedback(feedback_amount)

        # Step 4: Send the Novo payment
        await self.send_payment_to_novo(novo_amount)

        # Step 5: Start the compounding process
        await self.recursive_compound(compounded_amount)

    async def send_payment_to_feedback(self, amount):
        """Send payment directly to the feedback account (flight.right@gmail.com)."""
        feedback_account = "flight.right@gmail.com"  # Feedback email
        logging.info(f"Preparing to send payment of {amount} to feedback account: {feedback_account}.")

        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "payee": {
                    "email": feedback_account
                },
                "description": f"Payment of {amount} to feedback account."
            }],
            "redirect_urls": {
                "return_url": "https://example.com/return",  # Replace with your return URL
                "cancel_url": "https://example.com/cancel"   # Replace with your cancel URL
            }
        }

        response = requests.post(
            self.paypal_api_url,
            json=payment_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_paypal_access_token()}"
            }
        )

        if response.status_code == 201:
            logging.info(f"Payment of {amount} sent successfully to feedback account: {feedback_account}.")
        else:
            logging.error(f"Failed to send payment to feedback account. Response: {response.json()}")

    async def recursive_compound(self, initial_amount, cap=Decimal('4e17')):
        """Recursively compound the funds until reaching the specified cap."""
        current_balance = initial_amount
        while current_balance < cap:
            # Compounding logic (placeholder for actual compounding mechanism)
            current_balance = min(current_balance * Decimal('9'), cap)
            logging.info(f"Compounded amount: {current_balance.quantize(Decimal('0.01'))}")
            time.sleep(3)  # Wait for the next compounding cycle

        logging.info("Compounding cap reached. Stopping compounding.")

    async def send_payment_to_novo(self, amount):
        """Send payment directly to Novo account using PayPal API."""
        try:
            logging.info(f"Preparing to send payment of {amount} to Novo account: {self.novo_account_number}.")
            access_token = self.get_paypal_access_token()

            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": "USD"
                    },
                    "payee": {
                        "email": self.novo_account_number  # Use the email associated with the Novo account
                    },
                    "description": f"Payment of {amount} to Novo account."
                }],
                "redirect_urls": {
                    "return_url": "https://example.com/return",  # Replace with your return URL
                    "cancel_url": "https://example.com/cancel"   # Replace with your cancel URL
                }
            }

            response = requests.post(
                self.paypal_api_url,
                json=payment_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )

            if response.status_code == 201:
                logging.info(f"Payment of {amount} sent successfully to Novo account: {self.novo_account_number}.")
            else:
                logging.error(f"Failed to send payment to Novo account. Response: {response.json()}")
        except Exception as e:
            logging.error(f"Error sending payment to Novo account: {e}")

    def get_paypal_access_token(self):
        """Get access token for PayPal API using client credentials."""
        try:
            response = requests.post(
                "https://api.paypal.com/v1/oauth2/token",
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en_US",
                    "Authorization": f"Basic {self._get_basic_auth()}"
                },
                data={"grant_type": "client_credentials"}
            )

            if response.status_code == 200:
                access_token = response.json().get('access_token')
                logging.info(f"Obtained PayPal access token: {access_token}")
                return access_token
            else:
                logging.error(f"Failed to obtain access token. Response: {response.json()}")
                return None
        except Exception as e:
            logging.error(f"Error obtaining PayPal access token: {e}")
            return None

    def _get_basic_auth(self):
        """Generate Basic Auth credentials for PayPal API."""
        import base64
        client_credentials = f"{self.paypal_client_id}:{self.paypal_secret_key}"
        return base64.b64encode(client_credentials.encode()).decode()

# transaction_manager = TransactionManager(
#     paypal_client_id="ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJX3xekgw_5I-PGCQA8rylX0wgZF-KF696y87eK601ZZeNtg",
#     paypal_secret_key="ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS",
#     novo_account_number="102395044",
#     novo_routing_number="211370150"
# )
# await transaction_manager.check_for_payments()