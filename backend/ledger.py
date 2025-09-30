import csv
from pathlib import Path
from datetime import datetime

LEDGER_FILE = Path(__file__).parent / "ledger.csv"
FIELDNAMES = ["timestamp", "event_id", "event_name", "first_name", "last_name", "student_id", "email", "num_tickets", "num_checked_in", "uid", "price"]

def get_ledger():
    ledger = []
    if not LEDGER_FILE.exists():
        return ledger
    with open(LEDGER_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Safely parse num_tickets
            try:
                row["num_tickets"] = int(row.get("num_tickets", 0))
            except ValueError:
                row["num_tickets"] = 0

            # Safely parse num_checked_in
            try:
                row["num_checked_in"] = int(row.get("num_checked_in", 0))
            except ValueError:
                row["num_checked_in"] = 0

            ledger.append(row)
    return ledger

def save_ledger(ledger):
    with open(LEDGER_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(ledger)

def add_transaction(event_id, event_name, first_name, last_name, student_id, email, num_tickets, uid, price=0):
    ledger = get_ledger()
    transaction = {
        "timestamp": datetime.now().isoformat(),
        "event_id": event_id,
        "event_name": event_name,
        "first_name": first_name,
        "last_name": last_name,
        "student_id": student_id,
        "email": email,
        "num_tickets": num_tickets,
        "num_checked_in": 0,
        "uid": uid,
        "price": price
    }
    ledger.append(transaction)
    save_ledger(ledger)

def update_check_in(uid, num_checkin=1):
    ledger = get_ledger()
    updated = False
    for row in ledger:
        if row["uid"] == uid:
            row["num_checked_in"] += num_checkin
            updated = True
            break
    if updated:
        save_ledger(ledger)
    return updated

def get_tickets_sold(event_id):
    ledger = get_ledger()
    total = sum(row["num_tickets"] for row in ledger if row["event_id"] == event_id)
    return total

def get_checked_in(event_id):
    ledger = get_ledger()
    total = sum(row["num_checked_in"] for row in ledger if row["event_id"] == event_id)
    return total
