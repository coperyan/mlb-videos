try:
    import os
    import time

    import traceback
    import sys

    print("About to switch dirs")
    # time.sleep(5)

    print(os.getcwd())
    time.sleep(5)

    os.chdir(r"C:/Users/rcope/Documents/Dev/mlb_videos/mlb_videos")

    sys.path.append(f"C:/Users/rcope/Documents/Dev/mlb_videos/mlb_videos")

    print("About to import logs dirs")
    # time.sleep(5)

    import logging
    import logging.config

    print("About to import utils")
    # time.sleep(5)

    from utils import setup_project, yesterday, twilio_message

    # yesterday_title = yesterday("%B %d, %Y")
    yesterday_title = "August 15, 2023"

    _PROJECT_NAME = "worst_calls_yesterday"
    project_path = setup_project(_PROJECT_NAME, "2023-08-15")

    logging.config.fileConfig(
        "../logging.ini", defaults={"project_name": _PROJECT_NAME}
    )
    logger = logging.getLogger(__name__)

    print("About to import mlb client")
    time.sleep(5)

    from client import MLBVideoClient

    def main():
        vid = MLBVideoClient(
            project_name=_PROJECT_NAME,
            project_path=project_path,
            # start_date=yesterday(),
            # end_date=yesterday(),
            start_date="2023-08-15",
            end_date="2023-08-15",
            enable_cache=False,
            game_info=False,
            player_info=False,
            team_info=False,
            analysis=["umpire_calls"],
            queries=None,
            steps=[
                {
                    "type": "query",
                    "params": {"query": "description in ('called_strike','ball')"},
                },
                {
                    "type": "query",
                    "params": {"query": "release_speed >= 65"},
                },
                {
                    "type": "query",
                    "params": {"query": "total_miss >= 3"},
                },
                {
                    "type": "rank",
                    "params": {
                        "name": "total_miss_rank",
                        "group_by": None,
                        "fields": ["total_miss"],
                        "ascending": [False],
                        "keep_sort": True,
                    },
                },
                {"type": "query", "params": {"query": "total_miss_rank <= 25"}},
            ],
            search_filmroom=True,
            filmroom_params={"feed": "Best", "download": True},
            build_compilation=True,
            # compilation_params={"metric_caption": "launch_speed"},
            youtube_upload=True,
            youtube_params={
                "title": f"MLB Umpires | Worst Calls ({yesterday_title})",
                "description": f"Here are the worst calls from yesterday's game(s) on yesterday_title.",
                "tags": ["umpires", "angel hernandez", "bad baseball calls"],
                "playlist": "Umpires - Worst Calls",
                # "thumbnail": "resources/acuna.jpg",
            },
            purge_files=False,
        )

    if __name__ == "__main__":
        try:
            main()
            twilio_message(f"New video successfully uploaded for {_PROJECT_NAME}..")
        except Exception as e:
            logging.info(f"Exception: {e}")
            twilio_message(f"{_PROJECT_NAME} Pipeline Failed: {e}")

except Exception as e:
    print(e)
    print(traceback.format_exc())
    time.sleep(30)
    # or
    # print(sys.exc_info()[2])
