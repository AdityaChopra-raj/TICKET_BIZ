import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS, ASSETS_DIR
from ledger import add_transaction, get_ledger
from datetime import datetime

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# Load CSS
with open(Path(__file__).parent / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title
st.markdown(
    '<h1 style="color:#e50914;text-align:center;font-size:60px;">🎟 Ticket_Biz — Event Ticketing</h1>',
    unsafe_allow_html=True
)

# Session State
if "mode" not in st.session_state:
    st.session_state.mode = None
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# Buttons under heading
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

# Show event grid only if mode selected
if st.session_state.mode and st.session_state.selected_event is None:
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for event in EVENTS:
        with st.container():
            st.markdown('<div class="event-card">', unsafe_allow_html=True)
            img_path = ASSETS_DIR / event["image"]
            if not img_path.exists():
                img_path = ASSETS_DIR / "placeholder.txt"
            st.markdown(f'<img src="{img_path}" class="card-image">', unsafe_allow_html=True)

            st.markdown('<div class="card-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{event["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-desc">{event["description"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="card-details">📅 {event["date"]}<br>📍 {event["location"]}<br>'
                f'🎟️ Tickets left: <b>{event["available_tickets"]}</b><br>💰 Price: ₹{event["price"]}</div>',
                unsafe_allow_html=True
            )
            if event["available_tickets"] <= 0:
                st.markdown('<span class="status-badge full">FULL</span>', unsafe_allow_html=True)
            if st.button(event["name"], key=f"btn_{event['id']}"):
                st.session_state.selected_event = event["name"]
            st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# After event selected
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
            ledger = get_ledger()
            if any(l["ticket_uid"] == ticket_uid and l["email"] == email for l in ledger):
                st.success("Check-In Successful ✅")
            else:
                st.error("Invalid Ticket UID or Email ❌")

# Footer
st.markdown('<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span>.</div>', unsafe_allow_html=True)
