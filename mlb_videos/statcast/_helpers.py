import re
import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from mlb_videos.constants import DATE_FORMAT, SEASON_DATES

_DF_DATE_FORMATS = [
    (re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"), "%Y-%m-%d"),
    (
        re.compile(r"^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$"),
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ),
]


def get_date(
    days_ago: int = None,
    weeks_ago: int = None,
    months_ago: int = None,
    years_ago: int = None,
    fmt: str = DATE_FORMAT,
):
    if days_ago:
        return (datetime.now() - timedelta(days=days_ago)).strftime(fmt)
    elif weeks_ago:
        today = date.today()
        start_date = today + timedelta(-today.weekday() - 1, weeks=-weeks_ago)
        end_date = start_date + timedelta(days=6)

        return {
            "start_date": start_date.strftime(fmt),
            "end_date": end_date.strftime(fmt),
            "week_number": int(start_date.strftime("%W")),
            "year": int(start_date.strftime("%Y")),
        }
    elif months_ago:
        today = date.today()
        today_x_months_ago = today - relativedelta(months=x)
        first_day_x_months = today_x_months_ago.replace(day=1)
        today_x_months_ago_next = today - relativedelta(months=months_ago - 1)
        last_day_x_months = today_x_months_ago_next.replace(day=1) - timedelta(days=1)

        return {
            "start_date": first_day_x_months.strftime(fmt),
            "end_date": last_day_x_months.strftime(fmt),
            "month_name": last_day_x_months.strftime("%B"),
            "month_number": int(last_day_x_months.strftime("%m")),
            "year": int(last_day_x_months.strftime("%Y")),
        }
    elif years_ago:
        today = date.today()
        x_years_ago = today - relativedelta(years=years_ago)
        return x_years_ago.strftime(fmt)


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
    start_date = datetime.strptime(start_dt, DATE_FORMAT).date()
    end_date = datetime.strptime(end_dt, DATE_FORMAT).date()
    max_date = datetime.strptime(get_date(days_ago=1), DATE_FORMAT).date()

    dates = []
    iter_date = start_date

    while iter_date <= end_date:
        season_start, season_end = SEASON_DATES.get(iter_date.year)

        if iter_date < season_start:
            iter_date = season_start
        elif iter_date > season_end:
            iter_date, _ = SEASON_DATES.get(iter_date.year + 1)

        if iter_date > end_date or iter_date > max_date:
            break
        else:
            dates.append(iter_date.strftime(DATE_FORMAT))
            iter_date += timedelta(days=1)

    return dates


def parse_dates(df: pd.DataFrame, strcol: str, fieldval) -> pd.DataFrame:
    for date_regex, date_format in _DF_DATE_FORMATS:
        if isinstance(fieldval, str) and date_regex.match(fieldval):
            df[strcol] = df[strcol].apply(
                pd.to_datetime, errors="ignore", format=date_format
            )
            df[strcol] = df[strcol].convert_dtypes(convert_string=False)
            break
    return df
