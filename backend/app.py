import streamlit as st
from events_data import get_events
from ledger import Ledger

# Page configuration
st.set_page_config(page_title="Event Ledger App", layout="wide")
st.title("🎉 Event Ledger Dashboard")

# Apply custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------
# Events Section
# -------------------------
st.header("Upcoming Events")
events = get_events()

# Grid layout for events
st.markdown('<div class="event-grid">', unsafe_allow_html=True)
for event in events:
    card_html = f"""
    <div class="event-card">
        <img src="assets/{event['image']}" alt="{event['title']}">
        <h3>{event['title']}</h3>
        <p>{event['description']}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Ledger Section
# -------------------------
st.header("Ledger")
ledger = Ledger()

# Ledger container
st.markdown('<div class="ledger-section">', unsafe_allow_html=True)
st.subheader("Current Balance")
st.write("₹", ledger.get_balance())

# Display existing transactions
st.subheader("Transactions")
transactions = ledger.get_transactions()
if not transactions.empty:
    st.dataframe(transactions)
else:
    st.info("No transactions added yet.")

# Add Transaction Form
st.subheader("Add Transaction")
with st.form("transaction_form"):
    date = st.date_input("Date")
    desc = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    type_ = st.selectbox("Type", ["Credit", "Debit"])
    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        ledger.add_transaction(date, desc, amount, type_)
        st.success("Transaction added successfully!")
        st.experimental_rerun()  # Refresh page to show new transaction
st.markdown('</div>', unsafe_allow_html=True)
