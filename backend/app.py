import streamlit as st
from pathlib import Path
from PIL import Image
from ledger import add_transaction, get_ledger, update_check_in, get_tickets_sold, get_checked_in
from events_data import EVENTS
import uuid

# Directories
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# App Config
st.set_page_config(page_title="🎟 Ticket_Biz — Event Ticketing", layout="wide")

# Helper: Resize image to uniform size
def get_resized_image(img_path, width=320, height=180):
    img = Image.open(img_path)
    return img.resize((width, height), Image.LANCZOS)

# Helper: Display event card
def show_event_card(event, tab_name="home", idx=0):
    col1, col2, col3 = st.columns(3)
    col = [col1, col2, col3][idx % 3]

    with col:
        # Image
        img_path = ASSETS_DIR / event["image"]
        img = get_resized_image(img_path)
        st.image(img, use_container_width=True)

        # Availability
        tickets_left = event["total_tickets"] - get_tickets_sold(event["id"])
        checked_in = get_checked_in(event["id"])
        avail_text = f"AVAILABLE ({tickets_left} left)" if tickets_left > 0 else "FULL"
        avail_color = "green" if tickets_left > 0 else "red"
        st.markdown(f"<p style='color:{avail_color}; font-weight:bold; text-align:center'>{avail_text}</p>", unsafe_allow_html=True)

        # Title & description
        st.markdown(f"<h4 style='margin:5px 0'>{event['name']}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#bbb; font-size:14px'>{event['description']}</p>", unsafe_allow_html=True)

        # Details
        st.markdown(f"<p>📅 {event['date']}<br>📍 {event['venue']}<br>🎟️ Tickets sold: {get_tickets_sold(event['id'])}/{event['total_tickets']}<br>💰 From ₹{event['price']}</p>", unsafe_allow_html=True)

        # Buttons per tab
        if tab_name == "buy":
            buy_key = f"buy_btn_{event['id']}_{idx}"
            if tickets_left > 0 and st.button("Buy Ticket", key=buy_key):
                st.session_state["current_event"] = event
                st.session_state["flow"] = "buy"
        elif tab_name == "checkin":
            check_key = f"checkin_btn_{event['id']}_{idx}"
            if st.button("Check In", key=check_key):
                st.session_state["current_event"] = event
                st.session_state["flow"] = "checkin"

# Initialize session state
if "flow" not in st.session_state:
    st.session_state["flow"] = "home"
if "current_event" not in st.session_state:
    st.session_state["current_event"] = None

# Tabs
tab_home, tab_buy, tab_checkin, tab_blockchain = st.tabs(["Home", "Buy Ticket", "Check In", "Blockchain"])

# --- Home Tab ---
with tab_home:
    st.markdown("<h1 style='color:#e50914; text-align:center; font-size:48px'>🎟 Ticket_Biz — Event Ticketing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ddd; font-size:18px'>Welcome to Ticket_Biz! Buy tickets and check in securely with our blockchain-powered ledger.</p>", unsafe_allow_html=True)

# --- Buy Ticket Tab ---
with tab_buy:
    st.markdown("<h2 style='color:white; text-align:center'>Trending Events</h2>", unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="buy", idx=idx)

    # If user clicked Buy on a specific event
    if st.session_state.get("flow") == "buy" and st.session_state.get("current_event"):
        event = st.session_state["current_event"]
        st.subheader(f"Buy Tickets for {event['name']}")
        with st.form(key=f"buy_form_{event['id']}"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            student_id = st.text_input("Student ID")
            email = st.text_input("Email")
            tickets_left = event["total_tickets"] - get_tickets_sold(event["id"])
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=min(15, tickets_left), step=1)
            submit = st.form_submit_button("Confirm Purchase")
            if submit:
                if first_name and last_name and student_id and email and num_tickets > 0:
                    uid = str(uuid.uuid4())[:8]
                    add_transaction(event["id"], event["name"], first_name, last_name, student_id, email, num_tickets, uid, price=event["price"])
                    st.success(f"Purchase Confirmed! Your UID: {uid}")
                else:
                    st.error("Please fill in all fields and select number of tickets.")

# --- Check In Tab ---
with tab_checkin:
    st.markdown("<h2 style='color:white; text-align:center'>Check In</h2>", unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="checkin", idx=idx)

    if st.session_state.get("flow") == "checkin" and st.session_state.get("current_event"):
        event = st.session_state["current_event"]
        st.subheader(f"Check In for {event['name']}")
        with st.form(key=f"checkin_form_{event['id']}"):
            uid = st.text_input("Enter Ticket UID")
            tickets_left = event["total_tickets"] - get_tickets_sold(event["id"])
            max_checkin = min(15, get_tickets_sold(event["id"]))
            num_checkin = st.number_input("Number of People Checking In", min_value=1, max_value=max_checkin, step=1)
            submit = st.form_submit_button("Confirm Check In")
            if submit:
                if uid:
                    success = update_check_in(uid, num_checkin)
                    if success:
                        st.success(f"Checked in {num_checkin} person(s) successfully!")
                    else:
                        st.error("Invalid UID. Check your ticket UID.")
                else:
                    st.error("Please enter a valid UID.")

# --- Blockchain Tab ---
with tab_blockchain:
    st.markdown("<h2 style='color:white; text-align:center'>Blockchain Ledger</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    if ledger:
        for record in ledger:
            st.markdown(
                f"<div style='background:#111418; padding:10px; margin:5px 0; border-radius:8px'>"
                f"<b>Event:</b> {record['event_name']}<br>"
                f"<b>Name:</b> {record['first_name']} {record['last_name']}<br>"
                f"<b>Student ID:</b> {record['student_id']}<br>"
                f"<b>Email:</b> {record['email']}<br>"
                f"<b>Tickets Bought:</b> {record['num_tickets']}<br>"
                f"<b>Checked In:</b> {record['num_checked_in']}<br>"
                f"<b>UID:</b> {record['uid']}<br>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No transactions yet.")
