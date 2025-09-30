# ledger.py

import csv
from pathlib import Path
from datetime import datetime

LEDGER_FILE = Path(__file__).parent / "ledger.csv"

# Ensure ledger file exists
if not LEDGER_FILE.exists():
    with open(LEDGER_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp",
            "event_id",
            "event_name",
            "first_name",
            "last_name",
            "student_id",
            "email",
            "num_tickets",
            "num_checked_in"
        ])
        writer.writeheader()


def add_transaction(event_id, event_name, first_name, last_name, student_id, email, num_tickets):
    """Add a new ticket purchase transaction to the ledger."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LEDGER_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp",
            "event_id",
            "event_name",
            "first_name",
            "last_name",
            "student_id",
            "email",
            "num_tickets",
            "num_checked_in"
        ])
        writer.writerow({
            "timestamp": now,
            "event_id": event_id,
            "event_name": event_name,
            "first_name": first_name,
            "last_name": last_name,
            "student_id": student_id,
            "email": email,
            "num_tickets": num_tickets,
            "num_checked_in": 0
        })


def check_in(uid_email_mapping, tickets_to_check_in=1):
    """
    Update ledger for check-ins.
    uid_email_mapping: tuple (student_id, email)
    tickets_to_check_in: number of tickets to check in
    """
    student_id, email = uid_email_mapping
    updated_rows = []
    with open(LEDGER_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["student_id"] == student_id and row["email"] == email:
                already_checked = int(row["num_checked_in"])
                total_tickets = int(row["num_tickets"])
                can_check_in = min(tickets_to_check_in, total_tickets - already_checked)
                row["num_checked_in"] = already_checked + can_check_in
            updated_rows.append(row)

    with open(LEDGER_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


def get_ledger():
    """Return the entire ledger as a list of dicts."""
    ledger = []
    with open(LEDGER_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["num_tickets"] = int(row["num_tickets"])
            row["num_checked_in"] = int(row["num_checked_in"])
            row["event_id"] = int(row["event_id"])
            ledger.append(row)
    return ledger


def get_tickets_sold(event_id):
    """Return total tickets sold for a specific event."""
    ledger = get_ledger()
    return sum(row["num_tickets"] for row in ledger if row["event_id"] == event_id)


def get_checked_in(event_id):
    """Return total checked-in count for a specific event."""
    ledger = get_ledger()
    return sum(row["num_checked_in"] for row in ledger if row["event_id"] == event_id)
