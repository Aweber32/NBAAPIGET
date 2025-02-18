import requests
import json
from datetime import datetime, timedelta
import re
import unicodedata

def clean_player_name(s):
    # Normalize Unicode characters (e.g., é → e, ñ → n)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')

    # Remove anything that is not a letter, space, or hyphen
    s = re.sub(r"[^a-zA-Z \-]", "", s)

    # Remove generational suffixes like II, III, IV (standalone)
    s = re.sub(r'\b(II|III|IV|V|VI|VII|VIII|IX|X)\b', '', s)

    # Clean up multiple spaces and leading/trailing spaces
    s = re.sub(r'\s+', ' ', s).strip()

    return s

api_key = "86645240d449932ada2a404eb3cc7a11"

today = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d') #error in api where games are appearing as tommrow

url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events?commenceTimeFrom={today}T01:00:00Z&commenceTimeTo={today}T23:59:00Z&apiKey={api_key}"

response = requests.get(url) 
data = response.json()

# Extract game IDs and game dates
games = [{"id": game["id"], "date": game["commence_time"][:10]} for game in data]  # Extract YYYY-MM-DD date

# Step 2: Iterate through each game and fetch player odds
#player_lines = []  # Store all extracted player line data

for game in games:
    gameid = game["id"]
    game_date = datetime.strptime(game["date"], "%Y-%m-%d") - timedelta(days=1)  # ✅ Adjust date (-1 day)
    game_date = game_date.strftime("%Y-%m-%d")  # Convert back to string

    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/events/{gameid}/odds?&regions=us&markets=player_points,player_steals,player_rebounds,player_assists&oddsFormat=american&apiKey={api_key}"
    
    response = requests.get(url) 
    data = response.json()
    # Debugging: Print API response for odds
    if "bookmakers" not in data:
        print(f"Error: No 'bookmakers' found in game ID {gameid}")
        continue

    # Define the stat categories to extract
    stat_categories = {
        "player_points": "Player_Points",
        "player_assists": "Player_Assists",
        "player_rebounds": "Player_Rebounds",
        "player_steals": "Player_Steals"
    }

    for bookmaker in data["bookmakers"]:
        if bookmaker["key"] in ["fanduel", "draftkings"]:  # Filter for FanDuel & DraftKings
            book = bookmaker["key"]  # "fanduel" or "draftkings"
            
            for market in bookmaker["markets"]:
                if market["key"] in stat_categories:  # Extract relevant stats
                    over_price = None
                    under_price = None
                    player_name = None
                    line_value = None

                    # ✅ Ensure we correctly assign both "Over" and "Under" values
                    for outcome in market["outcomes"]:
                        if player_name is None:  # Assign name only once
                            player_name = clean_player_name(outcome["description"])
                            line_value = outcome["point"]

                        if outcome["name"] == "Over":
                            over_price = outcome["price"]
                        elif outcome["name"] == "Under":
                            under_price = outcome["price"]

                    # Store extracted data
                    payload = {
                        # Leaving GameId blank as per request
                        "Date": game_date,  # ✅ Adjusted game date (-1 day)
                        "Name": player_name,
                        "Book": book,
                        "Type": stat_categories[market["key"]],  # Convert stat key to readable format
                        "Line": line_value,
                        "Over": over_price,  # ✅ Ensures over is stored
                        "Under": under_price,  # ✅ Ensures under is stored
                        # Leaving Prediction blank as per request
                    }
                    #player_lines.append(player_line)

                    # Define the URL for the POST request
                    url = "http://localhost:5086/api/linepredictions"  # Replace with your API endpoint

                    # Define headers (optional, but commonly used)
                    headers = {
                        "Content-Type": "application/json",  # Ensure the payload is sent as JSON
                        "Authorization": ""  # Add an API key or token if required
                    }

                    #Make the POST request
                    response = requests.post(url, json=payload, headers=headers, timeout=2)
                    print(f"Response Status: {response.status_code}")
                    print("Response JSON:", response.json())

