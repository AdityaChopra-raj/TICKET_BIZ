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
    'Welcome to Ticket_Biz! Book and check-in for trending events easily, '
    'with blockchain-secured ticketing for full transparency and trust.'
    '</p>',
    unsafe_allow_html=True
)

# -------------------- Center Buttons --------------------
st.markdown('<div class="center-buttons">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎟 Buy Ticket", key="buy_button"):
        st.session_state.mode = "buy"
        st.session_state.selected_event = None
with col2:
    if st.button("✅ Check-In", key="checkin_button"):
        st.session_state.mode = "checkin"
        st.session_state.selected_event = None
with col3:
    if st.button("🔗 Blockchain", key="blockchain_button"):
        st.session_state.mode = "blockchain"
        st.session_state.selected_event = None
st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Image Resizing --------------------
def get_resized_image(image_path, target_width=320, target_height=180):
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

# -------------------- Trending Events Grid --------------------
if st.session_state.mode in ["buy", "checkin"] and st.session_state.selected_event is None:
    st.markdown('<h2 class="section-title">Trending Events</h2>', unsafe_allow_html=True)
    st.markdown('<div class="event-grid">', unsafe_allow_html=True)
    
    for event in EVENTS:
        st.markdown('<div class="event-card">', unsafe_allow_html=True)
        
        # Image + Available tag
        st.markdown('<div class="card-image-container">', unsafe_allow_html=True)
        img_path = ASSETS_DIR / event.get("image","placeholder.jpg")
        if not img_path.exists():
            img_path = ASSETS_DIR / "placeholder.jpg"
        resized_img = get_resized_image(img_path)
        temp_path = ASSETS_DIR / "temp_display.png"
        resized_img.save(temp_path)
        st.image(str(temp_path), use_container_width=True)
        st.markdown('<div class="availability-tag">AVAILABLE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Card content
        st.markdown('<div class="card-content">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{event.get("name","Event Title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-desc">{event.get("description","Short description.")}</div>', unsafe_allow_html=True)
        
        # Details
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

# -------------------- Blockchain Ledger Display --------------------
if st.session_state.mode == "blockchain":
    st.markdown('<h2 class="section-title">Blockchain Ledger</h2>', unsafe_allow_html=True)
    ledger_records = get_ledger()
    for record in ledger_records:
        st.markdown(f'''
        <div class="ledger-card">
            <b>Event:</b> {record.get("event","")}<br>
            <b>First Name:</b> {record.get("first_name","")}<br>
            <b>Last Name:</b> {record.get("last_name","")}<br>
            <b>UID:</b> {record.get("uid","")}<br>
            <b>Tickets Bought:</b> {record.get("tickets",0)}<br>
            <b>Time:</b> {record.get("timestamp","")}<br>
            <b>Hash:</b> {record.get("hash","")}<br>
        </div>
        ''', unsafe_allow_html=True)

# -------------------- Footer --------------------
st.markdown(
    '<div class="footer">Ticket_Biz © 2025. Powered by <span>Blockchain Technology</span>.</div>',
    unsafe_allow_html=True
)
