
---

## 📄 `backend/app.py`
```python
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Paths
DATA_DIR = "backend/data"
ASSETS_DIR = "backend/assets"

EVENTS_FILE = os.path.join(DATA_DIR, "events.csv")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.csv")
LEDGER_FILE = os.path.join(DATA_DIR, "ledger.csv")
STYLE_FILE = os.path.join("backend", "style.css")

# Load CSS
with open(STYLE_FILE) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
events_df = pd.read_csv(EVENTS_FILE)
tickets_df = pd.read_csv(TICKETS_FILE)
ledger_df = pd.read_csv(LEDGER_FILE)

# Page title
st.markdown("<h1 style='text-align:center; margin-bottom:30px;'>🎉 Trending Events</h1>", unsafe_allow_html=True)

# Layout for event cards
st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)

for idx, row in events_df.iterrows():
    event_id = row["id"]
    name = row["name"]
    desc = row["description"]
    date = row["date"]
    location = row["location"]
    tickets_left = row["tickets_left"]
    price = row["price"]
    image = os.path.join(ASSETS_DIR, row["image"])

    # Card
    st.markdown(f"""
    <div class="card">
        <img src="{image}" alt="{name}">
        <div class="badge">Available</div>
        <div class="card-content">
            <h3>{name}</h3>
            <p>{desc[:100]}...</p>
            <div class="details">
                <span>📅 {date}</span>
                <span>📍 {location}</span>
                <span>🎟️ {tickets_left} tickets left</span>
                <span>💰 {price}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Booking button
    if st.button(f"Book Now ({name})", key=event_id, help="Reserve your ticket"):
        if tickets_left > 0:
            # Update tickets
            events_df.loc[events_df["id"] == event_id, "tickets_left"] -= 1
            events_df.to_csv(EVENTS_FILE, index=False)

            # Add to tickets file
            new_ticket = {"event_id": event_id, "timestamp": datetime.now()}
            tickets_df = pd.concat([tickets_df, pd.DataFrame([new_ticket])], ignore_index=True)
            tickets_df.to_csv(TICKETS_FILE, index=False)

            # Add to ledger
            new_ledger = {"event_id": event_id, "status": "booked", "timestamp": datetime.now()}
            ledger_df = pd.concat([ledger_df, pd.DataFrame([new_ledger])], ignore_index=True)
            ledger_df.to_csv(LEDGER_FILE, index=False)

            st.success(f"🎟️ Ticket booked for {name}!")
        else:
            st.error("❌ No tickets left for this event.")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p><strong>Ticket_Biz</strong> © 2025. All rights reserved.<br>
    Powered by Blockchain Technology | Developer Use Only</p>
</div>
""", unsafe_allow_html=True)
