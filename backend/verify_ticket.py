def verify_ticket(ticket_id, selected_event, events_list):
    """
    Simple verification: checks if ticket_id is numeric and updates scanned count
    """
    if not ticket_id.isdigit():
        return False, "Invalid Ticket ID"
    
    for event in events_list:
        if event["name"] == selected_event:
            if event["tickets_scanned"] < event["total_tickets"]:
                event["tickets_scanned"] += 1
                return True, "Ticket verified successfully"
            else:
                return False, "All tickets for this event have been scanned"
    return False, "Event not found"
