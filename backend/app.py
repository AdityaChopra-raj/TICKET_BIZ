import streamlit as st
from events_data import events as EVENTS_DATA
from verify_ticket import verify_ticket
from PIL import Image
import os

# Page config
st.set_page_config(page_title="Event Ticketing System", layout="wide")

# Inject custom CSS for hover effects & button transitions
st.markdown("""
<style>
/* Card hover effect */
.card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    padding: 10px;
    margin-bottom: 20px;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
}

/* Button style and hover */
.stButton>button {
    background-color: #e50914;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-size: 16px;
    font-weight: bold;
    transition: transform 0.2s ease, background-color 0.2s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    background-color: #f6121d;
}

/* Progress bar customization */
[data-testid="stProgressBar"] > div > div > div {
    background-color: #e50914 !important;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎫 Event Ticketing System")

# Event selection dropdown
event_names = [event['name'] for event in EVENTS_DATA]
selected_event = st.selectbox("Select Event", event_names)

# Event card with image and stats
event_obj = next((e for e in EVENTS_DATA if e["name"] == selected_event), None)
if event_obj:
    if os.path.exists(event_obj["image"]):
        img = Image.open(event_obj["image"])
        st.image(img, use_column_width=True)

    st.markdown(f"""
    <div class="card">
        <h3>{selected_event}</h3>
        <p>Tickets Scanned: {event_obj['tickets_scanned']} / {event_obj['total_tickets']}</p>
    </div>
    """, unsafe_allow_html=True)

# Ticket input
ticket_id = st.text_input("Enter Ticket ID or Scan QR")

# Verify button
if st.button("Verify Ticket"):
    if not ticket_id:
        st.warning("Please enter a Ticket ID")
    else:
        valid, message = verify_ticket(ticket_id, selected_event, EVENTS_DATA)
        if valid:
            st.success(message)
        else:
            st.error(message)

# Progress bar for ticket scanning
if event_obj:
    progress_value = event_obj["tickets_scanned"]/event_obj["total_tickets"]
    st.progress(progress_value)

# Footer
st.markdown("---")
st.markdown("© 2025 Event Ticketing System | Streamlit Version ✅")
