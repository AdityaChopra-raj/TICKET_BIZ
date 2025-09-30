# app.py
import streamlit as st
from PIL import Image
from pathlib import Path
from events_data import EVENTS
from ledger import add_transaction, get_ledger, check_in, get_tickets_sold, get_checked_in
import hashlib

st.set_page_config(page_title="🎟 Ticket_Biz — Event Ticketing", page_icon="🎫", layout="wide")
ASSETS_DIR = Path(__file__).parent / "assets"

st.markdown("""
<style>
/* General */
body {
    background: linear-gradient(#0b0c10, #111418);
    color: #fff;
    font-family: 'Inter', sans-serif;
}
h1 {
    color: #e50914;
    font-size: 48px;
    text-align: center;
    margin-bottom: 10px;
}
h3 {
    color: #ddd;
    text-align: center;
    margin-bottom: 40px;
}
.footer {
    text-align:center;
    color:#888;
    padding:10px;
    border-top:1px solid #222;
}
.event-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(320px,1fr));
    gap: 20px;
    justify-items:center;
}
.event-card {
    background:#111418;
    border-radius:12px;
    width:320px;
    transition: 0.3s all;
    overflow:hidden;
}
.event-card:hover {
    box-shadow: 0 0 20px #e50914;
}
.event-card img {
    width:320px;
    height:180px;
    object-fit:cover;
}
.event-content {
    padding:15px;
}
.event-content h4 {
    margin:5px 0;
}
.event-content p {
    color:#bbb;
    font-size:14px;
    height:40px;
    overflow:hidden;
}
.event-details {
    font-size:13px;
    color:#ccc;
    margin-bottom:10px;
}
.book-btn, .check-btn {
    width:100%;
    background:#e50914;
    color:#fff;
    font-weight:bold;
    padding:10px;
    border:none;
    border-radius:6px;
    cursor:pointer;
}
.book-btn:hover, .check-btn:hover {
    background:#ff1a1a;
}
.available-tag {
    background:#16a34a;
    color:#fff;
    padding:3px 8px;
    border-radius:6px;
    display:inline-block;
    margin-bottom:5px;
    font-size:12px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# Tabs
tabs = ["Home", "Buy Ticket", "Check In", "Blockchain"]
tab_choice = st.tabs(tabs)
tab_home, tab_buy, tab_checkin, tab_blockchain = tab_choice

# HOME TAB
with tab_home:
    st.title("🎟 Ticket_Biz — Event Ticketing")
    st.subheader("Welcome! Book and manage your event tickets easily. Explore trending events and check in seamlessly.")

# UTILITY FUNCTIONS
def get_resized_image(img_path):
    img = Image.open(img_path)
    img = img.resize((320, 180))
    return img

def get_hash(record):
    """Generate SHA256 hash of a record dict"""
    record_str = "|".join([str(v) for v in record.values()])
    return hashlib.sha256(record_str.encode()).hexdigest()[:10]

def show_event_card(event, tab="buy"):
    tickets_left = event["total_tickets"] - get_tickets_sold(event["id"])
    checked_in = get_checked_in(event["id"])
    img_path = ASSETS_DIR / event["image"]
    img = get_resized_image(img_path)
    
    st.image(img, use_container_width=True)
    st.markdown(f'<div class="available-tag">{"AVAILABLE" if tickets_left>0 else "FULL"}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="event-content"><h4>{event["name"]}</h4>', unsafe_allow_html=True)
    st.markdown(f'<p>{event["description"]}</p>', unsafe_allow_html=True)
    st.markdown(f'''
    <div class="event-details">
    📅 {event["date_time"]} <br>
    📍 {event["venue"]} <br>
    🎟️ {tickets_left}/{event["total_tickets"]} tickets left <br>
    💰 From ₹{event["price"]}
    </div>
    ''', unsafe_allow_html=True)
    
    if tab=="buy" and tickets_left>0:
        buy_key = f"buy_{event['id']}"
        if st.button("Buy Ticket", key=buy_key):
            with st.form(f"form_{event['id']}"):
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                student_id = st.text_input("Student ID")
                email = st.text_input("Email")
                num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=min(15,tickets_left))
                submitted = st.form_submit_button("Confirm Purchase")
                if submitted:
                    if first_name and last_name and student_id and email and num_tickets>0:
                        add_transaction(event["id"], event["name"], first_name, last_name, student_id, email, int(num_tickets))
                        st.success(f"Successfully purchased {int(num_tickets)} ticket(s)!")
                    else:
                        st.error("Please fill all fields correctly.")
    
    elif tab=="checkin":
        check_key = f"check_{event['id']}"
        if st.button("Check In", key=check_key):
            with st.form(f"check_form_{event['id']}"):
                student_id = st.text_input("Student ID")
                email = st.text_input("Email")
                num_checkin = st.number_input("Number of people checking in", min_value=1, max_value=5)
                submitted = st.form_submit_button("Confirm Check-In")
                if submitted:
                    if student_id and email:
                        check_in((student_id,email), tickets_to_check_in=num_checkin)
                        st.success(f"Checked in {num_checkin} attendee(s)!")
                    else:
                        st.error("Please enter valid Student ID and Email.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

# BUY TICKET TAB
with tab_buy:
    st.header("Trending Events")
    for event in EVENTS:
        show_event_card(event, tab="buy")

# CHECK IN TAB
with tab_checkin:
    st.header("Check In Events")
    for event in EVENTS:
        show_event_card(event, tab="checkin")

# BLOCKCHAIN TAB
with tab_blockchain:
    st.header("Blockchain Ledger")
    ledger = get_ledger()
    for record in ledger:
        st.markdown(f'''
        <div class="event-card" style="width:320px; padding:10px; margin-bottom:10px;">
            <b>Event:</b> {record['event_name']}<br>
            <b>Name:</b> {record['first_name']} {record['last_name']}<br>
            <b>Student ID:</b> {record['student_id']}<br>
            <b>Email:</b> {record['email']}<br>
            <b>Tickets:</b> {record['num_tickets']}<br>
            <b>Checked In:</b> {record['num_checked_in']}<br>
            <b>Hash:</b> {get_hash(record)}
        </div>
        ''', unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="footer">Ticket_Biz © 2025. Powered by Blockchain Technology</div>', unsafe_allow_html=True)
