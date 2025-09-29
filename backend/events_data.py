import os

BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets")

events = [
    {
        "name": "Navratri Pooja",
        "total_tickets": 100,
        "tickets_scanned": 0,
        "image": os.path.join(BASE_IMAGE_PATH, "navratri.jpeg")
    },
    {
        "name": "Diwali Dance",
        "total_tickets": 150,
        "tickets_scanned": 0,
        "image": os.path.join(BASE_IMAGE_PATH, "diwali.jpeg")
    },
    {
        "name": "Freshers",
        "total_tickets": 200,
        "tickets_scanned": 0,
        "image": os.path.join(BASE_IMAGE_PATH, "freshers.jpeg")
    },
    {
        "name": "Ravan Dehan",
        "total_tickets": 80,
        "tickets_scanned": 0,
        "image": os.path.join(BASE_IMAGE_PATH, "ravan_dehan.jpeg")
    }
]
