import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS
from ledger import BlockchainLedger

ASSETS_DIR = Path(__file__).parent / "assets"
ledger = BlockchainLedger()

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# ---- Custom CSS ----
with open(Path(__file__).parent / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------- Session State --------
if "mode" not in st.session_state:
    st.session_state.mode = "buy"  # default
for event in EVENTS:
    if f"{event['id']}_sold" not in st.session_state:
        st.session_state[f"{event['id']}_sold"] = 0
        st.session_state[f"{event['id']}_checkin"] = 0

# -------- Centered Buttons under Heading --------
st.markdown('<div class="center-buttons">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2,1,2])  # center column narrower
with c2:
    colb1, colb2 = st.columns(2)
    with colb1:
        if st.button("🎟 Buy Ticket", key="buy_button"):
            st.session_state.mode = "buy"
    with colb2:
        if st.button("✅ Check-In", key="checkin_button"):
            st.session_state.mode = "checkin"
st.markdown('</div>', unsafe_allow_html=True)


# -------- Modes --------
if st.session_state.mode == "buy":
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for event in EVENTS:
        sold = st.session_state[f"{event['id']}_sold"]
        checkin = st.session_state[f"{event['id']}_checkin"]
        available = event["total_tickets"] - sold
        is_full = available <= 0
        badge_class = "status-badge full" if is_full else "status-badge"
        badge_text = "FULL" if is_full else "Available"

        with st.container():
            st.markdown('<div class="event-card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="position:relative;">
                <span class="{badge_class}">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)

            img_path = event["image"]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.image(str(ASSETS_DIR / "placeholder.txt"), use_container_width=True)

            st.markdown('<div class="card-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{event["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-desc">{event["description"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-details">📅 {event["date"]}<br>📍 {event["location"]}<br>🎟️ Tickets left: <b>{available}</b><br>💰 Price: ₹{event["price"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-details">✅ People checked in: <b>{checkin}</b></div>', unsafe_allow_html=True)

            if not is_full:
                qty = st.number_input(f"Select tickets for {event['name']}", 1, 15, 1, key=f"qty_{event['id']}")
                if st.button(f"Book Now — {event['name']}", key=f"btn_{event['id']}"):
                    if qty <= available:
                        st.session_state[f"{event['id']}_sold"] += qty
                        ledger.add_record(event['id'], "Customer", qty)
                        st.success(f"✅ {qty} ticket(s) booked for {event['name']}!")
                    else:
                        st.error("Not enough tickets available.")
            else:
                st.error("Event is FULL.")
            st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.mode == "checkin":
    st.subheader("✅ Venue Check-In")
    uid = st.text_input("Enter Ticket UID")
    email = st.text_input("Enter Email Address")
    if st.button("Check In Now"):
        if uid and email:
            st.success("✅ Check-In Successful for UID: " + uid)
        else:
            st.error("Please enter both UID and Email.")

# -------- Ledger --------
st.markdown('<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span>.</div>', unsafe_allow_html=True)
st.header("🔗 Blockchain Ledger")
st.write(ledger.all_records())
