import streamlit as st
from PIL import Image
import os, uuid, csv, smtplib
from email.message import EmailMessage
from datetime import datetime
from events_data import EVENTS
from ledger import add_block, read_ledger, init_ledger
from pathlib import Path

st.set_page_config(page_title="TicketBiz Clone", layout="wide")
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
TICKETS_CSV = BASE_DIR / "tickets.csv"

init_ledger()

# CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass
local_css(BASE_DIR / "styles/style.css")

# Helpers
def generate_uid():
    return uuid.uuid4().hex[:10].upper()

def send_ticket_email(to_email, first_name, last_name, uid, event_name):
    try:
        email_conf = st.secrets.get("email", None)
        if not email_conf:
            raise RuntimeError("Email credentials not configured in st.secrets")
        msg = EmailMessage()
        msg["Subject"] = f"Your ticket for {event_name}"
        msg["From"] = email_conf["address"]
        msg["To"] = to_email
        msg.set_content(f"Hi {first_name} {last_name},\n\nUID: {uid}\nEvent: {event_name}\n\nShow this at check-in.\n\n— TicketBiz Clone")
        s = smtplib.SMTP_SSL(email_conf.get("smtp_host","smtp.gmail.com"), int(email_conf.get("smtp_port",465)))
        s.login(email_conf["address"], email_conf["password"])
        s.send_message(msg)
        s.quit()
        return True, None
    except Exception as e:
        return False, str(e)

def save_ticket_record(uid, first, last, email, event_name):
    header = ["uid","first_name","last_name","email","event","purchased_at","checked_in"]
    exists = TICKETS_CSV.exists()
    with open(TICKETS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerow([uid, first, last, email, event_name, datetime.utcnow().isoformat(), ""])
    return

def mark_checked_in(uid):
    rows = []
    if not TICKETS_CSV.exists():
        return False
    with open(TICKETS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["uid"] == uid:
                r["checked_in"] = datetime.utcnow().isoformat()
            rows.append(r)
    with open(TICKETS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["uid","first_name","last_name","email","event","purchased_at","checked_in"])
        writer.writeheader()
        writer.writerows(rows)
    return True

# Session state
if "buy_event" not in st.session_state:
    st.session_state["buy_event"] = None
if "show_checkin" not in st.session_state:
    st.session_state["show_checkin"] = False
if "show_ledger" not in st.session_state:
    st.session_state["show_ledger"] = False

# --- Main Title & Subtitle ---
st.markdown('<h1 style="text-align:center; color:white;">🎟 TicketBiz — Seamless Event Ticketing</h1>', unsafe_allow_html=True)
st.markdown('''
<p style="text-align:center; color:#ccc; font-size:18px;">
Welcome to <b>TicketBiz</b>, your all-in-one platform to browse events, buy tickets securely, and manage check-ins effortlessly.  
Experience a modern, blockchain-backed ticketing system with email confirmations and a real-time ledger to track your tickets.
</p>
''', unsafe_allow_html=True)

# --- Events Section ---
st.markdown('<h2 style="text-align:center; color:#e50914;">🎬 Featured Events</h2>', unsafe_allow_html=True)
st.markdown('''
<p style="text-align:center; color:#ccc; font-size:16px;">
Discover our curated selection of exciting events. Scroll horizontally to explore upcoming shows, festivals, and parties.  
Click <b>Buy</b> on an event to reserve your ticket instantly.
</p>
''', unsafe_allow_html=True)

st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)

st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)

