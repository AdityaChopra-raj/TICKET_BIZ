import os
BASE_IMAGE_PATH = "assets"
events = [
    {
        "name": "Navratri Pooja",
        "image": os.path.join(BASE_IMAGE_PATH, "navratri.jpeg"),
        "tickets": [f"NAV{str(i).zfill(3)}" for i in range(1, 101)],
        "scanned_tickets": []
    },
    {
        "name": "Diwali Dance",
        "image": os.path.join(BASE_IMAGE_PATH, "diwali.jpeg"),
        "tickets": [f"DIA{str(i).zfill(3)}" for i in range(1, 101)],
        "scanned_tickets": []
    },
    {
        "name": "Freshers",
        "image": os.path.join(BASE_IMAGE_PATH, "freshers.jpeg"),
        "tickets": [f"FRE{str(i).zfill(3)}" for i in range(1, 101)],
        "scanned_tickets": []
    },
    {
        "name": "Ravan Dehan",
        "image": os.path.join(BASE_IMAGE_PATH, "ravan.jpeg"),
        "tickets": [f"RAV{str(i).zfill(3)}" for i in range(1, 101)],
        "scanned_tickets": []
    },
]
