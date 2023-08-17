import os
import pathlib
from twilio.rest import Client

from datetime import datetime, date, timedelta

from constants import _SEASON_DATES, _DT_FORMAT

_PROJECT_SUBFOLDERS = ["clips", "compilations", "data", "thumbnails", "logs"]
_PURGE_SUBFOLDERS = ["clips", "compilations", "data"]


def yesterday(fmt: str = _DT_FORMAT):
    return (datetime.now() - timedelta(days=1)).strftime(fmt)


def today(fmt: str = _DT_FORMAT):
    return datetime.now().strftime(fmt)


def setup_project(project_name: str, project_date: str = today()):
    pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}/../projects").mkdir(
        parents=False, exist_ok=True
    )
    pathlib.Path(
        f"{os.path.dirname(os.path.abspath(__file__))}/../projects/{project_name}"
    ).mkdir(parents=False, exist_ok=True)
    pathlib.Path(
        f"{os.path.dirname(os.path.abspath(__file__))}/../projects/{project_name}/{today()}"
    ).mkdir(parents=False, exist_ok=True)
    for subfolder in _PROJECT_SUBFOLDERS:
        pathlib.Path(
            f"{os.path.dirname(os.path.abspath(__file__))}/../projects/{project_name}/{today()}/{subfolder}"
        ).mkdir(parents=False, exist_ok=True)
    return f"{os.path.dirname(os.path.abspath(__file__))}/../projects/{project_name}/{today()}"


def purge_project_files(project_name: str, project_date: str = today()):
    project_path = f"{os.path.dirname(os.path.abspath(__file__))}/../projects/{project_name}/{today()}"
    for subfolder in _PURGE_SUBFOLDERS:
        iter_path = os.path.join(project_path, subfolder)
        for file in os.listdir(iter_path):
            os.remove(os.path.join(iter_path, file))


def get_date_range(start_dt: str, end_dt: str) -> list:
    start_date = datetime.strptime(start_dt, _DT_FORMAT).date()
    end_date = datetime.strptime(end_dt, _DT_FORMAT).date()
    max_date = datetime.strptime(yesterday(), _DT_FORMAT).date()

    dates = []
    iter_date = start_date

    while iter_date <= end_date:
        season_start, season_end = _SEASON_DATES.get(iter_date.year)

        if iter_date < season_start:
            iter_date = season_start
        elif iter_date > season_end:
            iter_date, _ = _SEASON_DATES.get(iter_date.year + 1)

        if iter_date > end_date or iter_date > max_date:
            break
        else:
            dates.append(iter_date.strftime(_DT_FORMAT))
            iter_date += timedelta(days=1)

    return dates


def twilio_message(to: str = os.environ.get("TWILIO_TO_PHONE"), message: str = None):
    client = Client(os.environ.get("TWILIO_SID"), os.environ.get("TWILIO_TOKEN"))
    message = client.messages.create(
        to=to, from_=os.environ.get("TWILIO_PHONE"), body=message
    )
