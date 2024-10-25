# config.py

# Configuration settings
API_KEYS = {
    'venmo': 'your_venmo_api_key',  # Replace with your Venmo API key
    'paypal': 'your_paypal_api_key',  # Replace with your PayPal API key
    'cashapp': 'your_cashapp_api_key',  # Replace with your CashApp API key
    
    # Venmo account details
    'VENMO_ACCESS_TOKEN': "your_venmo_access_token_here",
    'VENMO_API_URL': "https://venmo.com/pay",
    'VENMO_USER_ID': "222164973891",
    'VENMO_ROUTING_NUMBER': "031101279",  # Routing number for Venmo

    # CashApp account details
    'CASHAPP_SECRET_KEY': "your_cashapp_secret_key_here",
    'CASHAPP_API_URL': "https://api.cash.app/v1/payments",
    'CASHAPP_ACCOUNT_NUMBER': "98971128727551668",
    'CASHAPP_ROUTING_NUMBER': "121000248",  # Routing number for CashApp

    # PayPal account details
    'PAYPAL_CLIENT_ID': "AQMT2VkIsLvlk0sZOV6C3mP-rOgcIumZo636FAGfjOCoYo34nTxaLMwsOda0XEIQaQfmXMWEcJIO1JAM",
    'PAYPAL_SECRET': "your_paypal_secret_here",
    'PAYPAL_API_URL': "https://api-m.paypal.com/v1/payments/payouts",
    'PAYPAL_EMAIL': "flight.right@gmail.com"
}

# Black Door app details
APP_DETAILS = {
    'APP_NAME': "Black Door",
    'CLIENT_ID': "AYb4xL8sOmXCPzKU7xvS-ma1P1BwuULGxut5APSf",
    'SECRET_KEY_1': "EloLcvD0Y1naigN-ZIHBOm8TMGpGCI2NrQeQZwn9",
    'SECRET_KEY_2': "ksQOFEsccwmR2n0lbk6Lwfv2-lx3S5C6IC_qXQnJ"
}

THRESHOLDS = {
    'amplification': 1000,
    'escrow_release': 500
}

# Logging settings
LOGGING_LEVEL = 'INFO'
