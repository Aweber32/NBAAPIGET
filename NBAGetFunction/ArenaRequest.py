from nba_api.stats.endpoints import ScoreboardV2
from nba_api.live.nba.endpoints import boxscore
from datetime import datetime, timedelta
import json
import requests
import nba_api.stats.library.http as nba_http


def run():
    # Configure your Data Impulse proxy details
    proxies = {
        'http': "http://d3654d34ba507d40ef6a__cr.us:3d4c9b7c48e1a1ea@gw.dataimpulse.com:823",
        'https': "http://d3654d34ba507d40ef6a__cr.us:3d4c9b7c48e1a1ea@gw.dataimpulse.com:823"
    }

    # Create a custom session that uses your proxy and sets browser-like headers
    session = requests.Session()
    session.proxies.update(proxies)
    session.headers.update({
        'Host': 'stats.nba.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    # Override the default session used by nba_api to use our custom session
    nba_http._get_session = lambda: session

    x = 1
    while x < 2:
        print(x)
        x = x + 1
        # Get yesterday's date in NBA API format (MM/DD/YYYY)
        yesterday = (datetime.now() - timedelta(days=x)).strftime('%m/%d/%Y')

        # Query scoreboard for yesterday's games
        board = ScoreboardV2(game_date=yesterday, timeout=120)

        # Get game data
        games = board.get_dict()['resultSets'][0]['rowSet']

        response = requests.get('https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/arenas/').json()
        #response = requests.get('http://localhost:5086/api/arenas/').json()
        all_arena_ids = [arena["arenaId"] for arena in response if "arenaId" in arena]


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
            
            #Arenas Tables
            arena = find_all_fields(data, "arena")
            for i in arena:  
                arena_id = str(i["arenaId"])  # Convert to NVARCHAR
                if arena_id in all_arena_ids:
                    continue
                else:
                    arena_name = str(i["arenaName"]) if i["arenaName"] else None  # Convert to NVARCHAR
                    arena_city = str(i["arenaCity"]) if i["arenaCity"] else None  # Convert to NVARCHAR
                    arena_state = str(i["arenaState"]) if i["arenaState"] else None  # Convert to NVARCHAR
                    arena_country = str(i["arenaCountry"]) if i["arenaCountry"] else None  # Convert to NVARCHAR
                    arena_tz = str(i["arenaTimezone"]) if i["arenaTimezone"] else None  # Convert to NVARCHAR

                    # Define the URL for the POST request
                    #url = f"http://localhost:5086/api/arenas/"  # Replace with your API endpoint
                    url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/arenas/"

                    # Define the data payload (JSON)
                    payload = {
                        "arenaId": arena_id, # str
                        "arenaName": arena_name,  # nvarchar
                        "arenaCity": arena_city,  # nvarchar
                        "arenaState": arena_state,  # nvarchar
                        "arenaCountry": arena_country,  # nvarchar
                        "arenaTimezone": arena_tz  # nvarchar
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
    return f"Arenas data processed successfully for {yesterday} data."