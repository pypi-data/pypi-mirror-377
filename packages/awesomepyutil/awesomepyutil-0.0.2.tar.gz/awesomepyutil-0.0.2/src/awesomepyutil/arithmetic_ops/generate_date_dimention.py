import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from datetime import date


def generate_date_dimension(start_date: str = "", end_date: str = ""):

    start_date = start_date.replace("/", "-").replace("\\", "-")
    end_date = end_date.replace("/", "-").replace("\\", "-")

    # cur_date = dt.today().strftime("%Y-%m-%d")  # "%Y-%m-%d" "%d-%m-%Y"
    prev_date = (dt.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    next_date = (dt.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    if start_date is None or start_date == "":
        start_date = prev_date
    if end_date is None or end_date == "":
        end_date = next_date

    _start_date = dt.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    _end_date = dt.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    data = dict()
    # data["current_date"] = cur_date
    data["start_date"] = _start_date
    data["end_date"] = _end_date

    # empty dataframe
    # df_empty = pd.DataFrame()

    # use date functionality of pandas dataframe
    date_df = pd.DataFrame({"date_time": pd.date_range(start=_start_date, end=_end_date)})

    # date_df.date_time is pandas series with "date_time" column
    date_df["date"] = date_df.date_time.dt.strftime("%Y-%m-%d")
    date_df["day"] = date_df.date_time.dt.day
    date_df["week_day"] = date_df.date_time.dt.weekday
    date_df["week_name"] = date_df.date_time.dt.day_name()
    date_df["week_of_year"] = date_df.date_time.dt.isocalendar().week
    date_df["month"] = date_df.date_time.dt.month
    date_df["quarter"] = date_df.date_time.dt.quarter
    date_df["year"] = date_df.date_time.dt.year

    # adding date_id column as unique id at 1st position
    date_df.insert(1, "date_id", (date_df.year.astype(str) +
                                  date_df.month.astype(str).str.zfill(2) +
                                  date_df.day.astype(str).str.zfill(2)).astype(int))

    # convert pandas dataframe to python dict
    data["date_dimension"] = str(date_df.loc[:, "date_id":"year"].to_dict())

    return data


if __name__ == "__main__":
    out1 = generate_date_dimension(start_date="2023\\08\\01", end_date="2023\\08\\03")
    out2 = generate_date_dimension(start_date="2023/08/01", end_date="2023/08/03")
    out3 = generate_date_dimension(start_date="2023-08-01", end_date="2023-08-03")
    print(f"out1: {out1}")
    print(f"out2: {out2}")
    print(f"out3: {out3}")
