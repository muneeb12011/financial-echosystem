# Financial Ecosystem - Black Door Payment System

## Overview
This project implements a financial ecosystem where small amounts (referred to as "pennies") are exponentially amplified and distributed across various payment endpoints such as Venmo, CashApp, PayPal, and Nova Bank. The project revolves around an automatic, scheduled loop that sends money from the `Black Door` system to these accounts via API integration.

## Features
- **Automatic payment execution**: The system automatically sends payments to the connected accounts (Venmo, PayPal, CashApp) once a payment is triggered.
- **Scheduled payouts**: Payments are routinely sent based on a defined schedule until the system is manually stopped.
- **Escrow management**: Payments are held in escrow, amplified, and then distributed according to predefined rules.
- **API Integration**: Secure integration with Venmo, CashApp, PayPal, and Nova Bank APIs to process real money transfers.

## System Architecture
The project is built using Python and is organized into modules to handle different aspects of the system:
- `account.py`: Manages user accounts, including balance updates and account information retrieval.
- `penny.py`: Handles the amplification logic for pennies.
- `escrow.py`: Manages escrow functionalities.
- `scheduler.py`: Manages scheduled payouts and periodic payment releases.
- `api_integration.py`: Interfaces with Venmo, PayPal, CashApp, and Nova Bank APIs to process payments.
- `transaction.py`: Manages transactions between accounts and the Black Door system.

## Requirements
- Python 3.8+
- `requests` (for API integration)
- `decimal` (for precise financial calculations)
- `threading` (for concurrent operations and scheduled payouts)
- Any additional dependencies listed in `requirements.txt`

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd financial_ecosystem
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # For MacOS/Linux
    venv\Scripts\activate      # For Windows
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up API credentials**: 
    Ensure your API keys for Venmo, CashApp, PayPal, and Nova Bank are correctly set in the `config.py` or passed securely as environment variables.

5. **Configuration**:
    Update the API keys and secrets in `config.py` or in the environment variables:
    - Venmo User ID
    - CashApp Account Number
    - PayPal Email
    - Nova Bank Account details

6. **Run the system**:
    The system is triggered once a payment is made. After receiving a dollar amount, the system will process the payment and automatically send the funds to the respective accounts based on the API setup.

    To run the main loop:
    ```bash
    python main.py
    ```

    The code will run indefinitely, sending payments according to the predefined schedule.

## Testing

The project includes a set of unit tests to ensure the correctness of account management, balance updates, and transaction handling.

1. **Run tests**:
    ```bash
    python -m unittest discover -s tests
    ```

    Ensure all tests pass, especially the API integration tests in `test_api.py` and `test_account.py`.

## API Integration

### Venmo
Ensure that your Venmo API credentials (User ID and Access Token) are set up properly. The system uses Venmo’s API to handle balance transfers.

### CashApp
Your CashApp API credentials (Account Number and Secret Key) should be set up in the configuration to securely transfer money to CashApp accounts.

### PayPal
PayPal integration is handled via API using the provided PayPal Email and associated API Key.

### Nova Bank
The Nova Bank integration is managed similarly, with transfers executed to the specified Nova Bank account using the configured credentials.

## File Structure


## Deployment

The system is designed to be deployed on any server with Python support. Ensure that all environment variables for API credentials are securely managed, and consider using a process manager like `supervisord` or `systemd` to keep the service running.

## Logging

All major actions within the system are logged for auditing and debugging purposes. Logs will record account balance updates, transaction status, API calls, and errors.

## Future Enhancements

- **Improved error handling**: Enhance error-handling logic to account for network failures and API rate limits.
- **Database integration**: Integrate with a database like PostgreSQL or MySQL for persistent balance tracking and transaction history.
- **UI Dashboard**: Build a dashboard to monitor the status of the Black Door system, track payments, and view logs in real-time.

## License

This project is licensed under the MIT License.

#   f i n a n c i a l - e c h o s y s t e m  
 