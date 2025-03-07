import os

# Configuration settings for Black Door and related payment systems

# API Keys and Endpoints
API_KEYS = {
    'PAYPAL_CLIENT_ID': os.getenv('PAYPAL_CLIENT_ID', 'ARB5HqrvzFFRgPnWAmKmWqM5QqwnaIednJ'),  # PayPal Client ID
    'PAYPAL_SECRET': os.getenv('PAYPAL_SECRET', 'ELiojntr74xZnpUwkZqDuA6rsAIXvQ6HB3Ks3EbeG1pnZauA6JI4KDTNw6aFajPu3rasyYd8i3KGtXFS'),  # PayPal Secret
    'PAYPAL_API_URL': "https://api-m.paypal.com/v1/payments/payouts",  # PayPal Payouts API URL
    'PAYPAL_EMAIL': os.getenv('PAYPAL_EMAIL', 'flight.right@gmail.com'),  # PayPal account email

    # Novo Bank account details for direct deposits
    'NOVO_ACCOUNT_NUMBER': os.getenv('NOVO_ACCOUNT_NUMBER', '102395044'),  # Novo Account Number
    'NOVO_ROUTING_NUMBER': os.getenv('NOVO_ROUTING_NUMBER', '211370150'),  # Novo Routing Number
    'NOVO_API_URL': "https://api.novo.co/v1/transfer"  # Update with actual Novo API URL if applicable
}

# Black Door app details for secure transactions
APP_DETAILS = {
    'APP_NAME': "Black Door",
    'CLIENT_ID': "AYb4xL8sOmXCPzKU7xvS-ma1P1BwuULGxut5APSf",
    'SECRET_KEY_1': "EloLcvD0Y1naigN-ZIHBOm8TMGpGCI2NrQeQZwn9",
    'SECRET_KEY_2': "ksQOFEsccwmR2n0lbk6Lwfv2-lx3S5C6IC_qXQnJ",
    'SMTP_USER': os.getenv('SMTP_USER', 'your_email@gmail.com'),  # Your email
    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', 'your_email_password'),  # Your email password
    'NOTIFICATION_EMAIL': os.getenv('NOTIFICATION_EMAIL', 'notification_email@example.com'),  # Recipient email for notifications
    'PAYMENT_FEEDBACK_EMAIL': os.getenv('PAYMENT_FEEDBACK_EMAIL', 'feedback_email@example.com')  # Feedback email
}

# Transaction thresholds
THRESHOLDS = {
    'AMPLIFICATION_FACTOR': 1000,  # Factor for amplification calculations
    'ESCROW_RELEASE_THRESHOLD': 500  # Minimum amount to trigger escrow release
}

# Amplification settings
AMPLIFICATION_SETTINGS = {
    'AMPLIFICATION_DURATION': 5,  # Duration in seconds for the amplification process
    'RELEASE_RATE': 0.01,  # Release rate as a percentage (1%)
    'NOVA_ALLOCATION': 0.01,  # Allocation percentage for Novo
    'FEEDBACK_ALLOCATION': 0.03,  # Feedback percentage to flight.right@gmail.com
}

# Logging settings for application-wide logging level
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')  # Default logging level

# Utility functions to get configuration values
def get_paypal_client_id():
    return API_KEYS['PAYPAL_CLIENT_ID']

def get_paypal_secret():
    return API_KEYS['PAYPAL_SECRET']

def get_novo_account_number():
    return API_KEYS['NOVO_ACCOUNT_NUMBER']

def get_novo_routing_number():
    return API_KEYS['NOVO_ROUTING_NUMBER']

def get_logging_level():
    return LOGGING_LEVEL
