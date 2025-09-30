import csv
from pathlib import Path
import uuid

BASE_DIR = Path(__file__).resolve().parent
LEDGER_FILE = BASE_DIR / "ledger.csv"

# -----------------------------
# Ensure ledger file exists
# -----------------------------
if not LEDGER_FILE.exists():
    with open(LEDGER_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["uid", "event", "first_name", "last_name", "student_id", "num_tickets", "email", "checked_in"]
        )
        writer.writeheader()

# -----------------------------
# Add a transaction (ticket purchase)
# -----------------------------
def add_transaction(event_name, first_name, last_name, student_id, num_tickets, email):
    uid = str(uuid.uuid4())[:8]  # Short UID
    with open(LEDGER_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["uid", "event", "first_name", "last_name", "student_id", "num_tickets", "email", "checked_in"]
        )
        writer.writerow({
            "uid": uid,
            "event": event_name,
            "first_name": first_name,
            "last_name": last_name,
            "student_id": student_id,
            "num_tickets": num_tickets,
            "email": email,
            "checked_in": 0
        })
    return uid

# -----------------------------
# Get ledger data
# -----------------------------
def get_ledger():
    records = []
    with open(LEDGER_FILE, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["num_tickets"] = int(row["num_tickets"])
            row["checked_in"] = int(row["checked_in"])
            records.append(row)
    return records

# -----------------------------
# Check in a ticket
# -----------------------------
def check_in_ticket(uid, email, num_people):
    ledger = get_ledger()
    updated = False
    for row in ledger:
        if row["uid"] == uid and row["email"] == email:
            remaining = row["num_tickets"] - row["checked_in"]
            if num_people <= remaining:
                row["checked_in"] += num_people
                updated = True
                message = f"{num_people} person(s) checked in successfully. {row['num_tickets'] - row['checked_in']} slots left."
            else:
                return False, f"Cannot check in {num_people} person(s). Only {remaining} slots available."
            break
    if not updated:
        return False, "Ticket UID or Email not found."

    # Save updated ledger
    with open(LEDGER_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["uid", "event", "first_name", "last_name", "student_id", "num_tickets", "email", "checked_in"])
        writer.writeheader()
        for row in ledger:
            writer.writerow(row)
    return True, message
