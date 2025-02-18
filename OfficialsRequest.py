from nba_api.stats.endpoints import ScoreboardV2
from nba_api.live.nba.endpoints import boxscore
from datetime import datetime, timedelta
import json
import requests
import uuid

x = 1
while x < 2:
    # Get yesterday's date in NBA API format (MM/DD/YYYY)
    yesterday = (datetime.now() - timedelta(days=x)).strftime('%m/%d/%Y')

    # Query scoreboard for yesterday's games
    board = ScoreboardV2(game_date=yesterday)

    # Get game data
    games = board.get_dict()['resultSets'][0]['rowSet']

    x = x + 1
    print(x)
    # Loop through games
    for game in games:
        gameId = game[2]

        box = boxscore.BoxScore(gameId)
        pretty_json = json.dumps(box.game.get_dict(), indent=4)

        #print(pretty_json)

        data = json.loads(pretty_json)

        def find_all_fields(data, field_name, results=None):
            if results is None:
                results = []

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == field_name:
                        results.append(value)
                    if isinstance(value, (dict, list)):
                        find_all_fields(value, field_name, results)
            elif isinstance(data, list):
                for item in data:
                    find_all_fields(item, field_name, results)

            return results
        def extract_first(lst):
            return lst[0] if isinstance(lst, list) and lst else None
        
        game_id = extract_first(find_all_fields(data, "gameId"))  # String

        officials = find_all_fields(data, "officials")
        for official in officials:
            for i in official:
                official_stat_id = str(uuid.uuid4())
                official_Id = str(i["personId"])
                #Add Game ID to post request
                official_name = str(i["name"])
                official_namei = str(i["nameI"])
                official_firstname = str(i["firstName"])
                official_familyname = str(i["familyName"])
                assignment = str(i["assignment"])

                # Define the URL for the POST request
                url = "http://localhost:5086/api/officials"  # Replace with your API endpoint

                # Define the data payload (JSON)
                payload = {
                    "OfficialStatId": official_stat_id,
                    "OfficialId" : official_Id,
                    "GameId": game_id,
                    "Name" : official_name,
                    "NameI": official_namei,
                    "FirstName": official_firstname,
                    "FamilyName": official_familyname,
                    "Assignment": assignment
                    
                }

                # Define headers (optional, but commonly used)
                headers = {
                    "Content-Type": "application/json",  # Ensure the payload is sent as JSON
                    "Authorization": ""  # Add an API key or token if required
                }

                #Make the POST request
                response = requests.post(url, json=payload, headers=headers, timeout=2)
                print(f"Response Status: {response.status_code}")
                #print("Response JSON:", response.json())