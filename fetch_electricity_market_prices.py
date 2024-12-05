# fetch wholesale electricity market prices (real-time LMP) for RTO/ISO regions from 2020 to 2023

import pandas as pd


def get_iso_ne_rt_lmp(years):
    data_frames = []
    for year in years:
        file_path = f"iso_ne_realtime_locational_marginal_prices/isone_lmp_rt_hr_hubs_{year}.csv"
        df = pd.read_csv(
            file_path,
            skiprows=3,
            nrows=8760,
            usecols=range(9),
            parse_dates=["Local Timestamp Eastern Time (Interval Beginning)"],
            index_col="Local Timestamp Eastern Time (Interval Beginning)",
        )
        data_frames.append(df)
    return pd.concat(data_frames)


# test the function
if __name__ == "__main__":
    years = [2021, 2022]
    try:
        data = get_iso_ne_rt_lmp(years)
        print("Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")
