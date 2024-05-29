from datetime import datetime, timedelta

def add_one_month(date):
    month = date.month + 1
    year = date.year
    if month > 12:
        month -= 12
        year += 1
    try:
        return date.replace(month=month, year=year)
    except ValueError:
        next_month = datetime(year, month, 1)
        return next_month - timedelta(days=1)

def add_one_year(date):
    try:
        return date.replace(year=date.year + 1)
    except ValueError:
        return date + (datetime(date.year + 1, 1, 1) - datetime(date.year, 1, 1))
