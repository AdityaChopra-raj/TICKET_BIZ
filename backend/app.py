import streamlit as st
from PIL import Image
from pathlib import Path
from events_data import EVENTS
from ledger import add_transaction, get_ledger, check_in_ticket
from email_utils import send_email

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# Streamlit page config
st.set_page_config(page_title="🎟 Ticket_Biz — Event Ticketing", layout="wide")

# -----------------------------
# Utility function to resize images uniformly
# -----------------------------
def get_resized_image(img_path, width=320, height=180):
    img = Image.open(img_path)
    return img.resize((width, height))

# -----------------------------
# Show event card
# -----------------------------
def show_event_card(event, idx, tab_name="buy"):
    # Image
    img_path = ASSETS_DIR / event["image"]
    try:
        img = get_resized_image(img_path)
    except:
        img = get_resized_image(ASSETS_DIR / "placeholder.jpg")

    st.image(img, use_container_width=True)

    # Available badge below image
    tickets_sold = sum([tx["num_tickets"] for tx in get_ledger() if tx["event"] == event["name"]])
    tickets_left = max(event["total_tickets"] - tickets_sold, 0)
    available_text = f"AVAILABLE: {tickets_left} tickets"
    if tickets_left == 0:
        available_text = "FULL"
    st.markdown(f"<div style='color: {'green' if tickets_left>0 else 'red'}; font-weight:bold;'>{available_text}</div>", unsafe_allow_html=True)

    # Event info
    st.markdown(f"### {event['name']}")
    st.markdown(f"{event['description']}")
    st.markdown(f"📅 {event['date']}  |  📍 {event['venue']}  |  🎟️ {tickets_left}/{event['total_tickets']} tickets left  |  💰 ₹{event['price']}")

    # Buttons
    buy_key = f"buy_btn_{tab_name}_{idx}"
    checkin_key = f"checkin_btn_{tab_name}_{idx}"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Buy Ticket", key=buy_key):
            st.session_state["current_view"] = "buy_form"
            st.session_state["selected_event"] = event["name"]
    with col2:
        if st.button("Check In", key=checkin_key):
            st.session_state["current_view_checkin"] = "checkin_form"
            st.session_state["selected_event"] = event["name"]

# -----------------------------
# Tabs
# -----------------------------
tabs = ["Home", "Buy Ticket", "Check In", "Blockchain Ledger"]
selected_tab = st.tabs(tabs)

# -----------------------------
# HOME TAB
# -----------------------------
with selected_tab[0]:
    st.title("🎟 Ticket_Biz — Event Ticketing")
    st.markdown(
        """
        Welcome to **Ticket_Biz**, your one-stop platform for event ticketing powered by Blockchain Technology. 
        Buy tickets, check in securely, and track your ticket ledger with transparency.
        """)
    st.markdown("---")

# -----------------------------
# BUY TICKET TAB
# -----------------------------
with selected_tab[1]:
    st.header("Buy Tickets")
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "cards"

    if st.session_state["current_view"] == "cards":
        for idx, event in enumerate(EVENTS):
            show_event_card(event, idx, tab_name="buy")

    elif st.session_state["current_view"] == "buy_form":
        event_name = st.session_state["selected_event"]
        st.subheader(f"Buy Tickets for {event_name}")

        with st.form("buy_ticket_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            student_id = st.text_input("Student ID")
            email = st.text_input("Email")
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, step=1)

            submitted = st.form_submit_button("Confirm Purchase")
            if submitted:
                if first_name and last_name and student_id and email and num_tickets:
                    uid = add_transaction(
                        event_name, first_name, last_name, student_id, num_tickets, email
                    )
                    subject = f"Your Ticket for {event_name}"
                    body = (
                        f"Hello {first_name} {last_name},\n\n"
                        f"Thank you for purchasing {num_tickets} ticket(s) for {event_name}.\n"
                        f"Your unique Ticket UID is: {uid}\n\n"
                        "Please save this UID to check in at the event.\n\n"
                        "Best regards,\nTicketBiz Team"
                    )
                    try:
                        send_email(email, subject, body)
                        st.success(
                            f"✅ Purchase successful! Your Ticket UID is: **{uid}**. "
                            f"An email has been sent to **{email}** with your ticket details."
                        )
                    except Exception as e:
                        st.warning(
                            f"⚠️ Purchase successful! UID: **{uid}**, but email failed. Error: {e}"
                        )
                    st.session_state["current_view"] = "cards"
                else:
                    st.error("⚠️ Please fill in all fields before confirming.")

# -----------------------------
# CHECK IN TAB
# -----------------------------
with selected_tab[2]:
    st.header("Check In")
    if "current_view_checkin" not in st.session_state:
        st.session_state["current_view_checkin"] = "cards"

    if st.session_state["current_view_checkin"] == "cards":
        for idx, event in enumerate(EVENTS):
            show_event_card(event, idx, tab_name="checkin")

    elif st.session_state["current_view_checkin"] == "checkin_form":
        event_name = st.session_state["selected_event"]
        st.subheader(f"Check In for {event_name}")

        with st.form("checkin_form"):
            ticket_uid = st.text_input("Enter Ticket UID")
            email = st.text_input("Email used for purchase")
            num_people = st.number_input(
                "Number of People Checking In", min_value=1, max_value=15, step=1
            )

            submitted = st.form_submit_button("Check In")
            if submitted:
                if ticket_uid and email:
                    success, message = check_in_ticket(ticket_uid, email, num_people)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"⚠️ {message}")
                    st.session_state["current_view_checkin"] = "cards"
                else:
                    st.error("⚠️ Please enter both Ticket UID and Email.")

# -----------------------------
# BLOCKCHAIN LEDGER TAB
# -----------------------------
with selected_tab[3]:
    st.header("Blockchain Ledger")
    ledger = get_ledger()
    if ledger:
        for record in ledger:
            st.markdown(
                f"**Event:** {record['event']}  |  **UID:** {record['uid']}  |  "
                f"**Buyer:** {record['first_name']} {record['last_name']}  |  "
                f"**Tickets:** {record['num_tickets']}  |  **Email:** {record['email']}"
            )
    else:
        st.info("Ledger is empty.")
