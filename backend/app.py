import streamlit as st
from PIL import Image
from pathlib import Path
import csv, uuid
from datetime import datetime
import smtplib
from email.message import EmailMessage

from events_data import EVENTS
from ledger import add_block, read_ledger

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
TICKETS_CSV = BASE_DIR / "tickets.csv"

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# Load CSS
with open(BASE_DIR / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="header-title">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Browse, buy, and check-in securely with blockchain verification</p>', unsafe_allow_html=True)

# Session state
if "selected_event" not in st.session_state: st.session_state["selected_event"] = None

# -------------------- HELPER FUNCTIONS --------------------
def generate_uid(): return uuid.uuid4().hex[:10].upper()

def save_ticket(uid, first, last, email, event_name):
    exists = TICKETS_CSV.exists()
    with open(TICKETS_CSV,"a",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["uid","first_name","last_name","email","event","purchased_at","checked_in"])
        writer.writerow([uid, first, last, email, event_name, datetime.utcnow().isoformat(),""])

def mark_checked_in(uid):
    if not TICKETS_CSV.exists(): return False
    rows = []
    with open(TICKETS_CSV,"r",newline="",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["uid"] == uid:
                r["checked_in"] = datetime.utcnow().isoformat()
            rows.append(r)
    with open(TICKETS_CSV,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["uid","first_name","last_name","email","event","purchased_at","checked_in"])
        writer.writeheader()
        writer.writerows(rows)
    return True

def send_ticket_email(to_email, first, last, uid, event_name):
    try:
        email_conf = st.secrets["email"]
        msg = EmailMessage()
        msg["Subject"] = f"Ticket Confirmation: {event_name}"
        msg["From"] = email_conf["address"]
        msg["To"] = to_email
        msg.set_content(f"Hi {first} {last},\n\nYour ticket UID: {uid}\nEvent: {event_name}\n\nShow this at check-in.\n\n— Ticket_Biz")
        s = smtplib.SMTP_SSL(email_conf.get("smtp_host","smtp.gmail.com"), int(email_conf.get("smtp_port",465)))
        s.login(email_conf["address"], email_conf["password"])
        s.send_message(msg)
        s.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# -------------------- DISPLAY EVENTS --------------------
st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)
for ev in EVENTS:
    dimmed_class = "dimmed" if st.session_state["selected_event"] and st.session_state["selected_event"] != ev["name"] else ""
    st.markdown(f'<div class="card {dimmed_class}">', unsafe_allow_html=True)
    try:
        img = Image.open(ASSETS_DIR / ev["image"])
    except:
        img = Image.open(ASSETS_DIR / "pla_
