import streamlit as st
from events_data import events
from verify_ticket import verify_ticket
from utils import get_event_stats

st.set_page_config(page_title='Event Ticketing System', layout='wide')
st.title('🎟️ Event Ticketing System')

# Event Selection
event_name = st.selectbox('Select Event', list(events.keys()))
st.image(events[event_name]['image'], use_column_width=True)

# Show stats
stats = get_event_stats(event_name, events)
st.metric(label='Total Tickets', value=stats['total'])
st.metric(label='Tickets Scanned', value=stats['scanned'])
st.metric(label='Tickets Remaining', value=stats['remaining'])

# Ticket QR/ID input
ticket_id = st.text_input('Enter Ticket ID / Scan QR')

if 'scanned_tickets_db' not in st.session_state:
    st.session_state.scanned_tickets_db = set()

if st.button('Verify Ticket'):
    if ticket_id:
        valid, msg = verify_ticket(event_name, ticket_id, st.session_state.scanned_tickets_db)
        if valid:
            st.success(msg)
        else:
            st.error(msg)
    else:
        st.warning('Please enter a Ticket ID or scan QR.')
