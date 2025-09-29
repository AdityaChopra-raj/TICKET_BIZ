# app.py

import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS
from ledger import add_transaction, get_ledger, update_check_in

ASSETS_DIR = Path(__file__).parent / "assets"

st.set_page_config(page_title="🎟 Ticket_Biz — Event Ticketing", layout="wide")

st.markdown(
    """
    <h1 style="text-align:center; font-size:48px; color:#e50914;">🎟 Ticket_Biz — Event Ticketing</h1>
    <p style="text-align:center; color:#ddd; font-size:18px;">
    Welcome! Buy tickets for trending events or check-in at your venue. Powered by blockchain technology.
    </p>
    """,
    unsafe_allow_html=True,
)

# --- Tabs ---
tabs = st.tabs(["Home", "Buy Ticket", "Check-In", "Blockchain"])

# --- Home Tab ---
with tabs[0]:
    st.markdown("<h2 style='text-align:center; color:#fff;'>Welcome to Ticket_Biz</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#bbb;'>Use the tabs above to buy tickets, check-in, or view blockchain records.</p>", unsafe_allow_html=True)

# --- Buy Ticket Tab ---
with tabs[1]:
    st.markdown("<h2 style='color:#fff;'>Trending Events</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, event in enumerate(EVENTS):
        col = cols[idx % 3]
        with col:
            img_path = ASSETS_DIR / event["image"]
            try:
                img = Image.open(img_path)
            except:
                img = Image.open(ASSETS_DIR / "placeholder.jpg")
            st.image(img, use_container_width=True)
            st.markdown(f"<h3 style='color:#fff'>{event['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#bbb'>{event['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:green; font-weight:bold;'>Available Tickets: {event['available_tickets']}</p>", unsafe_allow_html=True)

            buy_key = f"buy_btn_{event['id']}"
            if st.button("Buy Ticket", key=buy_key):
                st.session_state["selected_event"] = event
                st.session_state["action"] = "buy"

# --- Check-In Tab ---
with tabs[2]:
    st.markdown("<h2 style='color:#fff;'>Check-In</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    for idx, record in enumerate(ledger):
        st.markdown(f"<p style='color:#ddd;'>Event: {record['event']} | Tickets Bought: {record['tickets']} | Check-Ins: {record['check_ins']}</p>", unsafe_allow_html=True)

        checkin_key = f"check_btn_{idx}"
        if st.button("Check-In", key=checkin_key):
            st.session_state["check_in_idx"] = idx
            st.session_state["action"] = "checkin"

# --- Blockchain Tab ---
with tabs[3]:
    st.markdown("<h2 style='color:#fff;'>Blockchain Ledger</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    for idx, record in enumerate(ledger):
        st.markdown(
            f"""
            <div style='border:1px solid #444; border-radius:8px; padding:10px; margin-bottom:10px; background-color:#111418;'>
                <b style='color:#e50914'>Event:</b> {record['event']}<br>
                <b>Buyer:</b> {record['first_name']} {record['last_name']} | <b>Email:</b> {record['email']} | <b>Student ID:</b> {record['student_id']}<br>
                <b>Tickets:</b> {record['tickets']} | <b>Check-Ins:</b> {record['check_ins']}<br>
                <b>Prev Hash:</b> {record['prev_hash']}<br>
                <b>Hash:</b> {record['hash']}<br>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Handle Buy Ticket Flow ---
if "action" in st.session_state and st.session_state["action"] == "buy":
    event = st.session_state.get("selected_event")
    if event:
        st.markdown(f"<h2 style='color:#fff;'>Buy Tickets for {event['name']}</h2>", unsafe_allow_html=True)
        with st.form(key="buy_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            student_id = st.text_input("Student ID")
            email = st.text_input("Email")
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=15, value=1)
            submit = st.form_submit_button("Confirm Purchase")
            if submit:
                if not (first_name and last_name and student_id and email):
                    st.warning("All fields are required to purchase tickets.")
                elif num_tickets > event["available_tickets"]:
                    st.warning(f"Only {event['available_tickets']} tickets are available.")
                else:
                    add_transaction(event["name"], first_name, last_name, student_id, email, num_tickets)
                    event["available_tickets"] -= num_tickets
                    st.success(f"Successfully purchased {num_tickets} tickets for {event['name']}!")

# --- Handle Check-In Flow ---
if "action" in st.session_state and st.session_state["action"] == "checkin":
    idx = st.session_state.get("check_in_idx")
    ledger = get_ledger()
    if idx is not None and idx < len(ledger):
        record = ledger[idx]
        st.markdown(f"<h2 style='color:#fff;'>Check-In for {record['event']}</h2>", unsafe_allow_html=True)
        num_check = st.number_input("Number of People Checking In", min_value=1, max_value=record["tickets"], value=1)
        if st.button("Confirm Check-In", key=f"confirm_checkin_{idx}"):
            update_check_in(idx, num_check)
            st.success(f"{num_check} people checked in for {record['event']}!")
