from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"

EVENTS = [
    {
        "id": "navratri",
        "name": "Navratri Pooja",
        "description": "Celebrate Navratri with devotion and music.",
        "date": "2025-10-10 18:00",
        "location": "Community Hall, Ludhiana",
        "price": 299,
        "total_tickets": 150,
        "image": ASSETS_DIR / "navratri.jpeg.avif",
    },
    {
        "id": "diwali",
        "name": "Diwali Dance Night",
        "description": "A night of lights, dance and celebration.",
        "date": "2025-11-12 20:00",
        "location": "City Club, Ludhiana",
        "price": 399,
        "total_tickets": 200,
        "image": ASSETS_DIR / "diwali.jpeg",
    },
    {
        "id": "freshers",
        "name": "Freshers Bash",
        "description": "Welcome party for all freshers!",
        "date": "2025-10-20 19:00",
        "location": "University Auditorium",
        "price": 199,
        "total_tickets": 120,
        "image": ASSETS_DIR / "freshers.jpeg",
    },
    {
        "id": "ravan",
        "name": "Ravan Dahan",
        "description": "Witness the grand Dussehra celebration.",
        "date": "2025-10-24 18:30",
        "location": "Main Ground",
        "price": 99,
        "total_tickets": 500,
        "image": ASSETS_DIR / "ravan.jpeg",
    },
    {
        "id": "club",
        "name": "Club Night",
        "description": "DJ, drinks and dance till late!",
        "date": "2025-12-31 21:00",
        "location": "Downtown Club",
        "price": 499,
        "total_tickets": 100,
        "image": ASSETS_DIR / "club.jpeg",
    },
]
