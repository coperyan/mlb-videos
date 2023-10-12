import os
import pathlib
from twilio.rest import Client

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from .constants import _SEASON_DATES, _DT_FORMAT

_PROJECT_SUBFOLDERS = ["clips", "compilations", "data", "thumbnails", "logs"]
_PURGE_SUBFOLDERS = ["clips", "compilations", "data"]


def yesterday(fmt: str = _DT_FORMAT):
    """Returns yesterday's date

    Parameters
    ----------
        fmt (str, optional): str, default _DT_FORMAT
            datetime format (ex. `%Y-%m-%d`)

    Returns
    -------
        str
            Yesterday formatted as a str
    """
    return (datetime.now() - timedelta(days=1)).strftime(fmt)


def today(fmt: str = _DT_FORMAT):
    """Returns today's date

    Parameters
    ----------
        fmt (str, optional): str, default _DT_FORMAT
            datetime format (ex. `%Y-%m-%d`)

    Returns
    -------
        str
            Today formatted as a str
    """
    return datetime.now().strftime(fmt)


def x_days_ago(num_days: int = 0, fmt: str = _DT_FORMAT):
    """Returns the date x days ago

    Parameters
    ----------
        num_days (int, optional): int, default 0
            number of days to subtract from today
        fmt (str, optional): str, default _DT_FORMAT
            datetime format (ex. `%Y-%m-%d`)

    Returns
    -------
        str
            X days ago formatted as a str
    """
    return (datetime.now() - timedelta(days=num_days)).strftime(fmt)


def x_months_ago(x: int = 0, fmt: str = _DT_FORMAT):
    """Returns the month x months ago

    Parameters
    ----------
        x (int, optional): int, default 0
            number of months to subtract from this month
        fmt (str, optional): str, default _DT_FORMAT
            datetime format (ex. `%Y-%m-%d`)

    Returns
    -------
        str
            X months ago formatted as a str
    """
    today = date.today()
    today_x_months_ago = today - relativedelta(months=x)
    first_day_x_months = today_x_months_ago.replace(day=1)
    today_x_months_ago_next = today - relativedelta(months=x - 1)
    last_day_x_months = today_x_months_ago_next.replace(day=1) - timedelta(days=1)

    return {
        "start_date": first_day_x_months.strftime(fmt),
        "end_date": last_day_x_months.strftime(fmt),
        "month_name": last_day_x_months.strftime("%B"),
        "month_number": int(last_day_x_months.strftime("%m")),
        "year": int(last_day_x_months.strftime("%Y")),
    }


def x_weeks_ago(x: int = 0, fmt: str = _DT_FORMAT):
    """Returns the month x weeks ago

    Parameters
    ----------
        x (int, optional): int, default 0
            number of weeks to subtract from this week
        fmt (str, optional): str, default _DT_FORMAT
            datetime format (ex. `%Y-%m-%d`)

    Returns
    -------
        str
            X weeks ago formatted as a str
    """
    today = date.today()
    start_date = today + timedelta(-today.weekday() - 1, weeks=-x)
    end_date = start_date + timedelta(days=6)

    return {
        "start_date": start_date.strftime(fmt),
        "end_date": end_date.strftime(fmt),
        "week_number": int(start_date.strftime("%W")),
        "year": int(start_date.strftime("%Y")),
    }


def setup_project(project_name: str, project_date: str = today()):
    pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}../projects").mkdir(
        parents=False, exist_ok=True
    )
    pathlib.Path(
        f"{os.path.dirname(os.path.abspath(__file__))}../projects/{project_name}"
    ).mkdir(parents=False, exist_ok=True)
    pathlib.Path(
        f"{os.path.dirname(os.path.abspath(__file__))}../projects/{project_name}/{project_date}"
    ).mkdir(parents=False, exist_ok=True)
    for subfolder in _PROJECT_SUBFOLDERS:
        pathlib.Path(
            f"{os.path.dirname(os.path.abspath(__file__))}../projects/{project_name}/{project_date}/{subfolder}"
        ).mkdir(parents=False, exist_ok=True)
    return f"{os.path.dirname(os.path.abspath(__file__))}../projects/{project_name}/{project_date}"


def make_dirs_from_dict(d, current_dir="./"):
    """Recursive - Builds Directory from Nested Dict

    Parameters
    ----------
        d : _type_
            Nested Dictionary representing directories
        current_dir (str, optional): str, default "./"
            Directory to build folders in
    """
    for key, val in d.items():
        pathlib.Path(os.path.join(current_dir, key)).mkdir(parents=False, exist_ok=True)
        if type(val) == dict:
            make_dirs_from_dict(val, os.path.join(current_dir, key))


def setup_project2(project_name: str, project_date: str = today()):
    """Setup Project Directories

    Parameters
    ----------
        project_name : str
            project name (top level folder name)
        project_date (str, optional): str, default today()
            date of project analysis -- could be month, week, or actual date

    Returns
    -------
        _type_
            Path to local projects folder directory
    """
    project_tree = {
        "projects": {
            f"{project_name}": {
                f"{project_date}": {
                    "clips": None,
                    "compilations": None,
                    "data": None,
                    "logs": None,
                    "thumbnails": None,
                }
            }
        }
    }
    base_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent
    make_dirs_from_dict(project_tree, base_path)
    return base_path / "projects" / project_name / project_date


def purge_project_files(project_name: str, project_date: str = today()):
    project_path = f"{os.path.dirname(os.path.abspath(__file__))}/./projects/{project_name}/{project_date}"
    for subfolder in _PURGE_SUBFOLDERS:
        iter_path = os.path.join(project_path, subfolder)
        for file in os.listdir(iter_path):
            os.remove(os.path.join(iter_path, file))


def get_date_range(start_dt: str, end_dt: str) -> list:
    """Get Date Range

    Parameters
    ----------
        start_dt : str
        end_dt : str

    Returns
    -------
        list
            list of dates (str)
    """
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
    """Sends a message using the Twilio API

    Parameters
    ----------
        to (str, optional): str, default os.environ.get("TWILIO_TO_PHONE")
            phone number to text
        message (str, optional): str, default None
            message to text
    """
    client = Client(os.environ.get("TWILIO_SID"), os.environ.get("TWILIO_TOKEN"))
    message = client.messages.create(
        to=to, from_=os.environ.get("TWILIO_PHONE"), body=message
    )
