import streamlit as st
from PIL import Image
from pathlib import Path
import csv
import uuid
from datetime import datetime
import hashlib
import smtplib
from email.message import EmailMessage

# Directories
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
TICKETS_CSV = BASE_DIR / "tickets.csv"
LEDGER_CSV = BASE_DIR / "ledger.csv"

st.set_page_config(page_title="TicketBiz Clone", layout="wide")

# Load CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

local_css(BASE_DIR / "styles/style.css")

# Sample events data
EVENTS = [
    {"name":"Diwali Dance","desc":"Celebrate Diwali with music and dance!","price":500,"image":"diwali.jpeg"},
    {"name":"Freshers Party","desc":"Welcome the new batch with fun and games.","price":300,"image":"freshers.jpeg"},
    {"name":"Navratri Pooja","desc":"Join the spiritual celebrations of Navratri.","price":400,"image":"navratri.jpg"},
    {"name":"Ravan Dahan","desc":"Witness the traditional Ravan Dahan festival.","price":350,"image":"ravan.jpeg"},
]

# --- Helpers ---
def generate_uid():
    return uuid.uuid4().hex[:10].upper()

# Blockchain simulation
def hash_block(prev_hash, uid, first, last, action, timestamp):
    block_str = f"{prev_hash}{uid}{first}{last}{action}{timestamp}"
    return hashlib.sha256(block_str.encode()).hexdigest()

def add_block(uid, first, last, action):
    timestamp = datetime.utcnow().isoformat()
    prev_hash = ""
    ledger_rows = []
    if LEDGER_CSV.exists():
        with open(LEDGER_CSV,"r",newline="",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ledger_rows.append(row)
        prev_hash = ledger_rows[-1]["hash"] if ledger_rows else ""
    block_hash = hash_block(prev_hash, uid, first, last, action, timestamp)
    index = len(ledger_rows) + 1
    row = {"index":index,"uid":uid,"first_name":first,"last_name":last,"action":action,"timestamp":timestamp,"previous_hash":prev_hash,"hash":block_hash}
    ledger_rows.append(row)
    with open(LEDGER_CSV,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["index","uid","first_name","last_name","action","timestamp","previous_hash","hash"])
        writer.writeheader()
        writer.writerows(ledger_rows)
    return row

def read_ledger():
    rows = []
    if LEDGER_CSV.exists():
        with open(LEDGER_CSV,"r",newline="",encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    return rows

# Save tickets
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

# Send email
def send_ticket_email(to_email, first, last, uid, event_name):
    try:
        email_conf = st.secrets["email"]
        msg = EmailMessage()
        msg["Subject"] = f"Ticket Confirmation: {event_name}"
        msg["From"] = email_conf["address"]
        msg["To"] = to_email
        msg.set_content(f"Hi {first} {last},\n\nYour ticket UID: {uid}\nEvent: {event_name}\n\nShow this at check-in.\n\n— TicketBiz Clone")
        s = smtplib.SMTP_SSL(email_conf.get("smtp_host","smtp.gmail.com"), int(email_conf.get("smtp_port",465)))
        s.login(email_conf["address"], email_conf["password"])
        s.send_message(msg)
        s.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# Session state
if "buy_event" not in st.session_state: st.session_state["buy_event"] = None
if "show_checkin" not in st.session_state: st.session_state["show_checkin"] = False
if "show_ledger" not in st.session_state: st.session_state["show_ledger"] = False

# --- Title & Subtitle ---
st.markdown('<h1 style="text-align:center; color:white;">🎟 TicketBiz — Event Ticketing</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#ccc;">Browse events, buy tickets, and check-in securely using our blockchain ledger.</p>', unsafe_allow_html=True)

# --- Events Section ---
st.markdown('<h2 style="text-align:center; color:#e50914;">🎬 Featured Events</h2>', unsafe_allow_html=True)
st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)

for ev in EVENTS:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        img_path = ASSETS_DIR / ev.get("image","placeholder.jpeg")
        try:
            img = Image.open(img_path)
        except:
            img = Image.open(ASSETS_DIR / "placeholder.jpeg")
        st.image(img, use_column_width=True)
        st.markdown(f"<h3>{ev['name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p>{ev.get('desc','')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='price'>Price: ₹{ev.get('price',100)}</p>", unsafe_allow_html=True)
        if st.button(f"Buy — {ev['name']}", key=f"buy_{ev['name']}"):
            st.session_state["buy_event"] = ev["name"]
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Purchase Form ---
if st.session_state["buy_event"]:
    ev_name = st.session_state["buy_event"]
    st.markdown(f"<h2 style='text-align:center; color:#e50914;'>💳 Purchase Ticket — {ev_name}</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        first = st.text_input("First Name", key="first")
        last = st.text_input("Last Name", key="last")
        email = st.text_input("Email", key="email")
    with col2:
        st.write("Payment simulated (demo).")
        if st.button("Confirm Purchase"):
            if not (first and last and email):
                st.error("Enter first name, last name, and email")
            else:
                uid = generate_uid()
                save_ticket(uid, first, last, email, ev_name)
                add_block(uid, first, last, "buy")
                ok, err = send_ticket_email(email, first, last, uid, ev_name)
                if ok: st.success(f"Ticket purchased! UID: {uid}. Email sent.")
                else: st.warning(f"Ticket purchased but email failed: {err}")
                st.session_state["show_checkin"] = True
                st.session_state["show_ledger"] = True

# --- Check-in ---
if st.session_state["show_checkin"]:
    st.markdown("<h2 style='text-align:center; color:#e50914;'>✅ Ticket Check-In</h2>", unsafe_allow_html=True)
    uid_input = st.text_input("Enter ticket UID for check-in", key="check_uid")
    if st.button("Check In"):
        if not uid_input:
            st.error("Enter a UID")
        else:
            found = False
            if TICKETS_CSV.exists():
                with open(TICKETS_CSV,"r",newline="",encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r["uid"] == uid_input:
                            found = True
                            if r.get("checked_in"):
                                st.warning("Ticket already checked in.")
                            else:
                                mark_checked_in(uid_input)
                                add_block(uid_input,r["first_name"],r["last_name"],"check-in")
                                ok, err = send_ticket_email(r["email"], r["first_name"], r["last_name"], uid_input, r["event"])
                                if ok: st.success("Check-in successful! Email sent.")
                                else: st.success("Check-in successful! Email failed.")
                            break
            if not found:
                st.error("Ticket UID not found.")

# --- Ledger ---
if st.session_state["show_ledger"]:
    st.markdown("<h2 style='text-align:center; color:#e50914;'>🔗 Blockchain Ledger</h2>", unsafe_allow_html=True)
    ledger_rows = read_ledger()
    for row in ledger_rows[-20:]:
        st.markdown(f"""
        <div style="background:#111; border-radius:10px; padding:10px; margin-bottom:10px; box-shadow:0 8px 20px rgba(0,0,0,0.6); color:#eee;">
            <h4 style="text-align:center; color:#e50914;">Block {row['index']}</h4>
            <p><b>Timestamp:</b> {row['timestamp']}</p>
            <p><b>UID:</b> {row['uid']}</p>
            <p><b>Name:</b> {row['first_name']} {row['last_name']}</p>
            <p><b>Action:</b> {row['action']}</p>
            <p style="color:gray"><b>Prev Hash:</b> {row['previous_hash']}</p>
            <p style="color:#e50914"><b>Hash:</b> {row['hash']}</p>
        </div>
        """, unsafe_allow_html=True)
