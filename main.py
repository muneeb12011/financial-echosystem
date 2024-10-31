import logging
import requests
import os
import signal
import sys
import time
import sqlite3
from decimal import Decimal, getcontext
from modules.account import AccountManager
from modules.escrow import EscrowManager
from modules.transaction import TransactionManager
from modules.scheduler import Scheduler
from modules.utils import setup_logging, validate_transaction_data
from smtplib import SMTP
from email.mime.text import MIMEText

# Increase precision for extreme growth calculations
getcontext().prec = 10000

# Load API Credentials and constants from environment variables
API_KEYS = {
    'PAYPAL_CLIENT_ID': os.getenv('PAYPAL_CLIENT_ID'),
    'PAYPAL_SECRET': os.getenv('PAYPAL_SECRET'),
    'PAYPAL_API_URL': os.getenv('PAYPAL_API_URL'),
    'NOVO_API_URL': os.getenv('NOVO_API_URL')
}

APP_DETAILS = {
    'SMTP_USER': os.getenv('SMTP_USER'),
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
    'NOTIFICATION_EMAIL': os.getenv('NOTIFICATION_EMAIL'),
    'PAYMENT_FEEDBACK_EMAIL': os.getenv('PAYMENT_FEEDBACK_EMAIL'),
    'NOVO_ACCOUNT_NUMBER': os.getenv('NOVO_ACCOUNT_NUMBER'),
    'NOVO_ROUTING_NUMBER': os.getenv('NOVO_ROUTING_NUMBER'),
}

# Black Door System Constants
ESCROW_CAP = Decimal('4e17')  # Cap at 4e17
DAILY_RELEASE_RATE = Decimal('0.01')  # Daily release rate of 1%
PAYMENT_THRESHOLD = Decimal('250000')  # Minimum escrow for payouts

# Setup logging configuration
setup_logging()

# Database setup
def init_db():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        account_id TEXT,
        amount REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn

