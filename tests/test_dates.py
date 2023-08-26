import os
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

_DT_FORMAT = "%Y-%m-%d"


def x_months_ago(x: int = 0, fmt: str = _DT_FORMAT):
    today = date.today()
    today_x_months_ago = today - relativedelta(months=x)
    first_day_x_months = today_x_months_ago.replace(day=1)
    today_x_months_ago_next = today - relativedelta(months=x - 1)
    last_day_x_months = today_x_months_ago_next.replace(day=1) - timedelta(days=1)

    return {
        "start_date": first_day_x_months.strftime(fmt),
        "end_date": last_day_x_months.strftime(fmt),
        "month_name": last_day_x_months.strftime("%B"),
        "month_number": int(last_day_x_months.strftime("%-m")),
        "year": int(last_day_x_months.strftime("%Y")),
    }


def x_weeks_ago(x: int = 0, fmt: str = _DT_FORMAT):
    today = date.today()
    start_date = today + timedelta(-today.weekday() - 1, weeks=-x)
    end_date = start_date + timedelta(days=6)

    return {
        "start_date": start_date.strftime(fmt),
        "end_date": end_date.strftime(fmt),
        "week_number": int(start_date.strftime("%W")),
        "year": int(start_date.strftime("%Y")),
    }
