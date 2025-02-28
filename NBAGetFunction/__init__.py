import logging
import azure.functions as func
from ArenaRequest import run as script1_run
from BettingLinesRequest import run as script2_run
from GameRequest import run as script3_run
from OfficialsRequest import run as script4_run
from PeriodRequest import run as script5_run
from PlayerandStatsRequest import run as script6_run
from TeamRequest import run as script7_run

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
