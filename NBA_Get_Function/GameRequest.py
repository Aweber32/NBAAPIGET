from nba_api.stats.endpoints import ScoreboardV2
from nba_api.live.nba.endpoints import boxscore
from datetime import datetime, timedelta
import json
import requests
import uuid

def run():
    x = 1
    while x < 2:
        print(x)
        x = x + 1
        # Get yesterday's date in NBA API format (MM/DD/YYYY)
        yesterday = (datetime.now() - timedelta(days=x)).strftime('%m/%d/%Y')

        # Query scoreboard for yesterday's games
        board = ScoreboardV2(game_date=yesterday)

        # Get game data
        games = board.get_dict()['resultSets'][0]['rowSet']


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

            # Helper function to safely parse datetime as a string
            def parse_datetime(value):
                try:
                    return value if value else None
                except (ValueError, TypeError):
                    return None

            # Helper function to parse integers
            def parse_int(value):
                try:
                    return int(value) if value is not None else None
                except (ValueError, TypeError):
                    return None

            # Helper function to parse booleans
            def parse_bool(value):
                try:
                    return bool(int(value)) if value is not None else None  # Convert '1'/'0' to True/False
                except (ValueError, TypeError):
                    return None

            # Extract and convert variables to correct types
            game_stat_id = str(uuid.uuid4())
            game_id = extract_first(find_all_fields(data, "gameId"))  # String
            gametime_local = parse_datetime(extract_first(find_all_fields(data, "gameTimeLocal")))  # DateTime?
            gametime_utc = parse_datetime(extract_first(find_all_fields(data, "gameTimeUTC")))  # DateTime?
            gametime_home = parse_datetime(extract_first(find_all_fields(data, "gameTimeHome")))  # DateTime?
            gametime_away = parse_datetime(extract_first(find_all_fields(data, "gameTimeAway")))  # DateTime?
            game_et = parse_datetime(extract_first(find_all_fields(data, "gameEt")))  # DateTime?
            duration = parse_int(extract_first(find_all_fields(data, "duration")))  # int?
            game_code = extract_first(find_all_fields(data, "gameCode"))  # String
            game_status_text = extract_first(find_all_fields(data, "gameStatusText"))  # String
            game_status = parse_int(extract_first(find_all_fields(data, "gameStatus")))  # int?
            regulation_periods = parse_int(data["regulationPeriods"]) if "regulationPeriods" in data else None  # int?
            attendance = parse_int(extract_first(find_all_fields(data, "attendance")))  # int?
            sellout = parse_bool(extract_first(find_all_fields(data, "sellout")))  # bool?
            arena_id = parse_int(extract_first(find_all_fields(data, "arenaId")))  # int?
            lead_changes = parse_int(extract_first(find_all_fields(data, "leadChanges")))  # int?
            times_tied = parse_int(extract_first(find_all_fields(data, "timesTied")))  # int?


            # Define the URL for the POST request
            #url = "http://localhost:5086/api/games"  # Replace with your API endpoint
            url = "https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/games"

            # Define the data payload (JSON)
            payload = {
                "gameStatId":game_stat_id,
                "gameId": game_id,
                "gameTimeLocal": gametime_local,
                "gameTimeUTC": gametime_utc,
                "gameTimeHome": gametime_home,
                "gameTimeAway": gametime_away,
                "gameEt": game_et,
                "duration": duration,
                "gameCode": game_code,
                "gameStatusText": game_status_text,
                "gameStatus": game_status,
                "regulationPeriods": regulation_periods,
                "attendance": attendance,
                "sellout": sellout,
                "arenaId": arena_id,
                "leadChanges": lead_changes,
                "timesTied": times_tied
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
    return f"Game data processed successfully for {yesterday} data."    
       








