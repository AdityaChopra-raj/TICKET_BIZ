import streamlit as st
from PIL import Image
from pathlib import Path
from ledger import add_transaction, get_ledger, check_in_ticket
from events_data import EVENTS

# Directories
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(page_title="🎟 Ticket_Biz", layout="wide")

# ------------------- Helper Functions -------------------

def get_resized_image(img_path, width=320, height=180):
    """Open and resize image to uniform dimensions."""
    img = Image.open(img_path)
    img = img.resize((width, height), Image.LANCZOS)
    return img

def show_event_card(event, tab_name, idx):
    """Display a single event card."""
    img_path = ASSETS_DIR / event["image"]
    img = get_resized_image(img_path)

    st.image(img, use_container_width=True)
    
    # Availability Tag
    tickets_sold = sum([r["num_tickets"] for r in get_ledger() if r["event"] == event["name"]])
    tickets_left = event["total_tickets"] - tickets_sold
    availability = "AVAILABLE" if tickets_left > 0 else "FULL"
    avail_color = "#16a34a" if tickets_left > 0 else "#dc2626"
    st.markdown(f'<p style="color:{avail_color}; font-weight:bold;">{availability}</p>', unsafe_allow_html=True)

    # Event Title & Description
    st.markdown(f"### {event['name']}")
    st.markdown(f"{event['description']}")

    # Details
    st.markdown(f"📅 {event['date_time']}")
    st.markdown(f"📍 {event['venue']}")
    st.markdown(f"🎟️ {tickets_left}/{event['total_tickets']} tickets left")
    st.markdown(f"💰 From ₹{event['price']}")

    # Buy Ticket or Check-In buttons
    if tab_name == "buy":
        buy_key = f"buy_btn_{idx}"
        if st.button("Buy Ticket", key=buy_key):
            st.session_state["selected_event"] = event["name"]
            st.session_state["action"] = "buy"

    elif tab_name == "checkin":
        check_key = f"check_btn_{idx}"
        if st.button("Check In", key=check_key):
            st.session_state["selected_event"] = event["name"]
            st.session_state["action"] = "checkin"

# ------------------- App State -------------------

if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None
if "action" not in st.session_state:
    st.session_state["action"] = None

# ------------------- Tabs -------------------

tabs = ["Home", "Buy Ticket", "Check In", "Blockchain"]
active_tab = st.tabs(tabs)

with active_tab[0]:
    st.markdown('<h1 style="text-align:center; color:#e50914; font-size:48px;">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ddd;">Welcome to Ticket_Biz! Buy your event tickets or check in securely with blockchain-verified records.</p>', unsafe_allow_html=True)

with active_tab[1]:
    st.markdown("<h2>Buy Tickets</h2>", unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="buy", idx=idx)
    
    # Buy Ticket Form
    if st.session_state["selected_event"] and st.session_state["action"] == "buy":
        st.subheader(f"Buy Tickets for {st.session_state['selected_event']}")
        first_name = st.text_input("First Name", key="buy_fname")
        last_name = st.text_input("Last Name", key="buy_lname")
        student_id = st.text_input("Student ID", key="buy_sid")
        email = st.text_input("Email", key="buy_email")
        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, step=1, key="buy_num")
        if st.button("Confirm Purchase"):
            if first_name and last_name and student_id and email:
                add_transaction(
                    st.session_state["selected_event"],
                    first_name,
                    last_name,
                    student_id,
                    email,
                    num_tickets
                )
                st.success("Tickets purchased successfully!")
            else:
                st.error("Please fill all required fields.")

with active_tab[2]:
    st.markdown("<h2>Check In</h2>", unsafe_allow_html=True)
    for idx, event in enumerate(EVENTS):
        show_event_card(event, tab_name="checkin", idx=idx)

    # Check-In Form
    if st.session_state["selected_event"] and st.session_state["action"] == "checkin":
        st.subheader(f"Check In for {st.session_state['selected_event']}")
        uid = st.text_input("Enter Ticket UID", key="check_uid")
        num_people = st.number_input("Number of People Checking In", min_value=1, max_value=15, step=1, key="check_num")
        if st.button("Confirm Check-In"):
            try:
                check_in_ticket(uid, num_people)
                st.success(f"Successfully checked in {num_people} person(s)!")
            except Exception as e:
                st.error(str(e))

with active_tab[3]:
    st.markdown("<h2>Blockchain Ledger</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    for record in ledger:
        st.markdown(f"**Event:** {record['event']}")
        st.markdown(f"**Name:** {record['first_name']} {record['last_name']}")
        st.markdown(f"**UID:** {record['uid']}")
        st.markdown(f"**Tickets Bought:** {record['num_tickets']}")
        st.markdown(f"**Checked In:** {record['checked_in']}")
        st.markdown("---")
