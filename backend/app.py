# app.py
import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS
from ledger import add_transaction, get_ledger

# --- Directories ---
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# --- Page Config ---
st.set_page_config(page_title="Ticket_Biz", page_icon="🎟️", layout="wide")
st.markdown("<h1 style='text-align:center; font-size:48px; color:#e50914;'>🎟 Ticket_Biz — Event Ticketing</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color:#ddd;'>Welcome! Buy tickets and check in for your favorite events. Powered by blockchain ledger.</p>", unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["Home", "Buy Ticket", "Check In", "Blockchain"])
tab_home, tab_buy, tab_checkin, tab_blockchain = tabs

# --- Helper Functions ---
def get_resized_image(img_path, width=320, height=180):
    try:
        img = Image.open(img_path)
        img = img.resize((width, height), Image.LANCZOS)
        return img
    except:
        return Image.open(ASSETS_DIR / "placeholder.jpg").resize((width, height), Image.LANCZOS)

def show_event_card(event, tab_name, idx):
    img_path = ASSETS_DIR / event["image"]
    img = get_resized_image(img_path)
    
    # Event Card container
    st.markdown(f"""
    <div class="event-card">
        <img src="{img_path}" alt="{event['name']}">
        <div class="available-tag">{'AVAILABLE' if event['tickets_left']>0 else 'FULL'}</div>
        <div class="card-content">
            <div class="card-title">{event['name']}</div>
            <div class="card-description">{event['description']}</div>
            <div class="card-details">
                <div>📅 {event['date_time']}</div>
                <div>📍 {event['venue']}</div>
                <div>🎟️ {event['tickets_left']}/{event['total_tickets']} tickets left</div>
                <div>💰 From ₹{event['price']}</div>
            </div>
    """, unsafe_allow_html=True)
    
    buy_key = f"buy_{tab_name}_{idx}"
    checkin_key = f"checkin_{tab_name}_{idx}"
    
    if tab_name == "buy" and event['tickets_left']>0:
        if st.button("Buy Ticket", key=buy_key):
            st.session_state["selected_event"] = event['id']
    if tab_name == "checkin" and event['tickets_left']>0:
        if st.button("Check In", key=checkin_key):
            st.session_state["selected_event_checkin"] = event['id']
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- Home Tab ---
with tab_home:
    st.markdown("<p style='text-align:center; font-size:16px; color:#bbb;'>Select a tab above to buy tickets, check in, or view blockchain records.</p>", unsafe_allow_html=True)

# --- Buy Ticket Tab ---
with tab_buy:
    st.markdown("<h2 style='text-align:center; color:white;'>Trending Events</h2>", unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="buy", idx=idx)
    st.markdown("</div>", unsafe_allow_html=True)

    # Buy Ticket Form
    if "selected_event" in st.session_state:
        event = next(e for e in EVENTS if e['id']==st.session_state["selected_event"])
        st.subheader(f"Buy Tickets for {event['name']}")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        uid = st.text_input("Student ID / UID")
        email = st.text_input("Email")
        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, value=1)
        if st.button("Confirm Purchase"):
            if first_name and last_name and uid and email:
                add_transaction(event['name'], first_name, last_name, uid, num_tickets)
                st.success("Tickets purchased successfully!")
                event['tickets_left'] -= num_tickets
            else:
                st.error("Please fill all required fields!")

# --- Check In Tab ---
with tab_checkin:
    st.markdown("<h2 style='text-align:center; color:white;'>Check In</h2>", unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="checkin", idx=idx)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Check-in Form
    if "selected_event_checkin" in st.session_state:
        event = next(e for e in EVENTS if e['id']==st.session_state["selected_event_checkin"])
        st.subheader(f"Check In for {event['name']}")
        uid = st.text_input("Ticket UID")
        email = st.text_input("Email")
        num_people = st.number_input("Number of People Checking In", min_value=1, max_value=15, value=1)
        if st.button("Confirm Check-in"):
            st.success(f"{num_people} people checked in successfully!")

# --- Blockchain Tab ---
with tab_blockchain:
    st.subheader("Blockchain Ledger")
    ledger = get_ledger()
    for record in ledger:
        st.markdown(f"""
        <div class="event-card" style="padding:15px; margin-bottom:10px;">
            <b>Event:</b> {record['event']}<br>
            <b>Name:</b> {record['first_name']} {record['last_name']}<br>
            <b>UID:</b> {record['uid']}<br>
            <b>Tickets Bought:</b> {record['tickets']}<br>
            <b>Hash:</b> {record['hash']}<br>
        </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<footer>
Ticket_Biz © 2025. Powered by Blockchain Technology.
</footer>
""", unsafe_allow_html=True)
