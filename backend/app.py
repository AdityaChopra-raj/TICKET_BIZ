import streamlit as st
from pathlib import Path
from PIL import Image
from events_data import EVENTS, ASSETS_DIR
from ledger import add_transaction, get_ledger
from datetime import datetime

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# -------------------- Load CSS --------------------
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

# -------------------- Image Resizing --------------------
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

    # Crop center
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = left + target_width
    bottom = top + target_height
    img = img.crop((left, top, right, bottom))

    return img

# -------------------- Trending Events Section --------------------
if st.session_state.mode in ["buy", "checkin"] and st.session_state.selected_event is None:
    st.markdown('<h2 class="section-title">Trending Events</h2>', unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    
    for event in EVENTS:
        st.markdown('<div class="event-card">', unsafe_allow_html=True)
        
        # Image + Available tag
        st.markdown('<div class="card-image-container">', unsafe_allow_html=True)
        img_path = ASSETS_DIR / event["image"]
        if not img_path.exists():
            img_path = ASSETS_DIR / "placeholder.jpg"
        resized_img = get_resized_image(img_path, target_width=400, target_height=220)
        temp_path = ASSETS_DIR / "temp_display.png"
        resized_img.save(temp_path)
        st.image(str(temp_path), use_column_width=True)
        st.markdown('<div class="availability-tag">AVAILABLE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Card content
        st.markdown('<div class="card-content">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{event.get("name","Event Title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-desc">{event.get("description","Short description goes here.")}</div>', unsafe_allow_html=True)
        
        # Details with icons
        st.markdown('<div class="card-details">', unsafe_allow_html=True)
        st.markdown(f'<div>📅 {event.get("date","DD-MM-YYYY HH:MM")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div>📍 {event.get("location","Venue Address")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div>🎟️ {event.get("available_tickets",0)}/{event.get("available_tickets",0)} tickets left</div>', unsafe_allow_html=True)
        st.markdown(f'<div>₹ From {event.get("price",0)} - {event.get("price",0)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Book Now Button
        st.markdown('<button>Book Now</button>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Selected Event --------------------
if st.session_state.selected_event:
    event = next(e for e in EVENTS if e.get("name") == st.session_state.selected_event)
    st.markdown(f"<h2 style='text-align:center;color:#e50914;'>{event.get('name')}</h2>", unsafe_allow_html=True)
    st.write(event.get("description",""))

    if st.session_state.mode == "buy":
        st.markdown("### Buy Tickets")
        
        # Customer info
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        student_id = st.text_input("Student ID")
        email = st.text_input("Email Address")
        
        max_tickets = min(15, event.get("available_tickets",0))
        qty = st.number_input("Number of tickets", min_value=1, max_value=max_tickets, value=1)
        
        if st.button("Confirm Purchase"):
            if not all([first_name, last_name, student_id, email]):
                st.error("Please fill in all required fields!")
            elif qty > event.get("available_tickets",0):
                st.error("Not enough tickets available.")
            else:
                event["available_tickets"] -= qty
                add_transaction(
                    event.get("name"),
                    email,
                    qty,
                    datetime.now(),
                    first_name=first_name,
                    last_name=last_name,
                    student_id=student_id
                )
                st.success(f"Purchased {qty} ticket(s) for {event.get('name')}")

    elif st.session_state.mode == "checkin":
        st.markdown("### Venue Check-In")
        ticket_uid = st.text_input("Ticket UID")
        email = st.text_input("Email Address")
        if st.button("Check In"):
            ledger = get_ledger()
            record = next(
                (l for l in ledger if l.get("ticket_uid") == ticket_uid and l.get("email") == email),
                None
            )
            if record:
                if event.get("check_ins",0) + 1 <= int(record.get("tickets_bought",0)):
                    event["check_ins"] = event.get("check_ins",0) + 1
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
        st.markdown('<div class="event-grid">', unsafe_allow_html=True)
        for record in ledger:
            st.markdown('<div class="event-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-content">', unsafe_allow_html=True)
            st.markdown(f"<b>Event:</b> {record.get('event','N/A')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Name:</b> {record.get('first_name','')} {record.get('last_name','')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Student ID:</b> {record.get('student_id','')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Email:</b> {record.get('email','')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Tickets Bought:</b> {record.get('tickets_bought','')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Ticket UID:</b> {record.get('ticket_uid','')}<br>", unsafe_allow_html=True)
            st.markdown(f"<b>Timestamp:</b> {record.get('timestamp','')}<br>", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No blockchain records yet.")

# -------------------- Footer --------------------
st.markdown(
    '<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span>.</div>',
    unsafe_allow_html=True
)
