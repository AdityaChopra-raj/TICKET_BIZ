import hashlib
from datetime import datetime

# In-memory ledger list
ledger = []

def add_transaction(event_name: str, email: str, tickets_bought: int, timestamp: datetime):
    """
    Add a new transaction to the ledger.

    Args:
        event_name (str): Name of the event.
        email (str): Buyer email address.
        tickets_bought (int): Number of tickets purchased.
        timestamp (datetime): Time of purchase.
    """
    record = {
        "event_name": event_name,
        "email": email,
        "tickets_bought": tickets_bought,
        "timestamp": str(timestamp)
    }

    # Create a simple blockchain-style hash of the record
    record_string = f"{record['event_name']}{record['email']}{record['tickets_bought']}{record['timestamp']}"
    record_hash = hashlib.sha256(record_string.encode()).hexdigest()

    record["hash"] = record_hash

    ledger.append(record)


def get_ledger():
    """
    Retrieve the entire ledger.

    Returns:
        list[dict]: All ledger records.
    """
    return ledger
