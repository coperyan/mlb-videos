import os
import pathlib
from datetime import datetime, date, timedelta

from .constants import _SEASON_DATES, _DT_FORMAT

_PROJECT_SUBFOLDERS = ["clips", "compilations", "data", "thumbnails", "logs"]


def yesterday():
    return (datetime.now() - timedelta(days=1)).strftime(_DT_FORMAT)


def today():
    return datetime.now().strftime(_DT_FORMAT)


def setup_project(project_name: str):
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


def purge_project_files(project_name: str):
    for subfolder in _PROJECT_SUBFOLDERS:
        return None


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
