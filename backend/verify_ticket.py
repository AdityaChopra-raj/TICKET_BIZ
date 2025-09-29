from events_data import events
def verify_ticket(event_name, ticket_id, scanned_tickets_db):
    if ticket_id in scanned_tickets_db:
        return False, 'Ticket already scanned!'
    if ticket_id.startswith(event_name[:3].upper()):
        scanned_tickets_db.add(ticket_id)
        events[event_name]['scanned_tickets'] += 1
        return True, 'Ticket verified successfully!'
    return False, 'Invalid ticket!'