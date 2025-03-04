import logging
import azure.functions as func
import requests
import time
import functools
import time

# Define the retry decorator and patch requests.get
def retry(max_retries=3, delay=2):
    """Retry decorator for transient errors."""
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Attempt {attempt} failed: {e}")
                    if attempt == max_retries:
                        raise
                    time.sleep(delay)
        return wrapper_retry
    return decorator_retry

requests.get = retry(max_retries=3, delay=2)(requests.get)

from .ArenaRequest import run as script1_run
from .BettingLinesRequest import run as script2_run
from .GameRequest import run as script3_run
from .OfficialsRequest import run as script4_run
from .PeriodRequest import run as script5_run
from .PlayerandStatsRequest import run as script6_run
from .TeamRequest import run as script7_run

#wake up the API
url = 'https://nba-bet-api-gpafdhhmg9bxgbce.centralus-01.azurewebsites.net/api/arenas/'
max_attempts = 5

for attempt in range(1, max_attempts + 1):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        print("API call successful!")
        break  # Exit the loop if successful
    except requests.exceptions.RequestException as e:
        print(f"API call attempt {attempt} failed: {e}")
        if attempt < max_attempts:
            time.sleep(5)  # Wait 5 seconds before the next try
        else:
            print("Exceeded maximum attempts. Exiting.")

def main(myTimer: func.TimerRequest) -> None:
    logging.info("Azure Function started.")

    Arenas = script1_run()
    BettingLines = script2_run()
    Games = script3_run()
    Officials = script4_run()
    Periods = script5_run()
    PlayerandStats = script6_run()
    Teams = script7_run()

    logging.info(f"Results: {Arenas}, {BettingLines}, {Games}, {Officials}, {Periods}, {PlayerandStats}, {Teams}")
    logging.info("Azure Function execution finished.")
