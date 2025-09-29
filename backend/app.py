import streamlit as st
from PIL import Image
import os
from events_data import events as EVENTS_DATA

st.set_page_config(page_title="Event Ticketing", layout="wide")

# Load CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"CSS file not loaded: {e}")

local_css("styles/style.css")

# Load email credentials safely
try:
    EMAIL_ADDRESS = st.secrets["email"]["address"]
    EMAIL_PASSWORD = st.secrets["email"]["password"]
except KeyError:
    EMAIL_ADDRESS = None
    EMAIL_PASSWORD = None
    st.warning("Email credentials not found. Email features disabled.")

# Helper function to safely load images
def load_image(path, fallback="assets/placeholder.jpeg"):
    try:
        return Image.open(path)
    except Exception as e:
        st.error(f"Failed to load image: {path}. Using placeholder.")
        try:
            return Image.open(fallback)
        except:
            return None

# --- UI --- #
st.title("🎬 Event Ticketing System")
st.subheader("Scan and Verify Tickets Easily")

# Event selection dropdown
event_names = [event["name"] for event in EVENTS_DATA]
selected_event = st.selectbox("Select Event", event_names)

# Display event image
event_image_path = next((event["image"] for event in EVENTS_DATA if event["name"] == selected_event), None)
img = load_image(event_image_path)
if img:
    st.image(img, use_container_width=True)

# Ticket input
ticket_number = st.text_input("Enter Ticket Number", placeholder="e.g., NAV001")

# Verify ticket button inside a card
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("Verify Ticket"):
        if not ticket_number.strip():
            st.error("Please enter a ticket number.")
        else:
            try:
                event = next((e for e in EVENTS_DATA if e["name"] == selected_event), None)
                if ticket_number in event["tickets"]:
                    if ticket_number in event["scanned_tickets"]:
                        st.warning("This ticket has already been scanned.")
                    else:
                        event["scanned_tickets"].append(ticket_number)
                        st.success("✅ Ticket Verified Successfully!")
                else:
                    st.error("Ticket not found for this event.")
            except Exception as e:
                st.error(f"Error during verification: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# Display event stats in cards
st.markdown("### 📊 Event Ticket Stats")
try:
    for event in EVENTS_DATA:
        scanned = len(event.get("scanned_tickets", []))
        total = len(event.get("tickets", []))
        st.markdown(f'<div class="card">{event["name"]}: {scanned}/{total} tickets scanned</div>', unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading stats: {e}")
