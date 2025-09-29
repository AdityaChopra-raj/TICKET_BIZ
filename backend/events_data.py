from pathlib import Path

# -------------------- Assets Directory --------------------
ASSETS_DIR = Path(__file__).parent / "assets"

# -------------------- Events Data --------------------
EVENTS = [
    {
        "id": 1,
        "name": "Club Night",
        "description": "Experience an electrifying night at the Club with DJs, lights, and dance!",
        "image": "club.jpeg",
        "date": "2025-10-10 20:00",
        "location": "Main Hall, Campus Club",
        "price": 500,
        "available_tickets": 50,
        "check_ins": 0
    },
    {
        "id": 2,
        "name": "Diwali Celebration",
        "description": "Celebrate Diwali with music, dance, food, and lights galore!",
        "image": "diwali.jpeg",
        "date": "2025-11-01 18:00",
        "location": "Auditorium, Campus Grounds",
        "price": 300,
        "available_tickets": 100,
        "check_ins": 0
    },
    {
        "id": 3,
        "name": "Freshers Welcome Party",
        "description": "Welcome the new batch with a fun-filled evening of games and music.",
        "image": "freshers.jpeg",
        "date": "2025-08-25 19:00",
        "location": "Student Lounge, Campus",
        "price": 200,
        "available_tickets": 75,
        "check_ins": 0
    },
    {
        "id": 4,
        "name": "Navratri Pooja & Dance",
        "description": "Join us for Navratri festivities including traditional pooja and dance.",
        "image": "navratri.jpeg.avif",
        "date": "2025-09-15 17:00",
        "location": "Cultural Hall, Campus",
        "price": 400,
        "available_tickets": 60,
        "check_ins": 0
    },
    {
        "id": 5,
        "name": "Ravan Dahan Event",
        "description": "Witness the grand Ravan Dahan ceremony with fireworks and performances.",
        "image": "ravan.jpeg",
        "date": "2025-10-05 18:30",
        "location": "Open Grounds, Campus",
        "price": 350,
        "available_tickets": 80,
        "check_ins": 0
    },
]
