import streamlit as st
from pathlib import Path
from PIL import Image
from ledger import add_transaction, get_ledger, check_in_ticket
from events_data import EVENTS
from email_utils import send_email

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# -----------------------------
# Streamlit Page Setup
# -----------------------------
st.set_page_config(page_title="🎟 Ticket_Biz", page_icon="🎫", layout="wide")
st.markdown(
    """
    <style>
    body {background: linear-gradient(#0b0c10, #111418); font-family: 'Inter', sans-serif;}
    .event-card {background-color:#111418; border-radius:12px; padding:10px; margin:15px; width:320px; display:inline-block; vertical-align:top; transition:0.3s; color:white;}
    .event-card:hover {box-shadow:0 0 20px #e50914; transform:translateY(-5px);}
    .event-img {width:100%; height:180px; object-fit:cover; border-radius:12px 12px 0 0;}
    .btn-red {background-color:#e50914;color:white;font-weight:bold;border:none;border-radius:8px;padding:12px;width:100%;margin-top:10px;}
    .btn-red:hover {background-color:#ff1a1a;cursor:pointer;}
    .available-tag {background-color:#16a34a;color:white;padding:2px 6px;border-radius:4px;font-size:12px;display:inline-block;margin-bottom:5px;}
    .ribbon {display:flex;justify-content:center;gap:30px;margin-bottom:30px;}
    </style>
    """, unsafe_allow_html=True
)

# -----------------------------
# Tabs
# -----------------------------
tab = st.tabs(["Home", "Buy Ticket", "Check-In", "Blockchain"])
home_tab, buy_tab, checkin_tab, blockchain_tab = tab

# -----------------------------
# Home Tab
# -----------------------------
with home_tab:
    st.markdown('<h1 style="color:#e50914;font-size:48px;text-align:center;">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#ddd;font-size:20px;">Welcome to Ticket_Biz! Buy tickets and check-in seamlessly while blockchain secures your transactions.</p>', unsafe_allow_html=True)

# -----------------------------
# Helper: Resize Image
# -----------------------------
def get_resized_image(img_path):
    img = Image.open(img_path)
    img = img.resize((320, 180), Image.LANCZOS)
    return img

# -----------------------------
# Helper: Show Event Card
# -----------------------------
def show_event_card(event, tab_name, idx):
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        img_path = ASSETS_DIR / event["image"]
        img = get_resized_image(img_path)
        st.image(img, use_container_width=True)
        st.markdown(f'<div class="available-tag">AVAILABLE</div>', unsafe_allow_html=True)
        st.markdown(f"<b>{event['name']}</b>", unsafe_allow_html=True)
        st.markdown(f"<p>{event['description']}</p>", unsafe_allow_html=True)
        st.markdown(f"📅 {event['date']}<br>📍 {event['venue']}<br>🎟️ {event['total_tickets']} tickets<br>💰 ₹{event['price']}", unsafe_allow_html=True)
        if tab_name == "buy":
            if st.button("Buy Ticket", key=f"buy_btn_{idx}"):
                st.session_state["selected_buy_event"] = idx
        elif tab_name == "checkin":
            if st.button("Check-In", key=f"checkin_btn_{idx}"):
                st.session_state["selected_checkin_event"] = idx

# -----------------------------
# Buy Ticket Tab
# -----------------------------
with buy_tab:
    st.subheader("Available Events to Buy Tickets")
    for idx, event in enumerate(EVENTS):
        show_event_card(event, "buy", idx)

    if "selected_buy_event" in st.session_state:
        idx = st.session_state["selected_buy_event"]
        event = EVENTS[idx]
        st.markdown(f"### Buy Tickets for {event['name']}")
        with st.form("buy_ticket_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            student_id = st.text_input("Student ID")
            email = st.text_input("Email")
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, value=1)
            submitted = st.form_submit_button("Confirm Purchase")
            if submitted:
                if first_name and last_name and student_id and email:
                    uid = add_transaction(event["name"], first_name, last_name, student_id, num_tickets, email)
                    st.success(f"Tickets purchased successfully! Your Ticket UID is {uid}")
                    send_email(email, f"Tickets for {event['name']}", f"Hello {first_name},<br>You purchased {num_tickets} ticket(s) for {event['name']}.<br>UID: {uid}")
                else:
                    st.error("Please fill all fields to purchase tickets.")

# -----------------------------
# Check-In Tab
# -----------------------------
with checkin_tab:
    st.subheader("Check-In for Events")
    for idx, event in enumerate(EVENTS):
        show_event_card(event, "checkin", idx)

    if "selected_checkin_event" in st.session_state:
        idx = st.session_state["selected_checkin_event"]
        event = EVENTS[idx]
        st.markdown(f"### Check-In for {event['name']}")
        uid = st.text_input("Enter Ticket UID")
        email = st.text_input("Enter Email")
        num_people = st.number_input("Number of People Checking In", min_value=1, max_value=15, value=1)
        if st.button("Confirm Check-In"):
            success, message = check_in_ticket(uid, email, num_people)
            if success:
                st.success(message)
            else:
                st.error(message)

# -----------------------------
# Blockchain Ledger Tab
# -----------------------------
with blockchain_tab:
    st.subheader("Blockchain Ledger Records")
    ledger = get_ledger()
    for record in ledger:
        st.markdown(
            f"<div style='background:#111418;padding:10px;margin:5px;border-radius:12px;'>"
            f"<b>Event:</b> {record['event']}<br>"
            f"<b>Name:</b> {record['first_name']} {record['last_name']}<br>"
            f"<b>Student ID:</b> {record['student_id']}<br>"
            f"<b>Email:</b> {record['email']}<br>"
            f"<b>Tickets:</b> {record['num_tickets']}<br>"
            f"<b>Checked In:</b> {record['checked_in']}<br>"
            f"<b>Ticket UID:</b> {record['uid']}</div>", unsafe_allow_html=True
        )
