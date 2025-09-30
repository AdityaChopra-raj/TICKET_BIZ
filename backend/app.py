# app.py

import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS
from ledger import add_transaction, get_ledger, check_in_transaction

# Path to assets
ASSETS_DIR = Path(__file__).parent / "assets"

# ========== Helpers ==========
def get_resized_image(img_path, width=320, height=180):
    """Resize images safely with fallback placeholder."""
    try:
        img = Image.open(img_path)
    except Exception:
        img = Image.open(ASSETS_DIR / "placeholder.jpg")
    return img.resize((width, height))

def show_event_card(event, tab_name, idx):
    """Render a single event card in the grid."""
    col = st.container()
    with col:
        img = get_resized_image(ASSETS_DIR / event["image"])
        st.image(img, use_container_width=True)

        # Safe fallback for total tickets
        total_tickets = event.get("total_tickets", 100)
        tickets_left = total_tickets - sum(
            int(tx["tickets"]) for tx in get_ledger() if tx["event"] == event["name"]
        )

        # Card content
        st.markdown(f"### {event['name']}")
        st.write(event["description"])
        st.write(f"📅 {event['date']}")
        st.write(f"📍 {event['location']}")
        st.write(f"🎟️ {tickets_left}/{total_tickets} tickets left")
        st.write(f"💰 ₹{event['price']} per ticket")

        # Action buttons
        if tab_name == "buy":
            if st.button("Select Event to Buy", key=f"buy_btn_{idx}"):
                st.session_state["selected_event"] = event
        elif tab_name == "checkin":
            if st.button("Select Event to Check In", key=f"checkin_btn_{idx}"):
                st.session_state["selected_event"] = event


# ========== Main App ==========
st.set_page_config(page_title="🎟 Ticket_Biz", layout="wide")

st.title("🎟 Ticket_Biz — Event Ticketing")
tabs = st.tabs(["🏠 Home", "🛒 Buy Ticket", "✅ Check In", "🔗 Blockchain"])

# ---------- HOME ----------
with tabs[0]:
    st.markdown(
        "<h2 style='text-align: center; color: white;'>Welcome to Ticket_Biz</h2>",
        unsafe_allow_html=True,
    )
    st.write("Your trusted blockchain-powered event ticketing platform.")

# ---------- BUY TICKET ----------
with tabs[1]:
    st.header("Trending Events - Buy Tickets")

    # Grid for events
    cols = st.columns(3)
    for idx, event in enumerate(EVENTS):
        with cols[idx % 3]:
            show_event_card(event, tab_name="buy", idx=idx)

    # Show buy form if event selected
    if "selected_event" in st.session_state and st.session_state["selected_event"]:
        event = st.session_state["selected_event"]
        st.subheader(f"Buy Tickets for {event['name']}")

        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        student_id = st.text_input("Student ID")
        email = st.text_input("Email")
        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, step=1)

        # Dynamic total cost
        total_cost = num_tickets * event["price"]
        st.write(f"💰 **Total Cost: ₹{total_cost}**")

        if st.button("Confirm Purchase"):
            if all([first_name, last_name, student_id, email, num_tickets]):
                add_transaction(
                    event["name"], first_name, last_name, student_id, num_tickets
                )
                st.success(
                    f"🎉 Tickets purchased successfully for {event['name']}! "
                    f"Total Cost: ₹{total_cost}"
                )
                st.session_state["selected_event"] = None
            else:
                st.error("⚠️ Please fill in all details before confirming.")

# ---------- CHECK IN ----------
with tabs[2]:
    st.header("Check In")

    cols = st.columns(3)
    for idx, event in enumerate(EVENTS):
        with cols[idx % 3]:
            show_event_card(event, tab_name="checkin", idx=idx)

    if "selected_event" in st.session_state and st.session_state["selected_event"]:
        event = st.session_state["selected_event"]
        st.subheader(f"Check In for {event['name']}")

        ticket_uid = st.text_input("Enter Ticket UID")
        check_in_count = st.number_input("Number of People Checking In", min_value=1, max_value=15, step=1)

        if st.button("Confirm Check In"):
            if ticket_uid:
                success = check_in_transaction(ticket_uid, check_in_count)
                if success:
                    st.success(f"✅ {check_in_count} people checked in successfully!")
                    st.session_state["selected_event"] = None
                else:
                    st.error("❌ Invalid Ticket UID or check-in failed.")
            else:
                st.error("⚠️ Please enter your Ticket UID.")

# ---------- BLOCKCHAIN ----------
with tabs[3]:
    st.header("Blockchain Ledger")
    ledger = get_ledger()

    if not ledger:
        st.info("No transactions recorded yet.")
    else:
        for tx in ledger:
            st.markdown(
                f"""
                <div style="background:#111418; padding:15px; border-radius:10px; margin-bottom:10px;">
                    <b>Event:</b> {tx['event']} <br>
                    <b>Name:</b> {tx['first_name']} {tx['last_name']} <br>
                    <b>Student ID:</b> {tx['student_id']} <br>
                    <b>Email:</b> {tx['email']} <br>
                    <b>Tickets:</b> {tx['tickets']} <br>
                    <b>Transaction Hash:</b> {tx['hash']}
                </div>
                """,
                unsafe_allow_html=True,
            )
