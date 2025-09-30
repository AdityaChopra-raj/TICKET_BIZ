# ledger.py

import hashlib
import time
import uuid

# In-memory ledger (you could replace with DB or file later)
ledger = []

def generate_hash(data: str) -> str:
    """Generate a unique SHA256 hash for transaction integrity."""
    return hashlib.sha256(data.encode()).hexdigest()

def add_transaction(event, first_name, last_name, student_id, tickets, email="N/A"):
    """Add a ticket purchase transaction to the ledger."""
    tx_id = str(uuid.uuid4())  # unique ticket UID
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    data_str = f"{event}{first_name}{last_name}{student_id}{tickets}{timestamp}{tx_id}"
    tx_hash = generate_hash(data_str)

    tx = {
        "uid": tx_id,
        "event": event,
        "first_name": first_name,
        "last_name": last_name,
        "student_id": student_id,
        "email": email,
        "tickets": tickets,
        "timestamp": timestamp,
        "hash": tx_hash,
        "checked_in": 0,  # start with 0 checked-in
    }

    ledger.append(tx)
    return tx_id  # return UID to user

def get_ledger():
    """Return the current blockchain ledger."""
    return ledger

def check_in_transaction(ticket_uid: str, count: int = 1) -> bool:
    """
    Check in people for a given ticket UID.
    Returns True if check-in successful, False otherwise.
    """
    for tx in ledger:
        if tx["uid"] == ticket_uid:
            # Ensure check-in doesn't exceed purchased tickets
            if tx["checked_in"] + count <= tx["tickets"]:
                tx["checked_in"] += count
                return True
            return False
    return False
