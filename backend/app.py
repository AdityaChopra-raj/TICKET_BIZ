# app.py
import streamlit as st
from pathlib import Path
from PIL import Image
from ledger import add_transaction, update_checkin, get_ledger
from events_data import EVENTS

st.set_page_config(page_title="🎟 Ticket_Biz — Event Ticketing", layout="wide")

# Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# CSS
st.markdown(
    f'<link rel="stylesheet" href="styles.css">', unsafe_allow_html=True
)

# --- Helper Functions ---
def get_resized_image(img_path, width=320, height=180):
    img = Image.open(img_path)
    return img.resize((width, height))

def show_event_card(event, idx):
    img_path = ASSETS_DIR / event["image"]
    img = get_resized_image(img_path)
    st.image(img, use_column_width=False)

    # Event info
    st.markdown(f"<b>{event['name']}</b>", unsafe_allow_html=True)
    st.markdown(event["description"])
    tickets_left = event["total_tickets"] - sum(
        [r["tickets"] for r in get_ledger() if r["event"] == event["name"]]
    )
    st.markdown(f"**Available Tickets:** {tickets_left}")

    # Buy Ticket Button
    buy_key = f"buy_btn_{idx}"
    if st.button("Buy Ticket", key=buy_key):
        st.session_state["selected_event"] = event["name"]
        st.session_state["action"] = "buy"

    # Check In Button
    check_key = f"check_btn_{idx}"
    if st.button("Check In", key=check_key):
        st.session_state["selected_event"] = event["name"]
        st.session_state["action"] = "checkin"

# Initialize session state
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None
if "action" not in st.session_state:
    st.session_state["action"] = None

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Buy Ticket", "Check In", "Blockchain"])

# --- Home Tab ---
with tab1:
    st.markdown("<h1 style='text-align:center;color:#e50914;font-size:48px;'>🎟 Ticket_Biz — Event Ticketing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:white;font-size:20px;'>Welcome to Ticket_Biz! Buy tickets, check in at events, and view blockchain records securely.</p>", unsafe_allow_html=True)

# --- Buy Ticket Tab ---
with tab2:
    st.markdown("<h2 style='color:white;'>Select Event</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, event in enumerate(EVENTS):
        with cols[idx % 3]:
            show_event_card(event, idx)

    if st.session_state["action"] == "buy" and st.session_state["selected_event"]:
        st.markdown(f"<h3>Buy Tickets for {st.session_state['selected_event']}</h3>", unsafe_allow_html=True)
        with st.form(key="buy_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            uid = st.text_input("Student ID / UID")
            email = st.text_input("Email Address")
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, step=1)
            submit_buy = st.form_submit_button("Confirm Purchase")
            if submit_buy:
                add_transaction(st.session_state["selected_event"], first_name, last_name, uid, num_tickets)
                st.success(f"Successfully purchased {num_tickets} tickets for {st.session_state['selected_event']}!")

# --- Check In Tab ---
with tab3:
    st.markdown("<h2 style='color:white;'>Check In</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    unique_uids = list(set([r["uid"] for r in ledger]))
    selected_uid = st.selectbox("Select Ticket UID", unique_uids)
    num_people = st.number_input("Number of People Checking In", min_value=1, max_value=15, step=1)
    if st.button("Confirm Check-In"):
        updated = update_checkin(selected_uid, num_people)
        if updated:
            st.success(f"Successfully checked in {num_people} people for UID {selected_uid}!")
        else:
            st.error("UID not found in ledger.")

# --- Blockchain Tab ---
with tab4:
    st.markdown("<h2 style='color:white;'>Blockchain Ledger Records</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    for record in ledger:
        st.markdown(f"""
        <div class='ledger-card'>
            <b>Event:</b> {record['event']}<br>
            <b>Name:</b> {record['first_name']} {record['last_name']}<br>
            <b>UID:</b> {record['uid']}<br>
            <b>Tickets:</b> {record['tickets']}<br>
            <b>Check-ins:</b> {record['checkins']}<br>
            <b>Hash:</b> {record['hash']}<br>
        </div>
        """, unsafe_allow_html=True)
