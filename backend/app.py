/* ------------------------------
   General Page Styles
-------------------------------*/
body {
    font-family: "Arial", sans-serif;
}

h1 {
    color: #ff4b4b;
    text-align: center;
    margin-bottom: 30px;
}

h2, h3 {
    color: #4b6cff;
    margin-top: 20px;
}

/* ------------------------------
   Event Grid Layout
-------------------------------*/
.event-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

/* Individual Event Card */
.event-card {
    background-color: #f5f5f5;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.event-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* ------------------------------
   Ledger Section
-------------------------------*/
.ledger-section {
    background-color: #eef2ff;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}

/* Transactions Table */
.dataframe, .stDataFrame {
    width: 100% !important;
}

/* ------------------------------
   Buttons
-------------------------------*/
.stButton button {
    background-color: #4b6cff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
}

.stButton button:hover {
    background-color: #3a53d4;
}

/* ------------------------------
   Responsive Adjustments
-------------------------------*/
@media screen and (max-width: 768px) {
    .event-card img {
        height: 150px;
    }
}

@media screen and (max-width: 480px) {
    .event-card img {
        height: 120px;
    }

    .stButton button {
        width: 100%;
    }
}