# Send email notification
def send_notification(subject, message):
    try:
        with SMTP(APP_DETAILS['SMTP_USER'], 587) as smtp:  # Using TLS on port 587
            smtp.starttls()
            smtp.login(APP_DETAILS['SMTP_USER'], APP_DETAILS['SMTP_PASSWORD'])
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = APP_DETAILS['SMTP_USER']
            msg['To'] = APP_DETAILS['NOTIFICATION_EMAIL']
            smtp.send_message(msg)
            logging.info(f"Notification sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

# Handle payment to PayPal/Novo with retry mechanism
def perform_payment(account_id, user_identifier, amount_cents, retries=3):
    logging.info(f"Initiating payment of ${Decimal(amount_cents) / 100:.2f} to {user_identifier} via {account_id}.")
    for attempt in range(retries):
        try:
            if account_id == 'paypal':
                return process_paypal_payment(user_identifier, amount_cents)
            elif account_id == 'novo':
                return process_novo_transfer(amount_cents)
            else:
                raise ValueError("Unsupported account type.")
        except Exception as e:
            logging.error(f"Error performing payment on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logging.info(f"Retrying payment in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {'status': 'error', 'message': str(e)}

# Process PayPal payments
def process_paypal_payment(user_identifier, amount_cents):
    payload = {
        'sender_batch_header': {
            'sender_batch_id': str(int(time.time())),
            'email_subject': 'Black Door Payment'
        },
        'items': [{
            'recipient_type': 'EMAIL',
            'amount': {
                'value': str(Decimal(amount_cents) / 100),
                'currency': 'USD'
            },
            'receiver': APP_DETAILS['PAYMENT_FEEDBACK_EMAIL'],
            'note': 'Black Door System Payment'
        }]
    }
    response = requests.post(
        API_KEYS['PAYPAL_API_URL'],
        auth=(API_KEYS['PAYPAL_CLIENT_ID'], API_KEYS['PAYPAL_SECRET']),
        json=payload
    )
    return handle_response(response, user_identifier, 'paypal', amount_cents)

# Process Novo account transfers
def process_novo_transfer(amount_cents):
    logging.info(f"Transferring ${Decimal(amount_cents) / 100:.2f} to Novo account (Account: {APP_DETAILS['NOVO_ACCOUNT_NUMBER']}, Routing: {APP_DETAILS['NOVO_ROUTING_NUMBER']}).")
    
    payload = {
        'account_number': APP_DETAILS['NOVO_ACCOUNT_NUMBER'],
        'routing_number': APP_DETAILS['NOVO_ROUTING_NUMBER'],
        'amount': str(Decimal(amount_cents) / 100),
        'currency': 'USD'
    }

    response = requests.post(API_KEYS['NOVO_API_URL'], json=payload)
    return handle_response(response, 'Novo', 'novo', amount_cents)

# Handle API response and log errors or successes
def handle_response(response, user_identifier, account_id, amount_cents):
    logging.info(f"API Response Status: {response.status_code}")
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    
    if response.status_code in (200, 201):
        logging.info(f"Payment successful: {response.json()}")
        cursor.execute('INSERT INTO transactions (user_id, account_id, amount, status) VALUES (?, ?, ?, ?)',
                       (user_identifier, account_id, Decimal(amount_cents) / 100, 'success'))
        conn.commit()
        send_notification('Payment Successful', f'Payment of ${Decimal(amount_cents) / 100:.2f} was successful.')
        return {'status': 'success', 'data': response.json()}
    else:
        logging.error(f"Payment failed: {response.status_code} - {response.text}")
        cursor.execute('INSERT INTO transactions (user_id, account_id, amount, status) VALUES (?, ?, ?, ?)',
                       (user_identifier, account_id, Decimal(amount_cents) / 100, 'failure'))
        conn.commit()
        send_notification('Payment Failed', f'Payment of ${Decimal(amount_cents) / 100:.2f} failed: {response.status_code} - {response.text}')
        raise Exception(f"Payment failed: {response.status_code} - {response.text}")

# Graceful shutdown handling
def signal_handler(sig, frame):
    logging.info("Gracefully shutting down the payment loop...")
    sys.exit(0)

# Handle recursive compounding logic
def handle_recursive_compounding(amount_cents):
    compounding_rate = Decimal('0.01')  # 1% for Novo
    feedback_rate = Decimal('0.03')  # 3% for feedback
    remaining_balance = Decimal(amount_cents) / 100

    # Calculate amounts for Novo and Feedback
    novo_amount = remaining_balance * compounding_rate
    feedback_amount = remaining_balance * feedback_rate
    compounding_amount = remaining_balance - (novo_amount + feedback_amount)

    # Process payments to Novo and Feedback
    if feedback_amount > 0:
        process_paypal_payment(APP_DETAILS['PAYMENT_FEEDBACK_EMAIL'], feedback_amount * 100)  # Convert to cents
    if novo_amount > 0:
        process_novo_transfer(novo_amount * 100)  # Convert to cents

    return compounding_amount

# Main execution logic
def main():
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C for graceful shutdown
    logging.info("Starting financial ecosystem simulation.")

    # Initialize database
    db_conn = init_db()

    # Initialize managers
    account_manager = AccountManager(API_KEYS)
    escrow_manager = EscrowManager(perform_payment)
    transaction_manager = TransactionManager(account_manager, API_KEYS['PAYPAL_SECRET'], APP_DETAILS['NOVO_ACCOUNT_NUMBER'], APP_DETAILS['NOVO_ROUTING_NUMBER'])
    scheduler = Scheduler(transaction_manager, escrow_manager)

    try:
        account_manager.initialize_accounts()
        escrow_manager.initialize_escrow()

        # Infinite loop for managing escrow and transactions
        while True:
            logging.info("Checking for pending payments...")
            pending_payments = escrow_manager.get_pending_payments()
            logging.info(f"Pending payments: {pending_payments}")

            if not pending_payments:
                logging.info("No pending payments to process. Sleeping for a bit...")
                time.sleep(10)  # Sleep for a shorter time before checking again
                continue  # Skip the rest of the loop if there are no payments

            for payment in pending_payments:
                logging.info(f"Processing payment: {payment}")
                if validate_transaction_data(payment):
                    user_id = payment['user_id']
                    amount = payment['amount']
                    account_id = payment['account_id']

                    # Start timer for processing
                    start_time = time.time()
                    processing_duration = 5  # 3-5 seconds
                    elapsed_time = 0

                    while elapsed_time < processing_duration:
                        logging.info(f"Processing payment for {elapsed_time:.1f} seconds...")
                        elapsed_time = time.time() - start_time
                        time.sleep(1)  # Sleep for 1 second to simulate processing time

                    # Execute the payment after processing
                    amount_to_process = handle_recursive_compounding(amount * 100)  # Pass amount in cents
                    logging.info(f"Processed payment of ${amount_to_process:.2f}.")
                    escrow_manager.update_payment_status(payment['id'], 'processed')

            # Sleep before the next round of processing
            logging.info("Finished processing payments. Sleeping before next check...")
            time.sleep(30)  # Check for new payments every 30 seconds

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        db_conn.close()
        logging.info("Exiting application.")

if __name__ == "__main__":
    main()
    