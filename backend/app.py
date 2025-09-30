import streamlit as st
from PIL import Image
from pathlib import Path
from ledger import add_transaction, get_ledger, get_tickets_sold
from events_data import EVENTS
from email_utils import send_email

ASSETS_DIR = Path(__file__).parent / "assets"
MAX_TICKETS_PER_PURCHASE = 15

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# --- CSS ---
with open(Path(__file__).parent / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["Home", "Buy Ticket", "Check-In", "Blockchain"])
home_tab, buy_tab, checkin_tab, blockchain_tab = tabs

# --- Home Tab ---
with home_tab:
    st.markdown("<h1 style='color:#e50914;font-size:48px;'>🎟 Ticket_Biz — Event Ticketing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb;font-size:18px;'>Welcome to Ticket_Biz! Purchase your tickets and check in easily using our blockchain-powered platform.</p>", unsafe_allow_html=True)

# --- Utility Functions ---
def get_resized_image(img_path, width=320, height=180):
    img = Image.open(img_path)
    return img.resize((width, height))

def show_event_card(event, tab_name, idx):
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    col = cols[idx % 3]
    with col:
        img_path = ASSETS_DIR / event["image"]
        if not img_path.exists():
            img_path = ASSETS_DIR / "placeholder.jpg"
        img = get_resized_image(img_path)
        st.image(img, use_container_width=True)

        # AVAILABLE / FULL
        tickets_left = max(event["total_tickets"] - get_tickets_sold(event["id"]), 0)
        status = "AVAILABLE" if tickets_left > 0 else "FULL"
        color = "#16a34a" if tickets_left > 0 else "#ff0000"
        st.markdown(f"<p style='background:{color};color:white;padding:4px 8px;border-radius:4px;width:fit-content'>{status}</p>", unsafe_allow_html=True)

        # Event info
        st.markdown(f"<h3 style='color:white'>{event['name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#bbb'>{event['description']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#ccc'>📅 {event['date']}<br>📍 {event['venue']}<br>🎟️ {tickets_left}/{event['total_tickets']} tickets left<br>💰 From ₹{event['price']}</p>", unsafe_allow_html=True)

        # Action button
        button_key = f"{tab_name}_btn_{event['id']}"
        if st.button(f"{tab_name.replace('_',' ').title()}", key=button_key):
            st.session_state["selected_event"] = event["id"]
            st.session_state["tab_action"] = tab_name

# --- Buy Ticket Tab ---
with buy_tab:
    for idx, event in enumerate(EVENTS):
        show_event_card(event, "buy", idx)
    selected = st.session_state.get("selected_event", None)
    if selected:
        event = next((e for e in EVENTS if e["id"]==selected), None)
        if event:
            st.subheader(f"Buy Tickets for {event['name']}")
            with st.form(f"buy_form_{event['id']}"):
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                uid = st.text_input("Student ID")
                email = st.text_input("Email")
                max_buy = min(MAX_TICKETS_PER_PURCHASE, event["total_tickets"] - get_tickets_sold(event["id"]))
                num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=max_buy, value=1)
                submitted = st.form_submit_button("Confirm Purchase")
                if submitted:
                    if first_name and last_name and uid and email:
                        add_transaction(event["id"], event["name"], first_name, last_name, uid, num_tickets)
                        st.success(f"{num_tickets} ticket(s) purchased successfully!")
                        # send_email(email, subject="Ticket_Biz Purchase", body=f"You bought {num_tickets} ticket(s) for {event['name']}")
                    else:
                        st.error("Please fill in all fields.")

# --- Check-In Tab ---
with checkin_tab:
    for idx, event in enumerate(EVENTS):
        show_event_card(event, "checkin", idx)
    selected = st.session_state.get("selected_event", None)
    if selected:
        event = next((e for e in EVENTS if e["id"]==selected), None)
        if event:
            st.subheader(f"Check-In for {event['name']}")
            with st.form(f"checkin_form_{event['id']}"):
                uid = st.text_input("Ticket UID")
                email = st.text_input("Email")
                num_checkin = st.number_input("Number of People Checking In", min_value=1, max_value=15, value=1)
                submitted = st.form_submit_button("Confirm Check-In")
                if submitted:
                    if uid and email:
                        st.success(f"{num_checkin} attendee(s) checked in for UID {uid}!")
                    else:
                        st.error("Please fill in UID and Email.")

# --- Blockchain Tab ---
with blockchain_tab:
    st.subheader("Blockchain Ledger Records")
    ledger = get_ledger()
    for record in ledger:
        st.markdown(
            f"<div style='border:1px solid #444;padding:10px;margin-bottom:8px;border-radius:8px;background:#111418'>"
            f"<b>Event:</b> {record.get('event_name')}<br>"
            f"<b>Name:</b> {record.get('first_name')} {record.get('last_name')}<br>"
            f"<b>UID:</b> {record.get('uid')}<br>"
            f"<b>Tickets:</b> {record.get('num_tickets')}<br>"
            f"</div>",
            unsafe_allow_html=True
        )
