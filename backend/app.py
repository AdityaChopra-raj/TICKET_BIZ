import streamlit as st
from PIL import Image
from pathlib import Path
import time
from datetime import datetime
import hashlib # For Hashing / 'Blockchain' simulation

# --- Import Custom Modules ---
from ledger import add_transaction, get_ledger, get_tickets_sold, update_checkin_status
from events_data import EVENTS
from email_utils import send_email

# --- Configuration ---
ASSETS_DIR = Path(__file__).parent / "assets"
MAX_TICKETS_PER_PURCHASE = 15

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Ticket_Biz",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Initial Session State ---
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Home"
if 'checkin_record' not in st.session_state:
    st.session_state.checkin_record = None # Stores found record during check-in flow

# --- CSS Styling (Ensure styles.css is present) ---
try:
    with open(Path(__file__).parent / "styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("styles.css not found. The app will use default styles.")

# --- Utility Functions ---

def get_resized_image(img_name, width=320, height=180):
    """Opens and optionally resizes an image from the assets directory."""
    img_path = ASSETS_DIR / img_name
    try:
        img = Image.open(img_path)
        return img.resize((width, height))
    except FileNotFoundError:
        # Fallback to a placeholder image if needed
        # Assuming 'placeholder.jpg' is available in assets/
        placeholder_path = ASSETS_DIR / "placeholder.jpg"
        if placeholder_path.exists():
             return Image.open(placeholder_path).resize((width, height))
        return None 

def get_current_events():
    """Filters out events that have already passed."""
    now = datetime.now()
    return [
        event for event in EVENTS 
        if datetime.strptime(event["date"].split()[0], "%Y-%m-%d") >= now
    ]

CURRENT_EVENTS = get_current_events()

def update_selected_event(event_id, tab_name):
    """Updates session state and tab on button click."""
    st.session_state.selected_event = event_id
    st.session_state.active_tab = tab_name
    st.session_state.checkin_record = None # Reset checkin record when switching event
    st.rerun()

def show_event_card(event, tab_name, idx):
    """Renders a single event card with buttons."""
    
    tickets_sold = get_tickets_sold(event["id"])
    available = event["total_tickets"] - tickets_sold
    
    tag_class = "available-tag" if available > 0 else "sold-out-tag"
    tag_text = f"Available: {available}" if available > 0 else "SOLD OUT"

    button_text = "BUY TICKET" if tab_name == "buy" else "CHECK-IN"
    action_tab = "Buy Ticket" if tab_name == "buy" else "Check-In"
    
    # Image data base64 embedding (optimized for speed)
    img_data_key = f"img_data_{idx}"
    if img_data_key not in st.session_state:
        img_object = get_resized_image(event["image"])
        if img_object:
            import base64
            from io import BytesIO
            buffered = BytesIO()
            img_object.save(buffered, format="JPEG")
            st.session_state[img_data_key] = base64.b64encode(buffered.getvalue()).decode()
        else:
            st.session_state[img_data_key] = "" # Fallback

    card_html = f"""
    <div class='event-card'>
        <img src='data:image/jpeg;base64,{st.session_state.get(img_data_key)}' alt='{event["name"]}'>
        <div style="padding: 10px;">
            <div class="{tag_class}">{tag_text}</div>
            <h3 style="margin: 5px 0 0 0; color:#e50914;">{event["name"]}</h3>
            <p style="margin: 0; color:#bbb; font-size:14px;">{event["date"]}</p>
            <p style="margin: 5px 0; color:#eee;">{event["venue"]}</p>
            <p style="margin: 0 0 10px 0; font-weight:bold;">Price: {event["price"]}</p>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Button placement (with hover effect from styles.css)
    if available > 0 or tab_name == "checkin":
        st.button(
            button_text, 
            key=f"{tab_name}_btn_{event['id']}", 
            on_click=update_selected_event, 
            args=(event["id"], action_tab)
        )
    else:
         st.button("SOLD OUT", key=f"{tab_name}_btn_sold_{event['id']}", disabled=True)


# --- Tab Definition ---
tabs = st.tabs(["Home", "Buy Ticket", "Check-In", "Logs"]) # Logs replaces Blockchain
home_tab, buy_tab, checkin_tab, logs_tab = tabs

# Manually control which tab is active 
try:
    active_index = ["Home", "Buy Ticket", "Check-In", "Logs"].index(st.session_state.active_tab)
    # Using a minor hack to control active tab after rerun
    st.session_state["st_tab_idx"] = active_index 
except:
    st.session_state["st_tab_idx"] = 0 


# --- Home Tab Content ---
with home_tab:
    st.markdown("<div class='home-section'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#e50914;font-size:48px;'>🎟 Ticket_Biz — Event Ticketing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb;font-size:18px;'>Welcome to Ticket_Biz! Purchase your tickets and manage check-ins using our secure, hash-verified platform.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- Buy Ticket Tab Content ---
with buy_tab:
    st.subheader("Upcoming Events")
    
    selected_id = st.session_state.get("selected_event")
    event_to_buy = next((e for e in CURRENT_EVENTS if e["id"] == selected_id), None)
    
    if event_to_buy and st.session_state.active_tab == "Buy Ticket":
        
        tickets_sold = get_tickets_sold(event_to_buy["id"])
        available = event_to_buy["total_tickets"] - tickets_sold
        
        st.subheader(f"Purchase Tickets for: {event_to_buy['name']}")
        st.markdown("---")
        
        with st.form("purchase_form"):
            st.write("Customer Details:")
            col_first, col_last = st.columns(2)
            first_name = col_first.text_input("First Name", key="buy_first_name")
            last_name = col_last.text_input("Last Name", key="buy_last_name")
            
            col_email, col_phone = st.columns(2)
            email = col_email.text_input("Email Address", key="buy_email")
            phone = col_phone.text_input("Phone Number", key="buy_phone")
            
            num_tickets = st.number_input(
                "Number of Tickets to Buy", 
                min_value=1, 
                max_value=min(MAX_TICKETS_PER_PURCHASE, available), 
                value=1
            )
            
            submitted = st.form_submit_button("COMPLETE PURCHASE", type="primary")
            
            if submitted:
                required_fields = [first_name, last_name, email, phone]
                if all(required_fields) and num_tickets <= available:
                    
                    # 1. Generate Blockchain Hash and UID
                    timestamp = time.time()
                    data_to_hash = f"{event_to_buy['id']}|{email.lower()}|{phone}|{num_tickets}|{timestamp}"
                    hash_value = hashlib.sha256(data_to_hash.encode()).hexdigest()
                    uid = hash_value[:10].upper() # Ticket_ID
                    
                    # 2. Add to Ledger (Simulates Block creation)
                    add_transaction(
                        event_to_buy["id"], event_to_buy["name"], first_name, last_name, 
                        email, phone, uid, hash_value, num_tickets
                    )
                    
                    # 3. Send Email
                    email_content = f"""
                    Dear {first_name} {last_name},
                    
                    Thank you for your purchase!
                    Event: {event_to_buy['name']}
                    Tickets Purchased: {num_tickets}
                    
                    Your unique Ticket ID (UID) for check-in is: {uid}
                    Your Phone Number: {phone}
                    
                    Transaction Hash (Proof of Purchase): {hash_value}
                    """
                    # st.success is shown inside email_utils.py after successful send
                    send_email(email, f"Ticket Confirmation: {event_to_buy['name']} | UID: {uid}", email_content)
                    
                    # 4. Final Success Message
                    st.success(f"🥳 Purchase Successful! Your Ticket UID is: **{uid}**.")
                    
                    # Reset state and switch to Logs tab
                    st.session_state.selected_event = None
                    st.session_state.active_tab = "Logs" 
                    st.rerun()

                elif num_tickets > available:
                    st.error("Purchase failed: Not enough tickets available.")
                else:
                    st.error("Please fill in all required fields (Name, Email, Phone).")
    
    else:
        # --- SHOW EVENT CARDS ---
        st.markdown("<div class='event-grid'>", unsafe_allow_html=True)
        cols = st.columns(3) 
        for idx, event in enumerate(CURRENT_EVENTS):
            with cols[idx % 3]:
                show_event_card(event, "buy", idx)
        st.markdown("</div>", unsafe_allow_html=True)


# --- Check-In Tab Content ---
with checkin_tab:
    st.subheader("Check-In Attendees")
    
    selected_id = st.session_state.get("selected_event")
    event_to_checkin = next((e for e in CURRENT_EVENTS if e["id"] == selected_id), None)
    
    if event_to_checkin and st.session_state.active_tab == "Check-In":
        # --- SHOW CHECK-IN FORM (Search by 3 fields) ---
        st.subheader(f"Check-In for: {event_to_checkin['name']}")
        
        with st.form("checkin_form_main"):
            st.write("Enter **ONE** of the following credentials to find the ticket:")
            uid_input = st.text_input("Ticket UID", key="checkin_uid_input")
            email_input = st.text_input("Customer Email", key="checkin_email_input")
            phone_input = st.text_input("Phone Number", key="checkin_phone_input")
            
            search_button = st.form_submit_button("Search Ticket", type="secondary")
            
            if search_button:
                st.session_state.checkin_record = None
                
                ledger = get_ledger()
                
                # Search Logic: Check by UID, Email, OR Phone for the selected event
                match = next((
                    r for r in ledger 
                    if str(r.get("event_id")) == str(event_to_checkin["id"]) and 
                       ((r.get("uid", "").upper() == uid_input.upper() if uid_input else False) or
                        (r.get("email", "").lower() == email_input.lower() if email_input else False) or
                        (r.get("phone") == phone_input if phone_input else False))
                ), None)

                if match:
                    checked_in = match.get("checked_in", 0)
                    total_purchased = match["num_tickets"]
                    
                    if checked_in >= total_purchased:
                         st.error("Check-In failed: All tickets for this transaction have already been checked in.")
                    else:
                        st.session_state.checkin_record = match
                        st.success(f"Ticket Found! Purchased: {total_purchased}, Checked In: {checked_in}. Ready for check-in.")
                else:
                    st.error("Ticket not found or does not match this event.")

            # --- PARTIAL CHECK-IN FORM (Only visible after successful search) ---
            if st.session_state.get("checkin_record"):
                record = st.session_state.checkin_record
                available_to_checkin = record["num_tickets"] - record.get("checked_in", 0)
                
                st.markdown("---")
                st.write(f"**Transaction:** {record['first_name']} {record['last_name']} ({record['uid']})")
                st.write(f"**Remaining Check-ins Allowed:** {available_to_checkin}")

                # This allows partial check-in (e.g., 3 of 10 tickets)
                num_checkin = st.number_input(
                    "Number of People Checking In Now", 
                    min_value=1, 
                    max_value=available_to_checkin, 
                    value=min(1, available_to_checkin),
                    key="partial_checkin_num"
                )
                
                confirm_checkin = st.form_submit_button("Confirm Final Check-In", type="primary")

                if confirm_checkin:
                    # 1. Update Ledger 
                    update_checkin_status(record["uid"], num_checkin)
                    
                    # 2. Success Message
                    new_remaining = available_to_checkin - num_checkin
                    
                    st.success(f"✅ Check-In Successful! **{num_checkin}** attendee(s) checked in. Remaining tickets: **{new_remaining}**.")
                    
                    # Reset state
                    st.session_state.checkin_record = None
                    st.session_state.selected_event = None
                    st.session_state.active_tab = "Check-In"
                    st.rerun()
            
    else:
        # --- SHOW EVENT CARDS ---
        st.markdown("<div class='event-grid'>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, event in enumerate(CURRENT_EVENTS):
            with cols[idx % 3]:
                show_event_card(event, "checkin", idx)
        st.markdown("</div>", unsafe_allow_html=True)


# --- Logs Tab Content ---
with logs_tab:
    st.subheader("Transaction Logs (Hash Verification)")
    st.info("Every purchase is recorded with an SHA-256 Hash and number of tickets sold. This simulates a secure, verifiable log.")
    ledger = get_ledger()
    if ledger:
        for record in reversed(ledger):
            color = "#00cc66" 
            
            st.markdown(
                f"""
                <div class='ledger-card' style='border-left: 5px solid {color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='font-weight: bold; color: {color};'>TRANSACTION LOG</span>
                        <span style='color: #888;'>Tickets Used: {record.get('checked_in', 0)} / {record.get('num_tickets')}</span>
                    </div>
                    <b>Event:</b> {record.get('event_name')}<br>
                    <b>Customer:</b> {record.get('first_name')} {record.get('last_name')} ({record.get('email')})<br>
                    <b>Tickets Purchased:</b> {record.get('num_tickets')}<br>
                    <b>UID:</b> {record.get('uid')}<br>
                    <span style='color: #888; word-break: break-all;'><b>Hash (SHA-256):</b> {record.get('hash', 'N/A')}</span>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.info("The transaction log is currently empty.")

# --- Footer ---
st.markdown("<div class='footer'>Ticket_Biz App | All Rights Reserved.</div>", unsafe_allow_html=True)
