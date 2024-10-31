import logging
import asyncio
from typing import Dict, Any, List, Union
from decimal import Decimal
import requests  # Import for making HTTP requests
import time  # Import for time delay

class AccountError(Exception):
    """Custom exception for account-related errors."""
    pass

class AccountManager:
    def __init__(self, api_keys: Dict[str, str], max_balance: Decimal = Decimal('10000.0')):
        """
        Initializes the AccountManager with provided API keys and a maximum balance limit.

        :param api_keys: Dictionary containing API keys for different payment platforms.
        :param max_balance: Maximum balance allowed for any account.
        """
        self.api_keys = api_keys
        self.accounts: Dict[str, Decimal] = {}
        self.transaction_history: Dict[str, List[str]] = {}
        self.max_balance = max_balance
        self.initialize_accounts()

    def initialize_accounts(self) -> None:
        """Initializes account balances and transaction history to empty."""
        logging.info("Initializing accounts.")
        self.accounts = {
            'paypal': Decimal('0.0'),
            'nova': Decimal('0.0')  # Novo account only
        }
        self.transaction_history = {key: [] for key in self.accounts.keys()}
        logging.info(f"Accounts initialized: {self.accounts}")

    async def get_account_balance(self, account_id: str) -> Decimal:
        """Asynchronously retrieves the balance for the specified account."""
        if account_id not in self.accounts:
            logging.error(f"Account {account_id} does not exist.")
            raise AccountError(f"Account {account_id} not found.")
        balance = self.accounts[account_id]
        logging.info(f"Retrieved balance for {account_id}: {balance}")
        return balance

    async def update_balance(self, account_id: str, amount: Union[float, Decimal]) -> None:
        """
        Asynchronously updates the balance of the specified account and logs the transaction.

        :param account_id: The ID of the account to update.
        :param amount: The amount to add (or subtract if negative) from the account balance.
        :raises AccountError: If the account does not exist or if the balance would exceed limits.
        """
        if account_id not in self.accounts:
            logging.error(f"Account {account_id} does not exist.")
            raise AccountError(f"Account {account_id} not found.")

        amount = Decimal(amount)
        new_balance = self.accounts[account_id] + amount

        if new_balance < 0:
            logging.error(f"Insufficient funds for {account_id}. Attempted update: {amount}")
            raise AccountError(f"Insufficient funds in account {account_id}.")
        elif new_balance > self.max_balance:
            logging.error(f"Balance exceeds the limit for {account_id}. Attempted update: {amount}")
            raise AccountError(f"Balance exceeds the limit for {account_id}.")

        self.accounts[account_id] = new_balance
        transaction_type = 'Deposit' if amount > 0 else 'Withdrawal'
        self.transaction_history[account_id].append(f"{transaction_type}: {amount}, New Balance: {new_balance}")
        logging.info(f"Updated {account_id} balance: {new_balance}")

    async def get_transaction_history(self, account_id: str) -> List[str]:
        """
        Asynchronously retrieves the transaction history for a specified account.

        :param account_id: The ID of the account to retrieve history for.
        :return: A list of transactions for the account.
        """
        if account_id not in self.transaction_history:
            logging.error(f"Account {account_id} not found for transaction history.")
            raise AccountError(f"Account {account_id} not found.")
        logging.info(f"Retrieved transaction history for {account_id}.")
        return self.transaction_history[account_id]

    async def get_nova_account_details(self) -> Dict[str, Any]:
        """Asynchronously retrieves the Novo account details."""
        return {
            "account_number": self.api_keys.get("NOVO_ACCOUNT_NUMBER"),
            "routing_number": self.api_keys.get("NOVO_ROUTING_NUMBER")
        }

    async def get_paypal_account_email(self) -> str:
        """Asynchronously retrieves the PayPal account email."""
        return self.api_keys.get("PAYPAL_EMAIL")

    async def recursive_compounding(self, amount: Decimal) -> None:
        """
        Implements the recursive compounding system for fund allocation.

        :param amount: The total amount to compound.
        """
        allocation_nova = amount * Decimal('0.01')  # 1% to Novo
        feedback_amount = amount * Decimal('0.03')  # 3% feedback
        compound_amount = amount - (allocation_nova + feedback_amount)

        await self.update_balance('nova', allocation_nova)
        await self.update_balance('paypal', feedback_amount)

        # Logging the allocation
        logging.info(f"Allocated {allocation_nova} to Novo, {feedback_amount} as feedback.")
        logging.info(f"Remaining balance for compounding: {compound_amount}")

    async def send_payment_to_novo(self, amount: Decimal) -> None:
        """
        Sends a payment to the Novo account and updates the balance.

        :param amount: The amount to send to the Novo account.
        """
        await self.update_balance('paypal', -amount)  # Deduct from PayPal account
        novo_details = await self.get_nova_account_details()

        # Wait for 3-5 seconds before processing the payment
        await asyncio.sleep(4)  # Simulating the 3-5 second wait

        # Example payload for sending payment
        payload = {
            "amount": str(amount),
            "account_number": novo_details['account_number'],
            "routing_number": novo_details['routing_number']
        }
        
        # This URL would typically be your server endpoint to handle payment processing
        response = requests.post("https://your-server-endpoint.com/send_payment", json=payload)

        if response.status_code == 200:
            logging.info(f"Payment of {amount} sent to Novo account successfully.")
        else:
            logging.error(f"Failed to send payment: {response.text}")
            # If payment fails, rollback the balance update
            await self.update_balance('paypal', amount)

# Example of how to run an asynchronous method
async def main():
    api_keys = {
        'PAYPAL_EMAIL': "flight.right@gmail.com",
        'NOVO_ACCOUNT_NUMBER': "102395044",
        'NOVO_ROUTING_NUMBER': "211370150"
    }
    manager = AccountManager(api_keys)

    await manager.update_balance('paypal', 500)  # Simulate receiving a payment
    await manager.recursive_compounding(200)  # Simulate recursive compounding
    await manager.send_payment_to_novo(200)  # Simulate sending payment to Novo
    balance = await manager.get_account_balance('paypal')
    history = await manager.get_transaction_history('paypal')
    print(f"PayPal Balance: {balance}, History: {history}")

# Run the example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    asyncio.run(main())