for ev in EVENTS:
    img_path = ASSETS_DIR / ev.get("image", "placeholder.jpeg")
    try:
        img = Image.open(img_path)
    except:
        img = Image.open(ASSETS_DIR / "placeholder.jpeg")
    
    st.markdown(f'''
    <div class="card">
        <img src="{img_path}" alt="{ev['name']}">
        <h3>{ev["name"]}</h3>
        <p>{ev.get("desc","")}</p>
        <p class="price">Price: ₹{ev.get("price",100)}</p>
        <button onclick="alert('Buying ticket for {ev["name"]}')">Buy</button>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True)

# --- Buy Ticket Form ---
if st.session_state["buy_event"]:
    ev_name = st.session_state["buy_event"]
    st.markdown("---")
    st.markdown(f'<h2 style="text-align:center; color:#e50914;">💳 Purchase Ticket — {ev_name}</h2>', unsafe_allow_html=True)
    st.markdown('''
    <p style="text-align:center; color:#ccc; font-size:16px;">
    Fill in your details below to purchase your ticket. Payments are simulated for demo purposes, but your ticket UID and email confirmation are live.  
    Once purchased, your ticket will be recorded on our secure blockchain ledger.
    </p>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        first = st.text_input("First Name", key="first")
        last = st.text_input("Last Name", key="last")
        email = st.text_input("Email", key="email")
    with col2:
        st.write("Payment simulated for demo.")
        name_on_card = st.text_input("Name on card (demo)", key="cardname")
        if st.button("Confirm Purchase"):
            if not (first and last and email):
                st.error("Enter first name, last name, and email")
            else:
                uid = generate_uid()
                save_ticket_record(uid, first, last, email, ev_name)
                add_block(uid, first, last, "buy")
                ok, err = send_ticket_email(email, first, last, uid, ev_name)
                if ok: st.success(f"Ticket purchased! UID: {uid}. Email sent to {email}")
                else: st.warning(f"Ticket purchased (email failed): {err}")
                st.session_state["show_checkin"] = True
                st.session_state["show_ledger"] = True

# --- Check-in Section ---
if st.session_state["show_checkin"]:
    st.markdown("---")
    st.markdown('<h2 style="text-align:center; color:#e50914;">✅ Ticket Check-In</h2>', unsafe_allow_html=True)
    st.markdown('''
    <p style="text-align:center; color:#ccc; font-size:16px;">
    Verify your ticket by entering the <b>UID</b> provided in your purchase confirmation email.  
    Our blockchain ledger ensures that each ticket is secure and tamper-proof.  
    Check-in status will be updated in real-time and confirmation emails will be sent automatically.
    </p>
    ''', unsafe_allow_html=True)

    uid_input = st.text_input("Enter ticket UID", key="check_uid")
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
                                add_block(uid_input, r["first_name"], r["last_name"], "check-in")
                                ok, err = send_ticket_email(r["email"], r["first_name"], r["last_name"], uid_input, r["event"])
                                if ok: st.success("Check-in successful, confirmation email sent.")
                                else: st.success("Check-in successful, email failed")
                            break
            if not found:
                st.error("Ticket UID not found.")

# --- Blockchain Ledger ---
if st.session_state["show_ledger"]:
    st.markdown("---")
    st.markdown('<h2 style="text-align:center; color:#e50914;">🔗 Blockchain Ledger</h2>', unsafe_allow_html=True)
    st.markdown('''
    <p style="text-align:center; color:#ccc; font-size:16px;">
    All ticket purchases and check-ins are recorded on a transparent blockchain ledger.  
    Each block contains UID, purchaser name, action, timestamp, and hash values.  
    This ensures your ticket history is secure, immutable, and verifiable.
    </p>
    ''', unsafe_allow_html=True)

    ledger_rows = read_ledger()
    if not ledger_rows:
        st.info("Ledger empty")
    else:
        for row in ledger_rows[-20:]:
            block_html = f"""
            <div style="
                background: linear-gradient(180deg, #111 0%, #151515 100%);
                border-radius:10px;
                padding:10px;
                margin-bottom:10px;
                box-shadow:0 8px 20px rgba(0,0,0,0.6);
                color:#eee;
            ">
            <h4 style="text-align:center; color:#e50914;">Block {row['index']}</h4>
            <p><b>Timestamp:</b> {row['timestamp']}</p>
            <p><b>UID:</b> {row['uid']}</p>
            <p><b>Name:</b> {row['first_name']} {row['last_name']}</p>
            <p><b>Action:</b> {row['action']}</p>
            <p style="color:gray"><b>Prev Hash:</b> {row['previous_hash']}</p>
            <p style="color:#e50914"><b>Hash:</b> {row['hash']}</p>
            </div>
            """
            st.markdown(block_html, unsafe_allow_html=True)

    if st.button("Download ledger CSV"):
        with open("ledger.csv","rb") as f:
            st.download_button("Download ledger.csv", f, file_name="ledger.csv")

# --- Footer ---
st.markdown('''
<p style="text-align:center; color:#666; font-size:12px;">
© 2025 TicketBiz. Designed with ❤️ using Streamlit.  
For support or inquiries, contact <b>support@ticketbiz.com</b>.
</p>
''', unsafe_allow_html=True)
