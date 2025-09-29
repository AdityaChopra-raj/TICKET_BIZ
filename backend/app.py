import streamlit as st
from events_data import events as EVENTS_DATA
from PIL import Image
import json
import os

# Optional blockchain imports
from blockchain import (
    init_web3,
    make_ticket_hash,
    load_contract,
    store_hash_on_chain
)

# ---------------- Page Config ---------------- #
st.set_page_config(page_title="🎟 Event Ticketing", layout="wide")
st.title("🎬 Blockchain-Backed Event Ticketing System")

st.markdown(
    """
    **Welcome!**  
    Verify your ticket for any of our events below.  
    If enabled, a cryptographic hash of your ticket will also be written to the blockchain.
    """,
    unsafe_allow_html=True
)

# -------------- Sidebar & Blockchain Setup -------------- #
use_blockchain = st.sidebar.checkbox("Enable blockchain logging", value=False)

w3 = None
contract = None
blockchain_ready = False

if use_blockchain:
    try:
        RPC_URL = st.secrets["RPC_URL"]
        PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
        ACCOUNT_ADDRESS = st.secrets["ACCOUNT_ADDRESS"]
        CHAIN_ID = int(st.secrets["CHAIN_ID"])
        CONTRACT_ADDRESS = st.secrets["CONTRACT_ADDRESS"]
        CONTRACT_ABI = json.loads(st.secrets["CONTRACT_ABI_JSON"])

        w3 = init_web3(RPC_URL)
        contract = load_contract(w3, CONTRACT_ADDRESS, CONTRACT_ABI)
        blockchain_ready = True
        st.sidebar.success("Blockchain connection ready ✅")
    except Exception as e:
        st.sidebar.error(f"Blockchain initialisation failed: {e}")
        use_blockchain = False

# -------------- Event Selection -------------- #
event_names = [event["name"] for event in EVENTS_DATA]
selected_event_name = st.selectbox("Select Event", event_names)

selected_event = next(e for e in EVENTS_DATA if e["name"] == selected_event_name)

# Display event banner
try:
    event_image = Image.open(selected_event["image"])
    st.image(event_image, use_container_width=True)  # 16:9 images recommended
except Exception as e:
    st.warning(f"Image not found for {selected_event_name}: {e}")

# Display stats
total_tickets = len(selected_event["tickets"])
scanned_count = len(selected_event["scanned_tickets"])
remaining = total_tickets - scanned_count

st.markdown(
    f"""
    **Stats**  
    * Total tickets: `{total_tickets}`  
    * Tickets already scanned: `{scanned_count}`  
    * Tickets remaining: `{remaining}`
    """
)

# -------------- Ticket Verification -------------- #
ticket_number = st.text_input("Enter Ticket Number to verify")

if st.button("Verify Ticket"):
    if not ticket_number.strip():
        st.error("Please enter a ticket number.")
    else:
        ticket_number = ticket_number.strip().upper()
        if ticket_number in selected_event["tickets"]:
            if ticket_number in selected_event["scanned_tickets"]:
                st.warning("⚠️ Ticket already scanned.")
            else:
                # Mark ticket as scanned
                selected_event["scanned_tickets"].append(ticket_number)
                st.success("✅ Ticket verified successfully!")

                # Optional: store hash on blockchain
                if use_blockchain and blockchain_ready:
                    try:
                        ticket_hash = make_ticket_hash(ticket_number, selected_event_name)
                        tx_hash = store_hash_on_chain(
                            w3,
                            contract,
                            ACCOUNT_ADDRESS,
                            PRIVATE_KEY,
                            ticket_hash,
                            CHAIN_ID
                        )
                        st.info(f"Ticket hash stored on chain.\n\n**Tx hash:** {tx_hash}")
                    except Exception as e:
                        st.error(f"Blockchain transaction failed: {e}")
        else:
            st.error("❌ Invalid ticket number.")

# -------------- Email Notice -------------- #
st.markdown("---")
try:
    EMAIL_ADDRESS = st.secrets["email"]["address"]
    st.info(f"Email features enabled. Tickets can be sent from {EMAIL_ADDRESS}")
except Exception:
    st.warning("Email credentials not found. Email features are disabled.")

# -------------- Footer -------------- #
st.markdown(
    """
    <hr/>
    <small>© 2025 Event Ticketing Blockchain Demo. All rights reserved.</small>
    """,
    unsafe_allow_html=True
)
