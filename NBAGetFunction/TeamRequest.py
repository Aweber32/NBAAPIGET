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

            game_id = extract_first(find_all_fields(data, "gameId"))  # String

            #Team Table
            #Home team
            hometeam_index = find_all_fields(data, "homeTeam")
            for hometeam in hometeam_index:
                # Convert variables to correct types
                team_stat_id = str(uuid.uuid4())
                hometeam_id = str(hometeam["teamId"])  # String
                hometeam_name = str(hometeam["teamName"])  # Nullable String
                hometeam_city = str(hometeam["teamCity"])  # Nullable String
                hometeam_tricode = str(hometeam["teamTricode"])  # Nullable String
                hometeam_score = parse_int(hometeam["score"])  # int?
                hometeam_bonue = parse_bool(hometeam["inBonus"])  # bool?
                hometeam_toremaining = parse_int(hometeam["timeoutsRemaining"])  # int?

                # Extract statistics
                stats_home = hometeam["statistics"]

                home_court = bool(True)
                hometeam_assiststoratio = parse_int(stats_home["assistsTurnoverRatio"])  # int?
                hometeam_benchpoints = parse_int(stats_home["benchPoints"])  # int?
                hometeam_biggestlead = parse_int(stats_home["biggestLead"])  # int?
                hometeam_biggestleadscore = str(stats_home.get("biggestLeadScore", "N/A")) # Nullable String
                hometeam_biggestscoringrun = parse_int(stats_home["biggestScoringRun"])  # int?
                hometeam_biggestscoringrunscore = str(stats_home.get("biggestScoringRunScore", "N/A"))  # Default to "N/A" if missing
                hometeam_blocks = parse_int(stats_home["blocks"])  # int?
                hometeam_blocksreceived = parse_int(stats_home["blocksReceived"])  # int?
                hometeam_fastbreakpointsattempted = parse_int(stats_home["fastBreakPointsAttempted"])  # int?
                hometeam_fastbreakpointsmade = parse_int(stats_home["fastBreakPointsMade"])  # int?
                hometeam_fastbreakpointspercentage = float(stats_home["fastBreakPointsPercentage"]) if stats_home["fastBreakPointsPercentage"] is not None else None  # double?

                hometeam_fieldgoalsattempted = parse_int(stats_home["fieldGoalsAttempted"])  # int?
                hometeam_fieldgoalseffectiveadjusted = float(stats_home["fieldGoalsEffectiveAdjusted"]) if stats_home["fieldGoalsEffectiveAdjusted"] is not None else None  # double?
                hometeam_fieldgoalsmade = parse_int(stats_home["fieldGoalsMade"])  # int?
                hometeam_fieldgoalspercentage = float(stats_home["fieldGoalsPercentage"]) if stats_home["fieldGoalsPercentage"] is not None else None  # double?

                hometeam_foulsoffensive = parse_int(stats_home["foulsOffensive"])  # int?
                hometeam_foulsdrawn = parse_int(stats_home["foulsDrawn"])  # int?
                hometeam_foulspersonal = parse_int(stats_home["foulsPersonal"])  # int?
                hometeam_foulsteam = parse_int(stats_home["foulsTeam"])  # int?
                hometeam_foulstechnical = parse_int(stats_home["foulsTechnical"])  # int?
                hometeam_foulsteamtechnical = parse_int(stats_home["foulsTeamTechnical"])  # int?

                hometeam_freethrowsattempted = parse_int(stats_home["freeThrowsAttempted"])  # int?
                hometeam_freethrowsmade = parse_int(stats_home["freeThrowsMade"])  # int?
                hometeam_freethrowspercentage = float(stats_home["freeThrowsPercentage"]) if stats_home["freeThrowsPercentage"] is not None else None  # double?

                hometeam_leadchanges = parse_int(stats_home["leadChanges"])  # int?
                hometeam_minutes = str(stats_home["minutes"])  # Nullable String
                hometeam_minutescalculated = str(stats_home["minutesCalculated"])  # Nullable String

                hometeam_points = parse_int(stats_home["points"])  # int?
                hometeam_pointsagainst = parse_int(stats_home["pointsAgainst"])  # int?
                hometeam_pointsfastbreak = parse_int(stats_home["pointsFastBreak"])  # int?
                hometeam_pointsfromturnovers = parse_int(stats_home["pointsFromTurnovers"])  # int?
                hometeam_pointsinthepaint = parse_int(stats_home["pointsInThePaint"])  # int?
                hometeam_pointsinthepaintattempted = parse_int(stats_home["pointsInThePaintAttempted"])  # int?
                hometeam_pointsinthepaintmade = parse_int(stats_home["pointsInThePaintMade"])  # int?
                hometeam_pointsinthepaintpercentage = float(stats_home["pointsInThePaintPercentage"]) if stats_home["pointsInThePaintPercentage"] is not None else None  # double?
                hometeam_pointssecondchance = parse_int(stats_home["pointsSecondChance"])  # int?

                hometeam_reboundsdefensive = parse_int(stats_home["reboundsDefensive"])  # int?
                hometeam_reboundsoffensive = parse_int(stats_home["reboundsOffensive"])  # int?
                hometeam_reboundspersonal = parse_int(stats_home["reboundsPersonal"])  # int?
                hometeam_reboundsteam = parse_int(stats_home["reboundsTeam"])  # int?
                hometeam_reboundsteamdefensive = parse_int(stats_home["reboundsTeamDefensive"])  # int?
                hometeam_reboundsteamoffensive = parse_int(stats_home["reboundsTeamOffensive"])  # int?
                hometeam_reboundstotal = parse_int(stats_home["reboundsTotal"])  # int?

                hometeam_secondchancepointsattempted = parse_int(stats_home["secondChancePointsAttempted"])  # int?
                hometeam_secondchancepointsmade = parse_int(stats_home["secondChancePointsMade"])  # int?
                hometeam_secondchancepointspercentage = float(stats_home["secondChancePointsPercentage"]) if stats_home["secondChancePointsPercentage"] is not None else None  # double?

                hometeam_steals = parse_int(stats_home["steals"])  # int?
                hometeam_threepointersattempted = parse_int(stats_home["threePointersAttempted"])  # int?
                hometeam_threepointersmade = parse_int(stats_home["threePointersMade"])  # int?
                hometeam_threepointerspercentage = float(stats_home["threePointersPercentage"]) if stats_home["threePointersPercentage"] is not None else None  # double?

                hometeam_timeleading = str(stats_home["timeLeading"])  # Nullable String
                hometeam_timestied = parse_int(stats_home["timesTied"])  # int?
                hometeam_trueshootingattempts = float(stats_home["trueShootingAttempts"]) if stats_home["trueShootingAttempts"] is not None else None  # double?
                hometeam_trueshootingpercentage = float(stats_home["trueShootingPercentage"]) if stats_home["trueShootingPercentage"] is not None else None  # double?

                hometeam_turnovers = parse_int(stats_home["turnovers"])  # int?
                hometeam_turnoversteam = parse_int(stats_home["turnoversTeam"])  # int?
                hometeam_turnoverstotal = parse_int(stats_home["turnoversTotal"])  # int?

                hometeam_twopointersattempted = parse_int(stats_home["twoPointersAttempted"])  # int?
                hometeam_twopointersmade = parse_int(stats_home["twoPointersMade"])  # int?
                hometeam_twopointerspercentage = float(stats_home["twoPointersPercentage"]) if stats_home["twoPointersPercentage"] is not None else None  # double?

                
                # Define the URL for the POST request
                #url = f"http://localhost:5086/api/teams/"  # Replace with your API endpoint
                url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/teams/"

                # Define the data payload (JSON)
                payload = {
                    "TeamStatId": team_stat_id,
                    "TeamId": hometeam_id,
                    "GameId": game_id,  # Ensure this variable is defined elsewhere
                    "HomeCourt": home_court,
                    "TeamName": hometeam_name,
                    "TeamCity": hometeam_city,
                    "TeamTricode": hometeam_tricode,
                    "Assists": hometeam_assiststoratio,
                    "AssistsTurnoverRatio": hometeam_assiststoratio,
                    "BenchPoints": hometeam_benchpoints,
                    "BiggestLead": hometeam_biggestlead,
                    "BiggestLeadScore": hometeam_biggestleadscore,
                    "BiggestScoringRun": hometeam_biggestscoringrun,
                    "BiggestScoringRunScore": hometeam_biggestscoringrunscore,
                    "Blocks": hometeam_blocks,
                    "BlocksReceived": hometeam_blocksreceived,
                    "FastBreakPointsAttempted": hometeam_fastbreakpointsattempted,
                    "FastBreakPointsMade": hometeam_fastbreakpointsmade,
                    "FastBreakPointsPercentage": hometeam_fastbreakpointspercentage,
                    "FieldGoalsAttempted": hometeam_fieldgoalsattempted,
                    "FieldGoalsEffectiveAdjusted": hometeam_fieldgoalseffectiveadjusted,
                    "FieldGoalsMade": hometeam_fieldgoalsmade,
                    "FieldGoalsPercentage": hometeam_fieldgoalspercentage,
                    "FoulsOffensive": hometeam_foulsoffensive,
                    "FoulsDrawn": hometeam_foulsdrawn,
                    "FoulsPersonal": hometeam_foulspersonal,
                    "FoulsTeam": hometeam_foulsteam,
                    "FoulsTechnical": hometeam_foulstechnical,
                    "FoulsTeamTechnical": hometeam_foulsteamtechnical,
                    "FreeThrowsAttempted": hometeam_freethrowsattempted,
                    "FreeThrowsMade": hometeam_freethrowsmade,
                    "FreeThrowsPercentage": hometeam_freethrowspercentage,
                    "LeadChanges": hometeam_leadchanges,
                    "Minutes": hometeam_minutes,
                    "MinutesCalculated": hometeam_minutescalculated,
                    "Points": hometeam_points,
                    "PointsAgainst": hometeam_pointsagainst,
                    "PointsFastBreak": hometeam_pointsfastbreak,
                    "PointsFromTurnovers": hometeam_pointsfromturnovers,
                    "PointsInThePaint": hometeam_pointsinthepaint,
                    "PointsInThePaintAttempted": hometeam_pointsinthepaintattempted,
                    "PointsInThePaintMade": hometeam_pointsinthepaintmade,
                    "PointsInThePaintPercentage": hometeam_pointsinthepaintpercentage,
                    "PointsSecondChance": hometeam_pointssecondchance,
                    "ReboundsDefensive": hometeam_reboundsdefensive,
                    "ReboundsOffensive": hometeam_reboundsoffensive,
                    "ReboundsPersonal": hometeam_reboundspersonal,
                    "ReboundsTeam": hometeam_reboundsteam,
                    "ReboundsTeamDefensive": hometeam_reboundsteamdefensive,
                    "ReboundsTeamOffensive": hometeam_reboundsteamoffensive,
                    "ReboundsTotal": hometeam_reboundstotal,
                    "SecondChancePointsAttempted": hometeam_secondchancepointsattempted,
                    "SecondChancePointsMade": hometeam_secondchancepointsmade,
                    "SecondChancePointsPercentage": hometeam_secondchancepointspercentage,
                    "Steals": hometeam_steals,
                    "ThreePointersAttempted": hometeam_threepointersattempted,
                    "ThreePointersMade": hometeam_threepointersmade,
                    "ThreePointersPercentage": hometeam_threepointerspercentage,
                    "TimeLeading": hometeam_timeleading,
                    "TimesTied": hometeam_timestied,
                    "TrueShootingAttempts": hometeam_trueshootingattempts,
                    "TrueShootingPercentage": hometeam_trueshootingpercentage,
                    "Turnovers": hometeam_turnovers,
                    "TurnoversTeam": hometeam_turnoversteam,
                    "TurnoversTotal": hometeam_turnoverstotal,
                    "TwoPointersAttempted": hometeam_twopointersattempted,
                    "TwoPointersMade": hometeam_twopointersmade,
                    "TwoPointersPercentage": hometeam_twopointerspercentage
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
                    
            #Away Team 
            awayteam_index = find_all_fields(data, "awayTeam")
            for awayteam in awayteam_index:
                # Convert variables to correct types
                team_stat_id = str(uuid.uuid4())
                awayteam_id = str(awayteam["teamId"])  # String
                awayteam_name = str(awayteam["teamName"])  # Nullable String
                awayteam_city = str(awayteam["teamCity"])  # Nullable String
                awayteam_tricode = str(awayteam["teamTricode"])  # Nullable String
                awayteam_score = parse_int(awayteam["score"])  # int?
                awayteam_bonus = parse_bool(awayteam["inBonus"])  # bool?
                awayteam_toremaining = parse_int(awayteam["timeoutsRemaining"])  # int?

                # Extract statistics
                stats_away = awayteam["statistics"]

                home_court = bool(False)
                awayteam_assiststoratio = parse_int(stats_away["assistsTurnoverRatio"])  # int?
                awayteam_benchpoints = parse_int(stats_away["benchPoints"])  # int?
                awayteam_biggestlead = parse_int(stats_away["biggestLead"])  # int?
                awayteam_biggestLeadScore = str(stats_away.get("biggestLeadScore", "N/A")) # Default to "N/A" if missing
                awayteam_biggestscoringrun = parse_int(stats_away["biggestScoringRun"])  # int?

                awayteam_biggestscoringrunscore = str(stats_away.get("biggestScoringRunScore", "N/A"))  # Default to "N/A" if missing
                awayteam_blocks = parse_int(stats_away["blocks"])  # int?
                awayteam_blocksreceived = parse_int(stats_away["blocksReceived"])  # int?
                awayteam_fastbreakpointsattempted = parse_int(stats_away["fastBreakPointsAttempted"])  # int?
                awayteam_fastbreakpointsmade = parse_int(stats_away["fastBreakPointsMade"])  # int?
                awayteam_fastbreakpointspercentage = float(stats_away["fastBreakPointsPercentage"]) if stats_away["fastBreakPointsPercentage"] is not None else None  # double?

                awayteam_fieldgoalsattempted = parse_int(stats_away["fieldGoalsAttempted"])  # int?
                awayteam_fieldgoalseffectiveadjusted = float(stats_away["fieldGoalsEffectiveAdjusted"]) if stats_away["fieldGoalsEffectiveAdjusted"] is not None else None  # double?
                awayteam_fieldgoalsmade = parse_int(stats_away["fieldGoalsMade"])  # int?
                awayteam_fieldgoalspercentage = float(stats_away["fieldGoalsPercentage"]) if stats_away["fieldGoalsPercentage"] is not None else None  # double?

                awayteam_foulsoffensive = parse_int(stats_away["foulsOffensive"])  # int?
                awayteam_foulsdrawn = parse_int(stats_away["foulsDrawn"])  # int?
                awayteam_foulspersonal = parse_int(stats_away["foulsPersonal"])  # int?
                awayteam_foulsteam = parse_int(stats_away["foulsTeam"])  # int?
                awayteam_foulstechnical = parse_int(stats_away["foulsTechnical"])  # int?
                awayteam_foulsteamtechnical = parse_int(stats_away["foulsTeamTechnical"])  # int?

                awayteam_freethrowsattempted = parse_int(stats_away["freeThrowsAttempted"])  # int?
                awayteam_freethrowsmade = parse_int(stats_away["freeThrowsMade"])  # int?
                awayteam_freethrowspercentage = float(stats_away["freeThrowsPercentage"]) if stats_away["freeThrowsPercentage"] is not None else None  # double?

                awayteam_leadchanges = parse_int(stats_away["leadChanges"])  # int?
                awayteam_minutes = str(stats_away["minutes"])  # Nullable String
                awayteam_minutescalculated = str(stats_away["minutesCalculated"])  # Nullable String

                awayteam_points = parse_int(stats_away["points"])  # int?
                awayteam_pointsagainst = parse_int(stats_away["pointsAgainst"])  # int?
                awayteam_pointsfastbreak = parse_int(stats_away["pointsFastBreak"])  # int?
                awayteam_pointsfromturnovers = parse_int(stats_away["pointsFromTurnovers"])  # int?
                awayteam_pointsinthepaint = parse_int(stats_away["pointsInThePaint"])  # int?
                awayteam_pointsinthepaintattempted = parse_int(stats_away["pointsInThePaintAttempted"])  # int?
                awayteam_pointsinthepaintmade = parse_int(stats_away["pointsInThePaintMade"])  # int?
                awayteam_pointsinthepaintpercentage = float(stats_away["pointsInThePaintPercentage"]) if stats_away["pointsInThePaintPercentage"] is not None else None  # double?
                awayteam_pointssecondchance = parse_int(stats_away["pointsSecondChance"])  # int?

                awayteam_reboundsdefensive = parse_int(stats_away["reboundsDefensive"])  # int?
                awayteam_reboundsoffensive = parse_int(stats_away["reboundsOffensive"])  # int?
                awayteam_reboundspersonal = parse_int(stats_away["reboundsPersonal"])  # int?
                awayteam_reboundsteam = parse_int(stats_away["reboundsTeam"])  # int?
                awayteam_reboundsteamdefensive = parse_int(stats_away["reboundsTeamDefensive"])  # int?
                awayteam_reboundsteamoffensive = parse_int(stats_away["reboundsTeamOffensive"])  # int?
                awayteam_reboundstotal = parse_int(stats_away["reboundsTotal"])  # int?

                awayteam_secondchancepointsattempted = parse_int(stats_away["secondChancePointsAttempted"])  # int?
                awayteam_secondchancepointsmade = parse_int(stats_away["secondChancePointsMade"])  # int?
                awayteam_secondchancepointspercentage = float(stats_away["secondChancePointsPercentage"]) if stats_away["secondChancePointsPercentage"] is not None else None  # double?

                awayteam_steals = parse_int(stats_away["steals"])  # int?
                awayteam_threepointersattempted = parse_int(stats_away["threePointersAttempted"])  # int?
                awayteam_threepointersmade = parse_int(stats_away["threePointersMade"])  # int?
                awayteam_threepointerspercentage = float(stats_away["threePointersPercentage"]) if stats_away["threePointersPercentage"] is not None else None  # double?

                awayteam_timeleading = str(stats_away["timeLeading"])  # Nullable String
                awayteam_timestied = parse_int(stats_away["timesTied"])  # int?
                awayteam_trueshootingattempts = float(stats_away["trueShootingAttempts"]) if stats_away["trueShootingAttempts"] is not None else None  # double?
                awayteam_trueshootingpercentage = float(stats_away["trueShootingPercentage"]) if stats_away["trueShootingPercentage"] is not None else None  # double?

                awayteam_turnovers = parse_int(stats_away["turnovers"])  # int?
                awayteam_turnoversteam = parse_int(stats_away["turnoversTeam"])  # int?
                awayteam_turnoverstotal = parse_int(stats_away["turnoversTotal"])  # int?

                awayteam_twopointersattempted = parse_int(stats_away["twoPointersAttempted"])  # int?
                awayteam_twopointersmade = parse_int(stats_away["twoPointersMade"])  # int?
                awayteam_twopointerspercentage = float(stats_away["twoPointersPercentage"]) if stats_away["twoPointersPercentage"] is not None else None  # double?


                # Define the URL for the POST request
                #url = f"http://localhost:5086/api/teams/"  # Replace with your API endpoint
                url = f"https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/teams/"

                # Define the data payload (JSON)
                payload = {
                    "TeamStatId": team_stat_id,
                    "TeamId": awayteam_id,
                    "GameId": game_id,  # Ensure this variable is defined elsewhere
                    "HomeCourt": home_court,
                    "TeamName": awayteam_name,
                    "TeamCity": awayteam_city,
                    "TeamTricode": awayteam_tricode,
                    "Assists": awayteam_assiststoratio,
                    "AssistsTurnoverRatio": awayteam_assiststoratio,
                    "BenchPoints": awayteam_benchpoints,
                    "BiggestLead": awayteam_biggestlead,
                    "BiggestLeadScore": awayteam_biggestLeadScore,
                    "BiggestScoringRun": awayteam_biggestscoringrun,
                    "BiggestScoringRunScore": awayteam_biggestscoringrunscore,
                    "Blocks": awayteam_blocks,
                    "BlocksReceived": awayteam_blocksreceived,
                    "FastBreakPointsAttempted": awayteam_fastbreakpointsattempted,
                    "FastBreakPointsMade": awayteam_fastbreakpointsmade,
                    "FastBreakPointsPercentage": awayteam_fastbreakpointspercentage,
                    "FieldGoalsAttempted": awayteam_fieldgoalsattempted,
                    "FieldGoalsEffectiveAdjusted": awayteam_fieldgoalseffectiveadjusted,
                    "FieldGoalsMade": awayteam_fieldgoalsmade,
                    "FieldGoalsPercentage": awayteam_fieldgoalspercentage,
                    "FoulsOffensive": awayteam_foulsoffensive,
                    "FoulsDrawn": awayteam_foulsdrawn,
                    "FoulsPersonal": awayteam_foulspersonal,
                    "FoulsTeam": awayteam_foulsteam,
                    "FoulsTechnical": awayteam_foulstechnical,
                    "FoulsTeamTechnical": awayteam_foulsteamtechnical,
                    "FreeThrowsAttempted": awayteam_freethrowsattempted,
                    "FreeThrowsMade": awayteam_freethrowsmade,
                    "FreeThrowsPercentage": awayteam_freethrowspercentage,
                    "LeadChanges": awayteam_leadchanges,
                    "Minutes": awayteam_minutes,
                    "MinutesCalculated": awayteam_minutescalculated,
                    "Points": awayteam_points,
                    "PointsAgainst": awayteam_pointsagainst,
                    "PointsFastBreak": awayteam_pointsfastbreak,
                    "PointsFromTurnovers": awayteam_pointsfromturnovers,
                    "PointsInThePaint": awayteam_pointsinthepaint,
                    "PointsInThePaintAttempted": awayteam_pointsinthepaintattempted,
                    "PointsInThePaintMade": awayteam_pointsinthepaintmade,
                    "PointsInThePaintPercentage": awayteam_pointsinthepaintpercentage,
                    "PointsSecondChance": awayteam_pointssecondchance,
                    "ReboundsDefensive": awayteam_reboundsdefensive,
                    "ReboundsOffensive": awayteam_reboundsoffensive,
                    "ReboundsPersonal": awayteam_reboundspersonal,
                    "ReboundsTeam": awayteam_reboundsteam,
                    "ReboundsTeamDefensive": awayteam_reboundsteamdefensive,
                    "ReboundsTeamOffensive": awayteam_reboundsteamoffensive,
                    "ReboundsTotal": awayteam_reboundstotal,
                    "SecondChancePointsAttempted": awayteam_secondchancepointsattempted,
                    "SecondChancePointsMade": awayteam_secondchancepointsmade,
                    "SecondChancePointsPercentage": awayteam_secondchancepointspercentage,
                    "Steals": awayteam_steals,
                    "ThreePointersAttempted": awayteam_threepointersattempted,
                    "ThreePointersMade": awayteam_threepointersmade,
                    "ThreePointersPercentage": awayteam_threepointerspercentage,
                    "TimeLeading": awayteam_timeleading,
                    "TimesTied": awayteam_timestied,
                    "TrueShootingAttempts": awayteam_trueshootingattempts,
                    "TrueShootingPercentage": awayteam_trueshootingpercentage,
                    "Turnovers": awayteam_turnovers,
                    "TurnoversTeam": awayteam_turnoversteam,
                    "TurnoversTotal": awayteam_turnoverstotal,
                    "TwoPointersAttempted": awayteam_twopointersattempted,
                    "TwoPointersMade": awayteam_twopointersmade,
                    "TwoPointersPercentage": awayteam_twopointerspercentage
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
    return f"Team data processed successfully for {gameId} data."
