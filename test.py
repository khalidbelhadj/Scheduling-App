import datetime

def get_current_week():
    today = datetime.date(2024, 2, 4)
    for i, date in enumerate(dates):
        if today < datetime.datetime.strptime(date, "%Y-%m-%d").date():
            return i
    return -1

dates = [
    "2024-01-15",
    "2024-01-22",
    "2024-01-29",
    "2024-02-05",
    "2024-02-12",
    "2024-02-19",
    "2024-02-26",
    "2024-03-04",
    "2024-03-11",
    "2024-03-18",
    "2024-03-25",
    "2024-04-01"
]

current_week = get_current_week()
if current_week != -1:
    print("Today's date falls in Week", current_week)
else:
    print("Today's date does not fall in any week")