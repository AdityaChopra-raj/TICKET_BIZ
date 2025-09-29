import streamlit as st
from pathlib import Path
from PIL import Image
from ledger import add_transaction, get_ledger
from events_data import EVENTS
from datetime import datetime

ASSETS_DIR = Path(__file__).parent / "assets"
PLACEHOLDER_IMG = ASSETS_DIR / "placeholder.txt"  # dummy placeholder if any image is missing

st.set_page_config(page_title="🎟 Ticket_Biz", layout="wide")

# ---------- Load CSS ----------
with open(Path(__file__).parent / "styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# ---------- Page Title ----------
st.markdown(
    '<h1 style="color:#e50914;text-align:center;font-size:60px;">🎟 Ticket_Biz — Event Ticketing</h1>',
    unsafe_allow_html=True
)

# ---------- Session State ----------
if "mode" not in st.session_state:
    st.session_state.mode = None       # None | "buy" | "checkin"
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# ---------- Buttons under heading ----------
st.markdown('<div class="center-buttons">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2,1,2])
with c2:
    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("🎟 Buy Ticket", key="buy_button"):
            st.session_state.mode = "buy"
            st.session_state.selected_event = None
    with colb2:
        if st.button("✅ Check-In", key="checkin_button"):
            st.session_state.mode = "checkin"
            st.session_state.selected_event = None
st.markdown('</div>', unsafe_allow_html=True)

# ---------- If user has clicked Buy or Check-In but not selected an event ----------
if st.session_state.mode and st.session_state.selected_event is None:
    st.markdown('<h2 style="text-align:center;">Select an Event</h2>', unsafe_allow_html=True)
    # 3x3 Grid of event cards
    rows = [EVENTS[i:i+3] for i in range(0, len(EVENTS), 3)]
    for row in rows:
        cols = st.columns(3)
        for col, event in zip(cols, row):
            with col:
                img_path = ASSETS_DIR / event["image"]
                if not img_path.exists():
                    img_path = PLACEHOLDER_IMG
                st.image(img_path, use_container_width=True)
                if st.button(event["name"], key=f"ev_{event['name']}"):
                    st.session_state.selected_event = event["name"]

# ---------- After event selected ----------
if st.session_state.selected_event:
    event = next(e for e in EVENTS if e["name"] == st.session_state.selected_event)
    st.markdown(f"<h2 style='text-align:center;color:#e50914;'>{event['name']}</h2>", unsafe_allow_html=True)
    st.write(event["description"])

    if st.session_state.mode == "buy":
        st.markdown("### Buy Tickets")
        max_tickets = min(15, event["available_tickets"])
        qty = st.number_input("Number of tickets", min_value=1, max_value=max_tickets, value=1)
        buyer_email = st.text_input("Your email")
        if st.button("Confirm Purchase"):
            if qty <= event["available_tickets"]:
                event["available_tickets"] -= qty
                add_transaction(event["name"], buyer_email, qty, datetime.now())
                st.success(f"Purchased {qty} ticket(s) for {event['name']}")
            else:
                st.error("Not enough tickets available.")

    elif st.session_state.mode == "checkin":
        st.markdown("### Venue Check-In")
        ticket_uid = st.text_input("Ticket UID")
        email = st.text_input("Email Address")
        if st.button("Check In"):
            # Example simple validation (expand as needed)
            ledger = get_ledger()
            if any(l["ticket_uid"] == ticket_uid and l["email"] == email for l in ledger):
                st.success("Check-In Successful ✅")
            else:
                st.error("Invalid Ticket UID or Email ❌")
