import csv, uuid
from pathlib import Path
from PIL import Image, ImageDraw
import streamlit as st
from events_data import EVENTS
from ledger import add_block, read_ledger

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
TICKETS_CSV = BASE_DIR / "tickets.csv"

st.set_page_config(page_title="Ticket_Biz", layout="wide")

# Load CSS safely
with open(BASE_DIR / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="header-title">🎟 Ticket_Biz — Event Ticketing</h1>', unsafe_allow_html=True)

# --- Utilities ---
def generate_uid():
    return str(uuid.uuid4())[:8]

def save_ticket(uid, first, last, email, event):
    write_header = not TICKETS_CSV.exists()
    with open(TICKETS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["uid","first","last","email","event","checked_in"])
        if write_header:
            writer.writeheader()
        writer.writerow({
            "uid": uid, "first": first, "last": last,
            "email": email, "event": event, "checked_in": False
        })

def check_in_count(event_name):
    if not TICKETS_CSV.exists():
        return 0
    with open(TICKETS_CSV) as f:
        return sum(1 for r in csv.DictReader(f) if r["event"]==event_name and r["checked_in"]=="True")

if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

# --- Event Grid ---
st.markdown('<div class="grid-container">', unsafe_allow_html=True)

for ev in EVENTS:
    is_full = ev["tickets_left"] <= 0
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Safe image loading
    img_path = ASSETS_DIR / ev["image"]
    if img_path.exists():
        img = Image.open(img_path)
    else:
        img = Image.new("RGB",(1280,720),color=(30,30,30))
        d = ImageDraw.Draw(img)
        d.text((50,50),"No Image Available",fill=(200,200,200))
    st.image(img, use_container_width=True)

    badge_color = "#16a34a" if not is_full else "#ff0000"
    badge_text = "Available" if not is_full else "Full"
    st.markdown(f'<div class="status-badge" style="background:{badge_color}">{badge_text}</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-content">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{ev["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-desc">{ev["desc"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-details">', unsafe_allow_html=True)
    st.markdown(f'<span>📅 {ev["date"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<span>📍 {ev["location"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<span>🎟️ Tickets left: <span class="important">{ev["tickets_left"]}</span></span>', unsafe_allow_html=True)
    st.markdown(f'<span>👥 Checked in: {check_in_count(ev["name"])}</span>', unsafe_allow_html=True)
    st.markdown(f'<span>💰 Price: ₹{ev["price"]}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Book Now", key=f"buy_{ev['name']}") and not is_full:
        st.session_state["selected_event"] = ev["name"]

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Purchase Form ---
if st.session_state["selected_event"]:
    sel = next(e for e in EVENTS if e["name"]==st.session_state["selected_event"])
    st.subheader(f"Booking: {sel['name']}")
    with st.form("purchase_form"):
        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        email = st.text_input("Email")
        qty = st.number_input("Number of Tickets (Max 15)", min_value=1, max_value=15, value=1)
        submitted = st.form_submit_button("Confirm Purchase")
        if submitted:
            if sel["tickets_left"] >= qty:
                for _ in range(qty):
                    uid = generate_uid()
                    save_ticket(uid, first, last, email, sel["name"])
                    add_block(uid, first, last, "buy")
                sel["tickets_left"] -= qty
                st.success(f"{qty} ticket(s) purchased successfully!")
            else:
                st.error("Not enough tickets available!")
            st.session_state["selected_event"] = None

# --- Ledger Display ---
st.subheader("🔗 Blockchain Ledger")
ledger = read_ledger()
if ledger:
    st.dataframe(ledger, use_container_width=True)
else:
    st.write("Ledger is empty.")
