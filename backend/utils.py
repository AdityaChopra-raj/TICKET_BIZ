def get_event_stats(event_name, events):
    total = events[event_name]['total_tickets']
    scanned = events[event_name]['scanned_tickets']
    remaining = total - scanned
    return {'total': total, 'scanned': scanned, 'remaining': remaining}