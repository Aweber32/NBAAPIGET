from nba_api.stats.endpoints import ScoreboardV2
from nba_api.live.nba.endpoints import boxscore
from datetime import datetime, timedelta
import json
import requests
import uuid
import re
import unicodedata
import time

def run():

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

    x = 1
    while x < 2:
        # Get yesterday's date in NBA API format (MM/DD/YYYY)
        yesterday = (datetime.now() - timedelta(days=x)).strftime('%m/%d/%Y')

        # Get yesterday's date in Odds API format (YYYY/MM/YYYY)
        yesterday_odds = (datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d')

        # Query scoreboard for yesterday's games
        board = ScoreboardV2(game_date=yesterday)
        time.sleep(2)

        # Get game data
        games = board.get_dict()['resultSets'][0]['rowSet']

        #response = requests.get('http://localhost:5086/api/players/').json()
        response = requests.get('https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/players/').json()
        all_player_ids = [player["playerId"] for player in response if "playerId" in player]

        # Get yesterdays predictions
        #api_url = "http://localhost:5086/api/linepredictions"
        api_url = "https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/linepredictions"

        # ✅ Add Query Parameter to Filter by Date
        params = {"date": yesterday_odds}

        # ✅ Make GET Request
        response_odds = requests.get(api_url, params=params)
        # ✅ Check if the request was successful
        if response_odds.status_code == 200:
            data_odds = response_odds.json()  # Parse JSON response
        #print(data_odds)
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
            
            game_id = extract_first(find_all_fields(data, "gameId"))
            home_id = find_all_fields(data, "homeTeam")
            for home in home_id:
                home_id = str(home["teamId"])
            away_id = find_all_fields(data, "awayTeam")
            for away in away_id:
                away_id = str(away["teamId"])

            #Player and Stats Table
            #home team
            home_t = find_all_fields(data, "homeTeam")
            for home_players in home_t:
                home_players_i = home_players["players"]
                for player in home_players_i:
                    player_starter = False
                    player_name = clean_player_name(player["name"])
                    player_id = str(player["personId"])
                    if player_id in all_player_ids:
                        if player["starter"] == '1': #ensure starter is Posted to the Statistics table
                            player_starter = True
                        else:
                            player_starter = False
                    else:
                        #get home team id
                        #get game id
                        player_name = clean_player_name(player["name"])
                        player_namei = player["nameI"]
                        player_firstname = player["firstName"]
                        player_familyname = player["familyName"]
                        player_jerseynum = player["jerseyNum"]
                        if player.get("position") is None:
                            player_pos = ""
                        else:
                            player_pos = player["position"]
                        if player["starter"] == 1: #ensure starter is Posted to the Statistics table
                            player_starter = True
                        else:
                            player_starter = False

                        # Define the URL for the POST request
                        #url = f"http://localhost:5086/api/players/"  # Replace with your API endpoint
                        url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/players/"

                        # Define the data payload (JSON)
                        payload = {
                            "PlayerId" : player_id, 
                            "TeamId" : home_id, 
                            "Name" : player_name, 
                            "NameI": player_namei, 
                            "FirstName": player_firstname,
                            "FamilyName": player_familyname,
                            "JerseyNum":player_jerseynum, 
                            "Position": player_pos
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
                    
                    #Update GameIds for old records
                    for record in data_odds:
                        if player_name == record["name"]:
                            line_id = record["lineId"]
                            update_payload = {
                                "lineId" : line_id,
                                "gameId": game_id}
                            # ✅ API Endpoint for PUT request
                            put_url = f"{api_url}/{line_id}"
                            # ✅ Make PUT request to update the prediction field
                            put_response = requests.put(put_url, json=update_payload)
                            print(f'Historic Record Update: {put_response.status_code}')
                            #print("Response JSON:", put_response.text)
                        
                    #Statistics table
                    stat_id = str(uuid.uuid4())
                    player_stats = player["statistics"]
                    player_id = str(player["personId"])
                    #add game ID
                    if player["oncourt"] == "1":
                        player_oncourt = True
                    else:
                        player_oncourt = False
                    if player["played"] == "1":
                        player_played = True
                    else:
                        player_played = False
                    if player.get("notPlayingReason") is None:
                        player_notPlaying = "active"
                    else:
                        player_notPlaying = str(player["notPlayingReason"])
                    if player.get("notPlayingDescription") is None:
                        player_notPlayingdesc = ""
                    else:
                        player_notPlayingdesc = str(player["notPlayingDescription"])           
                    assists = int(player_stats["assists"])
                    blocks = int(player_stats["blocks"])
                    blocksRecieved = int(player_stats["blocksReceived"])
                    fieldGoalsAttempted = int(player_stats["fieldGoalsAttempted"])
                    fieldGoalsMade = int(player_stats["fieldGoalsMade"])
                    fieldGoalsPercentage = float(player_stats["fieldGoalsPercentage"])
                    foulsOffensive = int(player_stats["foulsOffensive"])
                    foulsDrawn = int(player_stats["foulsDrawn"])
                    foulsPersonal = int(player_stats["foulsPersonal"])
                    foulsTechnical = int(player_stats["foulsTechnical"])
                    freeThrowsAttempted = int(player_stats["freeThrowsAttempted"])
                    freeThrowsMade = int(player_stats["freeThrowsMade"])
                    freeThrowsPercentage = float(player_stats["freeThrowsPercentage"])
                    minus = float(player_stats["minus"])
                    minutes = str(player_stats["minutes"])
                    minutesCalculated = str(player_stats["minutesCalculated"])
                    plus = float(player_stats["plus"])
                    plusMinusPoints = float(player_stats["plusMinusPoints"])
                    points = int(player_stats["points"])
                    pointsFastBreak = int(player_stats["pointsFastBreak"])
                    pointsInThePaint = int(player_stats["pointsInThePaint"])
                    pointsSecondChance = int(player_stats["pointsSecondChance"])
                    reboundsDefensive = int(player_stats["reboundsDefensive"])
                    reboundsOffensive = int(player_stats["reboundsOffensive"])
                    reboundsTotal = int(player_stats["reboundsTotal"])
                    steals = int(player_stats["steals"])
                    threePointersAttempted = int(player_stats["threePointersAttempted"])
                    threePointersMade = int(player_stats["threePointersMade"])
                    threePointersPercentage = float(player_stats["threePointersPercentage"])
                    turnovers = int(player_stats["turnovers"])
                    twoPointersAttempted = int(player_stats["twoPointersAttempted"])
                    twoPointersMade = int(player_stats["twoPointersMade"])
                    twoPointersPercentage = float(player_stats["twoPointersPercentage"])

                    # Define the URL for the POST request
                    #url = f"http://localhost:5086/api/playerstatistics/"  # Replace with your API endpoint
                    url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/playerstatistics/"

                    # Define the data payload (JSON)
                    payload = { 
                        "StatId":stat_id,
                        "PlayerId": player_id,  
                        "GameId": game_id,  
                        "Assists": assists,
                        "Blocks": blocks,
                        "BlocksReceived": blocksRecieved,
                        "FieldGoalsAttempted": fieldGoalsAttempted,
                        "FieldGoalsMade": fieldGoalsMade,
                        "FieldGoalsPercentage": fieldGoalsPercentage,
                        "FoulsOffensive": foulsOffensive,
                        "FoulsDrawn": foulsDrawn,
                        "FoulsPersonal": foulsPersonal,
                        "FoulsTechnical": foulsTechnical,
                        "FreeThrowsAttempted": freeThrowsAttempted,
                        "FreeThrowsMade": freeThrowsMade,
                        "FreeThrowsPercentage": freeThrowsPercentage,
                        "Minus": minus,
                        "Minutes": minutes,
                        "MinutesCalculated": minutesCalculated,
                        "Plus": plus,
                        "PlusMinusPoints": plusMinusPoints,
                        "Points": points,
                        "PointsFastBreak": pointsFastBreak,
                        "PointsInThePaint": pointsInThePaint,
                        "PointsSecondChance": pointsSecondChance,
                        "ReboundsDefensive": reboundsDefensive,
                        "ReboundsOffensive": reboundsOffensive,
                        "ReboundsTotal": reboundsTotal,
                        "Steals": steals,
                        "ThreePointersAttempted": threePointersAttempted,
                        "ThreePointersMade": threePointersMade,
                        "ThreePointersPercentage": threePointersPercentage,
                        "Turnovers": turnovers,
                        "TwoPointersAttempted": twoPointersAttempted,
                        "TwoPointersMade": twoPointersMade,
                        "TwoPointersPercentage": twoPointersPercentage,
                        "Starter": player_starter,
                        "PlayerOnCourt": player_oncourt, 
                        "PlayerPlayed": player_played, 
                        "PlayerNotPlayingReason": player_notPlaying,
                        "PlayerNotPlayingDescription": player_notPlayingdesc
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
            away_t = find_all_fields(data, "awayTeam")
            for away_players in away_t:
                away_players_i = away_players["players"]
                for player in away_players_i:
                    player_starter = False
                    player_name = clean_player_name(player["name"])
                    player_id = str(player["personId"])
                    if player_id in all_player_ids:
                        if player["starter"] == '1': #ensure starter is Posted to the Statistics table
                            player_starter = True
                        else:
                            player_starter = False
                    else:
                        #get home team id
                        #get game id
                        player_name = clean_player_name(player["name"])
                        player_namei = player["nameI"]
                        player_firstname = player["firstName"]
                        player_familyname = player["familyName"]
                        player_jerseynum = player["jerseyNum"]
                        if player.get("position") is None:
                            player_pos = ""
                        else:
                            player_pos = player["position"]
                        if player["starter"] == 1: #ensure starter is Posted to the Statistics table
                            player_starter = True
                        else:
                            player_starter = False

                        # Define the URL for the POST request
                        #url = f"http://localhost:5086/api/players/"  # Replace with your API endpoint
                        url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/players/"

                        # Define the data payload (JSON)
                        payload = {
                            "PlayerId" : player_id, 
                            "TeamId" : away_id, 
                            "Name" : player_name, 
                            "NameI": player_namei, 
                            "FirstName": player_firstname,
                            "FamilyName": player_familyname,
                            "JerseyNum":player_jerseynum, 
                            "Position": player_pos
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
                    
                    #Update GameIds for old records
                    for record in data_odds:        
                        if player_name == record["name"]:
                            line_id = record["lineId"]
                            update_payload = {
                                "lineId" : line_id,
                                "gameId": game_id}
                            # ✅ API Endpoint for PUT request
                            put_url = f"{api_url}/{line_id}"
                            # ✅ Make PUT request to update the prediction field
                            put_response = requests.put(put_url, json=update_payload)
                            print(f'Historic Record Update: {put_response.status_code}')
                            #print("Response JSON:", put_response.text)

                    #Statistics table
                    stat_id = str(uuid.uuid4())
                    player_stats = player["statistics"]
                    player_id = str(player["personId"])
                    #add game ID
                    if player["oncourt"] == "1":
                        player_oncourt = True
                    else:
                        player_oncourt = False
                    if player["played"] == "1":
                        player_played = True
                    else:
                        player_played = False
                    if player.get("notPlayingReason") is None:
                        player_notPlaying = "active"
                    else:
                        player_notPlaying = str(player["notPlayingReason"])
                    if player.get("notPlayingDescription") is None:
                        player_notPlayingdesc = ""
                    else:
                        player_notPlayingdesc = str(player["notPlayingDescription"])           
                    assists = int(player_stats["assists"])
                    blocks = int(player_stats["blocks"])
                    blocksRecieved = int(player_stats["blocksReceived"])
                    fieldGoalsAttempted = int(player_stats["fieldGoalsAttempted"])
                    fieldGoalsMade = int(player_stats["fieldGoalsMade"])
                    fieldGoalsPercentage = float(player_stats["fieldGoalsPercentage"])
                    foulsOffensive = int(player_stats["foulsOffensive"])
                    foulsDrawn = int(player_stats["foulsDrawn"])
                    foulsPersonal = int(player_stats["foulsPersonal"])
                    foulsTechnical = int(player_stats["foulsTechnical"])
                    freeThrowsAttempted = int(player_stats["freeThrowsAttempted"])
                    freeThrowsMade = int(player_stats["freeThrowsMade"])
                    freeThrowsPercentage = float(player_stats["freeThrowsPercentage"])
                    minus = float(player_stats["minus"])
                    minutes = str(player_stats["minutes"])
                    minutesCalculated = str(player_stats["minutesCalculated"])
                    plus = float(player_stats["plus"])
                    plusMinusPoints = float(player_stats["plusMinusPoints"])
                    points = int(player_stats["points"])
                    pointsFastBreak = int(player_stats["pointsFastBreak"])
                    pointsInThePaint = int(player_stats["pointsInThePaint"])
                    pointsSecondChance = int(player_stats["pointsSecondChance"])
                    reboundsDefensive = int(player_stats["reboundsDefensive"])
                    reboundsOffensive = int(player_stats["reboundsOffensive"])
                    reboundsTotal = int(player_stats["reboundsTotal"])
                    steals = int(player_stats["steals"])
                    threePointersAttempted = int(player_stats["threePointersAttempted"])
                    threePointersMade = int(player_stats["threePointersMade"])
                    threePointersPercentage = float(player_stats["threePointersPercentage"])
                    turnovers = int(player_stats["turnovers"])
                    twoPointersAttempted = int(player_stats["twoPointersAttempted"])
                    twoPointersMade = int(player_stats["twoPointersMade"])
                    twoPointersPercentage = float(player_stats["twoPointersPercentage"])

                    # Define the URL for the POST request
                    #url = f"http://localhost:5086/api/playerstatistics/"  # Replace with your API endpoint
                    url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/playerstatistics/"

                    # Define the data payload (JSON)
                    payload = { 
                        "StatId":stat_id,
                        "PlayerId": player_id,  
                        "GameId": game_id,  
                        "Assists": assists,
                        "Blocks": blocks,
                        "BlocksReceived": blocksRecieved,
                        "FieldGoalsAttempted": fieldGoalsAttempted,
                        "FieldGoalsMade": fieldGoalsMade,
                        "FieldGoalsPercentage": fieldGoalsPercentage,
                        "FoulsOffensive": foulsOffensive,
                        "FoulsDrawn": foulsDrawn,
                        "FoulsPersonal": foulsPersonal,
                        "FoulsTechnical": foulsTechnical,
                        "FreeThrowsAttempted": freeThrowsAttempted,
                        "FreeThrowsMade": freeThrowsMade,
                        "FreeThrowsPercentage": freeThrowsPercentage,
                        "Minus": minus,
                        "Minutes": minutes,
                        "MinutesCalculated": minutesCalculated,
                        "Plus": plus,
                        "PlusMinusPoints": plusMinusPoints,
                        "Points": points,
                        "PointsFastBreak": pointsFastBreak,
                        "PointsInThePaint": pointsInThePaint,
                        "PointsSecondChance": pointsSecondChance,
                        "ReboundsDefensive": reboundsDefensive,
                        "ReboundsOffensive": reboundsOffensive,
                        "ReboundsTotal": reboundsTotal,
                        "Steals": steals,
                        "ThreePointersAttempted": threePointersAttempted,
                        "ThreePointersMade": threePointersMade,
                        "ThreePointersPercentage": threePointersPercentage,
                        "Turnovers": turnovers,
                        "TwoPointersAttempted": twoPointersAttempted,
                        "TwoPointersMade": twoPointersMade,
                        "TwoPointersPercentage": twoPointersPercentage,
                        "Starter": player_starter,
                        "PlayerOnCourt": player_oncourt, 
                        "PlayerPlayed": player_played, 
                        "PlayerNotPlayingReason": player_notPlaying,
                        "PlayerNotPlayingDescription": player_notPlayingdesc
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
    return f"Player and Stats data processed successfully for {yesterday} data. with response code {response.status_code}"  
