from nba_api.stats.endpoints import ScoreboardV2
from nba_api.live.nba.endpoints import boxscore
from datetime import datetime, timedelta
import json
import requests
import uuid
import time

def run():
    x = 1
    while x < 2:
        # Get yesterday's date in NBA API format (MM/DD/YYYY)
        yesterday = (datetime.now() - timedelta(days=x)).strftime('%m/%d/%Y')

        # Query scoreboard for yesterday's games
        board = ScoreboardV2(game_date=yesterday)
        time.sleep(2)

        # Get game data
        games = board.get_dict()['resultSets'][0]['rowSet']

        x = x + 1
        print(x)
        # Loop through games
        for game in games:
            gameId = game[2]

            box = boxscore.BoxScore(gameId)
            time.sleep(2)
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
            home_id = find_all_fields(data, "homeTeam")
            for home in home_id:
                home_id = str(home["teamId"])
            away_id = find_all_fields(data, "awayTeam")
            for away in away_id:
                away_id = str(away["teamId"])

            #Period Table
            #home team
            period_home_index = find_all_fields(data, "homeTeam")
            for period_home_i in period_home_index:
                periods_home = period_home_i["periods"]
                for period in periods_home:                 
                    period_stat_id = str(uuid.uuid4())
                    periodh_id = str(period["period"])         
                    #get home team ID
                    #get game ID
                    periodh_type = str(period["periodType"])       
                    periodh_score = int(period["score"])
                    

                    #url = "http://localhost:5086/api/periods"  # Replace with your API endpoint
                    url = "https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/periods"

                    # Define the data payload (JSON)
                    payload = {
                        "PeriodStatId": period_stat_id,
                        "PeriodId": periodh_id,
                        "TeamId": home_id,    
                        "GameId": game_id,    
                        "PeriodType": periodh_type,  
                        "Score": periodh_score  
                    }

                    # Define headers (optional, but commonly used)
                    headers = {
                        "Content-Type": "application/json",  # Ensure the payload is sent as JSON
                        "Authorization": ""  # Add an API key or token if required
                    }

                    #Make the POST request
                    response = requests.post(url, json=payload, headers=headers)
                    print(f"Response Status: {response.status_code}")
                    #print("Response JSON:", response.json())
                    
            #away team
            period_away_index = find_all_fields(data, "awayTeam")
            for period_away_i in period_away_index:     
                periods_away = period_away_i["periods"]
                for period in periods_away:           
                    period_stat_id = str(uuid.uuid4())
                    perioda_id = str(period["period"])
                    #get home team ID
                    #get game ID
                    perioda_type = str(period["periodType"])
                    perioda_score = int(period["score"])
                    

                    #url = "http://localhost:5086/api/periods"  # Replace with your API endpoint
                    url = "https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/periods"

                    # Define the data payload (JSON)
                    payload = {
                        "PeriodStatId": period_stat_id,
                        "PeriodId": perioda_id,                 
                        "TeamId": away_id,
                        "GameId": game_id,  
                        "PeriodType": perioda_type,  
                        "Score": perioda_score 
                    }

                    # Define headers (optional, but commonly used)
                    headers = {
                        "Content-Type": "application/json",  # Ensure the payload is sent as JSON
                        "Authorization": ""  # Add an API key or token if required
                    }

                    #Make the POST request
                    response = requests.post(url, json=payload, headers=headers)
                    print(f"Response Status: {response.status_code}")
                    #print("Response JSON:", response.json())
    return f"Period data processed successfully for {yesterday} data."
                    