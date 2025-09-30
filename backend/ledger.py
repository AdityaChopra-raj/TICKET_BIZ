import csv
from pathlib import Path
import uuid

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

def get_ledger():
    """Read the ledger CSV and return a list of transactions."""
    if not LEDGER_FILE.exists():
        return []

    ledger = []
    with open(LEDGER_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                row["num_tickets"] = int(row.get("num_tickets", 0) or 0)
            except ValueError:
                row["num_tickets"] = 0
            try:
                row["checked_in"] = int(row.get("checked_in", 0) or 0)
            except ValueError:
                row["checked_in"] = 0
            ledger.append(row)
    return ledger

def add_transaction(event, first_name, last_name, student_id, email, num_tickets):
    """Add a new transaction to the ledger."""
    uid = str(uuid.uuid4())
    header = ["uid", "event", "first_name", "last_name", "student_id", "email", "num_tickets", "checked_in"]

    # Create file with header if it doesn't exist
    file_exists = LEDGER_FILE.exists()
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists or LEDGER_FILE.stat().st_size == 0:
            writer.writerow(header)
        writer.writerow([uid, event, first_name, last_name, student_id, email, int(num_tickets), 0])

    return uid

def check_in_ticket(uid, num_people=1):
    """Update checked_in count for a ticket UID."""
    ledger = get_ledger()
    updated = False
    for row in ledger:
        if row["uid"] == uid:
            available = row["num_tickets"] - row["checked_in"]
            if available >= num_people:
                row["checked_in"] += num_people
                updated = True
            else:
                raise ValueError(f"Not enough remaining tickets to check in {num_people} people.")
            break
    else:
        raise ValueError("Ticket UID not found.")

    # Rewrite the ledger CSV
    with open(LEDGER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ledger[0].keys() if ledger else [])
        writer.writeheader()
        writer.writerows(ledger)

    return updated
