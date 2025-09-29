import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS, ASSETS_DIR
from ledger import add_transaction, get_ledger
from email_utils import send_email

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# Initialize session state
if "mode" not in st.session_state:
    st.session_state.mode = None
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# ------------------ Styles ------------------
with open(Path(__file__).parent / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ------------------ Header ------------------
st.markdown('<h1 style="text-align:center; color:#e50914; font-size:48px;">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#ddd; font-size:18px;">Welcome! Book tickets for events or check in attendees directly from this platform.</p>', unsafe_allow_html=True)

# ------------------ Triangular Buttons with Home ------------------
st.markdown('<h1 style="text-align:center; color:#e50914; font-size:48px;">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#ddd; font-size:18px;">Welcome! Book tickets for events or check in attendees directly from this platform.</p>', unsafe_allow_html=True)

# Top Row: Buy Ticket (left) and Check-In (right)
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Buy Ticket", key="btn_buy"):
        st.session_state.mode = "buy"
        st.session_state.selected_event = None
with col3:
    if st.button("Check-In", key="btn_checkin"):
        st.session_state.mode = "checkin"
        st.session_state.selected_event = None

st.write("\n")  # Spacer

# Middle Row: Home button centered
col_left, col_center, col_right = st.columns([1,2,1])
with col_center:
    if st.button("Home", key="btn_home"):
        st.session_state.mode = None
        st.session_state.selected_event = None

st.write("\n")  # Spacer

# Bottom Row: Blockchain Ledger button centered
col_left2, col_center2, col_right2 = st.columns([1,2,1])
with col_center2:
    if st.button("Blockchain Ledger", key="btn_blockchain"):
        st.session_state.mode = "ledger"
        st.session_state.selected_event = None


# Row 2: Blockchain Ledger button centered
col_left, col_center, col_right = st.columns([1,2,1])
with col_center:
    if st.button("Blockchain Ledger", key="btn_blockchain"):
        st.session_state.mode = "ledger"
        st.session_state.selected_event = None

# ------------------ Helper: Resize Image ------------------
def get_resized_image(img_name):
    img_path = ASSETS_DIR / img_name
    placeholder_path = ASSETS_DIR / "placeholder.jpg"
    if not img_path.exists():
        img_path = placeholder_path
    img = Image.open(img_path)
    img = img.resize((320, 180), Image.LANCZOS)
    return img

# ------------------ Display Event Grid ------------------
if st.session_state.mode in ["buy", "checkin"] and st.session_state.selected_event is None:
    st.markdown('<h2 class="section-title">Trending Events</h2>', unsafe_allow_html=True)
    rows = len(EVENTS) // 3 + (1 if len(EVENTS) % 3 else 0)
    for r in range(rows):
        cols = st.columns(3, gap="large")
        for c in range(3):
            idx = r*3 + c
            if idx >= len(EVENTS):
                continue
            event = EVENTS[idx]
            col = cols[c]
            with col:
                img = get_resized_image(event["image"])
                st.image(img, use_container_width=True)
                availability = "AVAILABLE" if event["available_tickets"] > 0 else "FULL"
                avail_color = "#16a34a" if event["available_tickets"] > 0 else "#ff0000"
                st.markdown(f'<div class="availability-tag" style="background-color:{avail_color}">{availability}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{event["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-desc">{event["description"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-details">📅 {event["date"]}<br>📍 {event["location"]}<br>🎟️ {event["available_tickets"]} tickets left<br>💰 From ₹{event["price"]}</div>', unsafe_allow_html=True)
                if st.button("Select Event", key=f"select_{event['id']}"):
                    st.session_state.selected_event = event

# ------------------ Buy Tickets Section ------------------
if st.session_state.mode == "buy" and st.session_state.selected_event:
    event = st.session_state.selected_event
    st.markdown(f'<h2 class="section-title">Buy Tickets for {event["name"]}</h2>', unsafe_allow_html=True)
    first_name = st.text_input("First Name", key="buy_first")
    last_name = st.text_input("Last Name", key="buy_last")
    uid = st.text_input("Student ID / UID", key="buy_uid")
    email = st.text_input("Email", key="buy_email")
    num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, value=1, key="buy_count")
    
    if st.button("Confirm Purchase", key="buy_confirm"):
        if not all([first_name, last_name, uid, email]):
            st.warning("Please fill all details.")
        elif num_tickets > event["available_tickets"]:
            st.warning(f"Only {event['available_tickets']} tickets available.")
        else:
            add_transaction(event["name"], first_name, last_name, uid, num_tickets, email)
            event["available_tickets"] -= num_tickets
            send_email(email, f"Tickets for {event['name']}", f"You have successfully booked {num_tickets} tickets!")
            st.success(f"Tickets purchased successfully! {event['available_tickets']} tickets remaining.")

# ------------------ Check-In Section ------------------
if st.session_state.mode == "checkin" and st.session_state.selected_event:
    event = st.session_state.selected_event
    st.markdown(f'<h2 class="section-title">Check-In for {event["name"]}</h2>', unsafe_allow_html=True)
    check_uid = st.text_input("Enter Ticket UID", key="checkin_uid")
    email = st.text_input("Enter Email", key="checkin_email")
    num_checkin = st.number_input("Number of People Checking In", min_value=1, max_value=15, value=1, key="checkin_count")
    
    if st.button("Confirm Check-In", key="confirm_checkin"):
        ledger_records = get_ledger()
        for record in ledger_records:
            if record["uid"] == check_uid and record["email"] == email:
                if num_checkin <= record["tickets"]:
                    st.success(f"Check-In confirmed for {num_checkin} people for {record['first_name']} {record['last_name']}!")
                    event["check_ins"] += num_checkin
                    event["available_tickets"] -= num_checkin
                else:
                    st.warning(f"Cannot check in {num_checkin} people. Only {record['tickets']} tickets were purchased.")
                break
        else:
            st.warning("No matching ticket found!")

# ------------------ Blockchain Ledger ------------------
if st.session_state.mode == "ledger":
    st.markdown('<h2 class="section-title">Blockchain Ledger</h2>', unsafe_allow_html=True)
    ledger_records = get_ledger()
    for record in ledger_records:
        st.markdown(f"""
            <div class="ledger-card">
            <b>Event:</b> {record['event']}<br>
            <b>Name:</b> {record['first_name']} {record['last_name']}<br>
            <b>UID:</b> {record['uid']}<br>
            <b>Tickets:</b> {record['tickets']}<br>
            <b>Email:</b> {record['email']}<br>
            <b>Timestamp:</b> {record['timestamp']}<br>
            <b>Hash:</b> {record['hash']}<br>
            <b>Previous Hash:</b> {record['previous_hash']}<br>
            </div>
        """, unsafe_allow_html=True)

# ------------------ Footer ------------------
st.markdown('<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span></div>', unsafe_allow_html=True)
