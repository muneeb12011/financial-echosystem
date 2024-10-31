# __init__.py

"""
A financial ecosystem simulation for automated payment processing.
"""

# Importing essential components for the financial ecosystem
from .escrow import EscrowManager  # Manages funds held in escrow
from .scheduler import Scheduler  # Schedules payment and release operations
from .transaction import TransactionManager  # Handles transaction processing and logging

__version__ = '1.0.0'
__author__ = 'Brandon'
