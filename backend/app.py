import streamlit as st
from pathlib import Path
from PIL import Image
from ledger import add_transaction, get_ledger
from events_data import EVENTS
from email_utils import send_email

# Assets directory
ASSETS_DIR = Path("assets")

# --- Helper Functions ---
def get_resized_image(img_path, width=320, height=180):
    """Resizes images to uniform dimensions."""
    img = Image.open(img_path)
    img = img.resize((width, height), Image.LANCZOS)
    return img

def show_event_card(event, tab_name, idx):
    """
    Displays a single event card with Buy/Check-In forms.
    `tab_name` ensures unique keys for Streamlit widgets.
    """
    st.markdown('<div class="event-card">', unsafe_allow_html=True)
    
    # Image
    img = get_resized_image(ASSETS_DIR / event["image"])
    st.image(img, use_container_width=True)

    # Availability
    availability = "AVAILABLE" if event["available_tickets"] > 0 else "FULL"
    color = "#16a34a" if event["available_tickets"] > 0 else "#ff0000"
    st.markdown(f'''
        <div class="availability-badge" style="background-color:{color};">{availability}</div>
    ''', unsafe_allow_html=True)

    # Title & Description
    st.markdown(f'<div class="event-title">{event["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="event-description">{event["description"]}</div>', unsafe_allow_html=True)

    # Details
    st.markdown(f'''
        <div class="event-details">
            📅 {event["date"]} <br>
            📍 {event["location"]} <br>
            🎟️ {event["available_tickets"]} tickets left <br>
            💰 From ₹{event["price"]}
        </div>
    ''', unsafe_allow_html=True)

    # Buttons under card
    st.markdown('<div class="card-buttons">', unsafe_allow_html=True)
    buy_key = f"{tab_name}_buy_{event['id']}_{idx}"
    if st.button("Buy Ticket", key=buy_key):
        st.session_state.selected_event = event["id"]
        st.session_state.mode = "buy"
        st.experimental_rerun()

    checkin_key = f"{tab_name}_checkin_{event['id']}_{idx}"
    if st.button("Check-In", key=checkin_key):
        st.session_state.selected_event = event["id"]
        st.session_state.mode = "checkin"
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Buy Ticket Form
    if st.session_state.get("mode") == "buy" and st.session_state.get("selected_event") == event["id"]:
        st.markdown('<div class="buy-checkin-form">', unsafe_allow_html=True)
        first_name = st.text_input("First Name", key=f"{tab_name}_first_{event['id']}_{idx}")
        last_name = st.text_input("Last Name", key=f"{tab_name}_last_{event['id']}_{idx}")
        uid = st.text_input("Student ID / UID", key=f"{tab_name}_uid_{event['id']}_{idx}")
        email = st.text_input("Email", key=f"{tab_name}_email_{event['id']}_{idx}")
        num_tickets = st.number_input(
            "Number of Tickets",
            min_value=1,
            max_value=min(15, event["available_tickets"]),
            value=1,
            key=f"{tab_name}_num_{event['id']}_{idx}"
        )
        confirm_key = f"{tab_name}_confirm_buy_{event['id']}_{idx}"
        if st.button("Confirm Purchase", key=confirm_key):
            if not all([first_name, last_name, uid, email]):
                st.warning("Please fill all details.")
            else:
                add_transaction(event["name"], first_name, last_name, uid, num_tickets, email)
                event["available_tickets"] -= num_tickets
                send_email(email, f"Tickets for {event['name']}", f"You have successfully booked {num_tickets} tickets!")
                st.success(f"Tickets purchased successfully! {event['available_tickets']} tickets remaining.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Check-In Form
    if st.session_state.get("mode") == "checkin" and st.session_state.get("selected_event") == event["id"]:
        st.markdown('<div class="buy-checkin-form">', unsafe_allow_html=True)
        check_uid = st.text_input("Enter Ticket UID", key=f"{tab_name}_checkin_uid_{event['id']}_{idx}")
        email = st.text_input("Enter Email", key=f"{tab_name}_checkin_email_{event['id']}_{idx}")
        num_checkin = st.number_input("Number of People Checking In", min_value=1, max_value=15, value=1, key=f"{tab_name}_checkin_num_{event['id']}_{idx}")
        confirm_checkin_key = f"{tab_name}_confirm_checkin_{event['id']}_{idx}"
        if st.button("Confirm Check-In", key=confirm_checkin_key):
            ledger_records = get_ledger()
            for record in ledger_records:
                if record["uid"] == check_uid and record["email"] == email and record["event"] == event["name"]:
                    if num_checkin <= record["tickets"]:
                        st.success(f"Check-In confirmed for {num_checkin} people for {record['first_name']} {record['last_name']}!")
                        event["check_ins"] += num_checkin
                        event["available_tickets"] -= num_checkin
                    else:
                        st.warning(f"Cannot check in {num_checkin} people. Only {record['tickets']} tickets were purchased.")
                    break
            else:
                st.warning("No matching ticket found!")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["Home", "Buy Ticket", "Check-In", "Blockchain"])
tab_home, tab_buy, tab_checkin, tab_blockchain = tabs

with tab_home:
    st.markdown('<h1>🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
    st.markdown('<p>Welcome to Ticket_Biz! Book tickets and check in securely via blockchain ledger.</p>', unsafe_allow_html=True)

with tab_buy:
    st.markdown('<h2>Trending Events</h2>', unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="buy", idx=idx)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_checkin:
    st.markdown('<h2>Check-In Events</h2>', unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="checkin", idx=idx)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_blockchain:
    st.markdown('<h2>Blockchain Ledger</h2>', unsafe_allow_html=True)
    ledger_records = get_ledger()
    for idx, record in enumerate(ledger_records):
        st.markdown(f'''
            <div class="event-card" style="padding:10px;">
                <b>Event:</b> {record['event']}<br>
                <b>Name:</b> {record['first_name']} {record['last_name']}<br>
                <b>UID:</b> {record['uid']}<br>
                <b>Email:</b> {record['email']}<br>
                <b>Tickets:</b> {record['tickets']}<br>
                <b>Check-Ins:</b> {record.get('check_ins', 0)}<br>
                <b>Hash:</b> {record['hash']}
            </div>
        ''', unsafe_allow_html=True)
