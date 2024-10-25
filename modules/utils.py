import logging

def setup_logging(level='INFO'):
    """Set up the logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging is set up.")

def validate_data(data):
    """Validate incoming data for required fields and types.

    Args:
        data (dict): Data to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    required_fields = ['account_id', 'amount']
    
    for field in required_fields:
        if field not in data:
            logging.warning(f"Missing field: {field}")
            return False
        if not isinstance(data[field], (int, float)) or data[field] < 0:
            logging.warning(f"Invalid data for field: {field}. Value: {data[field]}")
            return False

    logging.info("Data validation successful.")
    return True

# Example usage
if __name__ == "__main__":
    setup_logging('DEBUG')
    
    test_data = {
        'account_id': 'venmo',
        'amount': 100
    }
    
    if validate_data(test_data):
        logging.info("Data is valid.")
    else:
        logging.error("Data is invalid.")
