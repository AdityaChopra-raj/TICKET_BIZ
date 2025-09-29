import os
BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'assets')
events = {
    'Navratri Pooja': {'total_tickets':100,'scanned_tickets':0,'image':os.path.join(BASE_IMAGE_PATH,'navratri.jpeg')},
    'Diwali Dance': {'total_tickets':150,'scanned_tickets':0,'image':os.path.join(BASE_IMAGE_PATH,'diwali.jpeg')},
    'Freshers': {'total_tickets':200,'scanned_tickets':0,'image':os.path.join(BASE_IMAGE_PATH,'freshers.jpeg')},
    'Ravan Dehan': {'total_tickets':120,'scanned_tickets':0,'image':os.path.join(BASE_IMAGE_PATH,'ravan_dehan.jpeg')}
}