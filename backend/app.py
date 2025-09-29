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

# -------------------- Session State --------------------
if "mode" not in st.session_state:
    st.session_state.mode = None
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# -------------------- Page Title --------------------
st.markdown(
    '<h1 style="color:#e50914;text-align:center;font-size:100px;">🎟 Ticket_Biz — Event Ticketing</h1>',
    unsafe_allow_html=True
)

# -------------------- Welcome Paragraph --------------------
st.markdown(
    '<p style="text-align:center; font-size:20px; color:#ddd; max-width:800px; margin:auto;">'
    'Welcome to Ticket_Biz! This platform allows you to book and check-in for various exciting events, '
    'all while keeping your transactions secure using blockchain technology.'
    '</p>',
    unsafe_allow_html=True
)

# -------------------- Center Buttons --------------------
st.markdown('<div class="center-buttons">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,1,1])
with c2:
    colb1, colb2, colb3 = st.columns(3)
    with colb1:
        if st.button("🎟 Buy Ticket", key="buy_button"):
            st.session_state.mode = "buy"
            st.session_state.selected_event = None
    with colb2:
        if st.button("✅ Check-In", key="checkin_button"):
            st.session_state.mode = "checkin"
            st.session_state.selected_event = None
    with colb3:
        if st.button("🔗 Blockchain", key="blockchain_button"):
            st.session_state.mode = "blockchain"
            st.session_state.selected_event = None
st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Image Resizing Function --------------------
def get_resized_image(image_path, target_width=320, target_height=480):
    try:
        img = Image.open(image_path)
    except:
        img = Image.open(ASSETS_DIR / "placeholder.jpg")

    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = left + target_width
    bottom = top + target_height
    img = img.crop((left, top, right, bottom))

    return img

# -------------------- Event Grid --------------------
if st.session_state.mode in ["buy", "checkin"] and st.session_state.selected_event is None:
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    for event in EVENTS:
        with st.container():
            st.markdown('<div class="event-card">', unsafe_allow_html=True)
            img_path = ASSETS_DIR / event["image"]
            if not img_path.exists():
                img_path = ASSETS_DIR / "placeholder.jpg"

            resized_img = get_resized_image(img_path)
            temp_path = ASSETS_DIR / "temp_display.png"
            resized_img.save(temp_path)
            st.image(str(temp_path), use_container_width=True)

            st.markdown('<div class="card-content">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{event["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-desc">{event["description"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="card-details">📅 {event["date"]}<br>📍 {event["location"]}<br>'
                f'🎟️ Tickets left: <b>{event["available_tickets"]}</b><br>'
                f'✅ Check-Ins: <b>{event["check_ins"]}</b><br>'
                f'💰 Price: ₹{event["price"]}</div>',
                unsafe_allow_html=True
            )
            if st.button(event["name"], key=f"btn_{event['id']}"):
                st.session_state.selected_event = event["name"]
            st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Selected Event --------------------
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
            record = next(
                (l for l in ledger if l["ticket_uid"] == ticket_uid and l["email"] == email),
                None
            )
            if record:
                if event["check_ins"] + 1 <= record["tickets_bought"]:
                    event["check_ins"] += 1
                    st.success(f"Check-In Successful ✅ ({event['check_ins']} checked in)")
                else:
                    st.error("All tickets for this UID are already checked in ❌")
            else:
                st.error("Invalid Ticket UID or Email ❌")

# -------------------- Blockchain Ledger --------------------
if st.session_state.mode == "blockchain":
    st.markdown("<h2 style='text-align:center;color:#e50914;'>Blockchain Ledger Records</h2>", unsafe_allow_html=True)
    ledger = get_ledger()
    if ledger:
        st.table(ledger)
    else:
        st.info("No blockchain records yet.")

# -------------------- Footer --------------------
st.markdown(
    '<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span>.</div>',
    unsafe_allow_html=True
)
