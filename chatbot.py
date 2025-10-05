import pandas as pd
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv 

NASA_CSV = "data/neo_feed.csv"
USGS_CSV = "data/usgs_earthquakes.csv"

load_dotenv()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY =  os.getenv("GROQ_API_KEY")

app = FastAPI()

def load_nasa_data():
    return pd.read_csv(NASA_CSV)

def load_usgs_data():
    return pd.read_csv(USGS_CSV)

class UserQuery(BaseModel):
    question: str

def extract_location(question: str):
    """
    Extracts a possible location from the user question.
    For simplicity, takes the last proper noun-like word (e.g. Japan, India, California).
    """
    words = question.split()
    # crude heuristic: pick capitalized words or last word
    candidates = [w for w in words if w[0].isupper()]
    if candidates:
        return candidates[-1]
    return None

@app.post("/chatbot")
async def chatbot(query: UserQuery):
    try:
        nasa_data = load_nasa_data()
        usgs_data = load_usgs_data()
    except FileNotFoundError as e:
        return {"response": f"Error: {str(e)}. Make sure CSV files are generated."}

    user_question = query.question
    user_question_lower = user_question.lower()

    # -------- Location Context --------
    location_context = ""
    location = extract_location(user_question)
    if location:
        quakes = usgs_data[usgs_data["place"].str.contains(location, case=False, na=False)]
        if not quakes.empty:
            recent_quake = quakes.sort_values(by="magnitude", ascending=False).iloc[0]
            location_context += f"In {location}, the strongest earthquake in this dataset was magnitude {recent_quake['magnitude']} at {recent_quake['place']}. "
        else:
            location_context += f"There were no significant earthquakes in {location} in this dataset. "

    # -------- Asteroid Context --------
    if "asteroid" in user_question_lower or "hit" in user_question_lower or "affect" in user_question_lower:
        closest_approach = nasa_data.loc[nasa_data["miss_distance_km"].idxmin()]
        miss_dist = closest_approach['miss_distance_km']
        name = closest_approach['name']
        hazardous = bool(closest_approach['hazardous'])

        if miss_dist < 500000:  # ~ lunar distance
            location_context += f"The asteroid {name} passed very close to Earth at {miss_dist:,.0f} km. "
            if hazardous:
                location_context += "It is classified as potentially hazardous. "
        else:
            location_context += f"No asteroid in the dataset comes dangerously close; the nearest was {name} at {miss_dist:,.0f} km away. "

    # -------- Global Summaries --------
    nasa_summary = f"There are {nasa_data[nasa_data['hazardous'] == 1].shape[0]} hazardous asteroids."
    largest_asteroid = nasa_data.loc[nasa_data["diameter_m"].idxmax()]
    nasa_summary += f" The largest asteroid is {largest_asteroid['name']} with a diameter of {largest_asteroid['diameter_m']:.2f} meters."

    strongest_earthquake = usgs_data.loc[usgs_data["magnitude"].idxmax()]
    usgs_summary = f"The strongest earthquake overall was at {strongest_earthquake['place']} with a magnitude of {strongest_earthquake['magnitude']}."

    # -------- Final Prompt --------
    combined_prompt = (
        f"NASA Data:\n{nasa_summary}\n\n"
        f"USGS Data:\n{usgs_summary}\n\n"
        f"Location Context:\n{location_context}\n\n"
        f"User Question: {user_question}\n"
        f"Answer using the above data. If the user asks 'will this affect me in <location>', explain clearly whether earthquakes or asteroids pose a risk."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
    "model": "llama-3.1-8b-instant",   # updated model
    "messages": [
        {"role": "system", "content": "You are a data assistant. Use NASA asteroid and USGS earthquake data to answer user questions. If asked about a location, check dataset and explain risk."},
        {"role": "user", "content": combined_prompt}
    ],
    "temperature": 0.3
    }


    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        groq_response = response.json()
        return {"response": groq_response["choices"][0]["message"]["content"]}
    else:
        return {"response": f"Error: {response.status_code}, {response.text}"}
