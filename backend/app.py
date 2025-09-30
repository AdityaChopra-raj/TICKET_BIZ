import streamlit as st
from pathlib import Path
from PIL import Image

from ledger import add_transaction, get_ledger, check_in_transaction
from events_data import EVENTS
from email_utils import send_email  # ✅ Import email sender

# Assets folder
ASSETS_DIR = Path(__file__).parent / "assets"

# ---------------------------
# Helpers
# ---------------------------
def get_resized_image(image_path, size=(400, 225)):
    """Resize event images to 16:9 ratio for cards."""
    img = Image.open(image_path)
    img = img.resize(size)
    return img

def show_event_card(event, idx, tab_name):
    """Render event card with Buy or Check In options depending on tab."""
    img_path = ASSETS_DIR / event["image"]
    img = get_resized_image(img_path)

    st.markdown(
        f"""
        <div class="event-card" style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:20px;">
            <h3 style="text-align:center;">{event['name']}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.image(img, use_container_width=True)

    tickets_left = event["total_tickets"] - sum(
        tx["tickets"] for tx in get_ledger() if tx["event"] == event["name"]
    )
    st.markdown(f"**Available Tickets:** {tickets_left}")
    st.write(event["description"])

    if tab_name == "buy":
        if st.button(f"Buy for {event['name']}", key=f"buy_btn_{tab_name}_{idx}"):
            st.session_state["selected_event"] = event["name"]
            st.session_state["current_view"] = "buy_form"

    elif tab_name == "checkin":
        if st.button(f"Check In for {event['name']}", key=f"checkin_btn_{tab_name}_{idx}"):
            st.session_state["selected_event"] = event["name"]
            st.session_state["current_view"] = "checkin_form"


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="TicketBiz", layout="wide")

# Tabs navigation
tabs = ["Home", "Buy Ticket", "Check In", "Blockchain Ledger"]
selected_tab = st.tabs(tabs)

# ---------------------------
# HOME TAB
# ---------------------------
with selected_tab[0]:
    st.title("🎟️ TicketBiz Platform")
    st.write("Welcome to the decentralized event ticketing system.")

    for idx, event in enumerate(EVENTS):
        show_event_card(event, idx, tab_name="home")

# ---------------------------
# BUY TICKET TAB
# ---------------------------
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
            num_tickets = st.number_input("Number of Tickets", min_value=1, step=1)

            submitted = st.form_submit_button("Confirm Purchase")
            if submitted:
                if first_name and last_name and student_id and email and num_tickets:
                    uid = add_transaction(
                        event_name, first_name, last_name, student_id, num_tickets, email
                    )

                    # ✅ Send Ticket UID via email
                    subject = f"Your Ticket for {event_name}"
                    body = (
                        f"Hello {first_name} {last_name},\n\n"
                        f"Thank you for purchasing {num_tickets} ticket(s) for {event_name}.\n"
                        f"Your unique Ticket UID is: {uid}\n\n"
                        f"Please save this UID to check in at the event.\n\n"
                        "Best regards,\nTicketBiz Team"
                    )

                    try:
                        send_email(to=email, subject=subject, body=body)
                        st.success(
                            f"✅ Purchase successful! Your Ticket UID is: **{uid}**. "
                            f"An email has been sent to **{email}** with your ticket details."
                        )
                    except Exception as e:
                        st.warning(
                            f"⚠️ Purchase successful! Your Ticket UID is: **{uid}**, "
                            f"but the email could not be sent. Error: {e}"
                        )

                    st.session_state["current_view"] = "cards"
                else:
                    st.error("⚠️ Please fill in all fields before confirming.")

# ---------------------------
# CHECK IN TAB
# ---------------------------
with selected_tab[2]:
    st.header("Check In")

    if "checkin_view" not in st.session_state:
        st.session_state["checkin_view"] = "cards"

    if st.session_state["checkin_view"] == "cards":
        for idx, event in enumerate(EVENTS):
            show_event_card(event, idx, tab_name="checkin")

    elif st.session_state["checkin_view"] == "checkin_form":
        event_name = st.session_state["selected_event"]
        st.subheader(f"Check In for {event_name}")

        with st.form("checkin_form"):
            ticket_uid = st.text_input("Enter Ticket UID")
            num_people = st.number_input("Number of People Checking In", min_value=1, step=1)
            submitted = st.form_submit_button("Confirm Check In")

            if submitted:
                if check_in_transaction(ticket_uid, num_people):
                    st.success("✅ Check-in successful!")
                else:
                    st.error("❌ Invalid UID or exceeding purchased tickets.")

        st.session_state["checkin_view"] = "cards"

# ---------------------------
# BLOCKCHAIN LEDGER TAB
# ---------------------------
with selected_tab[3]:
    st.header("Blockchain Ledger")
    ledger = get_ledger()
    if ledger:
        for tx in ledger:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                    <b>Event:</b> {tx['event']}<br>
                    <b>Name:</b> {tx['first_name']} {tx['last_name']}<br>
                    <b>Student ID:</b> {tx['student_id']}<br>
                    <b>Email:</b> {tx['email']}<br>
                    <b>Tickets:</b> {tx['tickets']} (Checked in: {tx['checked_in']})<br>
                    <b>Ticket UID:</b> {tx['uid']}<br>
                    <b>Timestamp:</b> {tx['timestamp']}<br>
                    <b>Hash:</b> {tx['hash']}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No transactions recorded yet.")
