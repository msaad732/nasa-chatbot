README.md:

# NASA & USGS Data Chatbot

A FastAPI-based chatbot that answers user questions about asteroids (NASA data) and earthquakes (USGS data). The bot uses the Groq API to generate responses based on the dataset.

## Features

- Provides information about hazardous asteroids and their proximity to Earth.
- Provides information about recent and significant earthquakes by location.
- Answers user queries using both NASA and USGS datasets.
- Integrates with the Groq API for natural language responses.

## Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd <repo-directory>


Install dependencies

pip install -r requirements.txt


Set environment variables

Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key_here


Prepare datasets

Place your CSV files in the data/ directory:

neo_feed.csv (NASA asteroid data)

usgs_earthquakes.csv (USGS earthquake data)

Run the API
uvicorn main:app --reload


The API will be available at http://127.0.0.1:8000.

API Usage

Endpoint: /chatbot
Method: POST
Payload:

{
    "question": "Will the earthquake in California affect me?"
}


Response:

{
    "response": "..."
}

Notes

Make sure your CSV files have the correct columns:

neo_feed.csv: name, diameter_m, hazardous, miss_distance_km

usgs_earthquakes.csv: place, magnitude

The chatbot uses a simple heuristic to extract locations from the user query.


---

If you want, I can also make a **ready-to-use folder structure** including `data/`, `.env.example`, and `main.py` with this setup so you can just run it immediately.  

Do you want me to do that?
