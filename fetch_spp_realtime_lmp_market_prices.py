# fetch wholesale electricity market prices (real-time LMP) for SPP RTO/ISO region

import pandas as pd

# Dictionary to rename columns
column_rename_dict = {
    "Local Timestamp Central Time (Interval Ending)": "local_time_int_end",
    "UTC Timestamp (Interval Ending)": "utc_time_int_end",
    "Local Date": "local_date",
    "Hour Number": "hour_number",
    "North Hub LMP": "north_hub_lmp[$/MWh]",
    "South Hub LMP": "south_hub_lmp[$/MWh]",
}


def get_spp_rt_lmp(years):
    data_frames = []
    for year in years:
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            file_path = f"spp_realtime_locational_marginal_prices/spp_lmp_rt_5min_hubs_{year}{quarter}.csv"
            df = pd.read_csv(
                file_path,
                skiprows=3,
                usecols=range(13),
                parse_dates=["Local Timestamp Central Time (Interval Beginning)"],
                index_col="Local Timestamp Central Time (Interval Beginning)",
            )
            df.rename(columns=column_rename_dict, inplace=True)
            df.index.rename("local_time_int_start", inplace=True)
            df = df[list(column_rename_dict.values())]
            data_frames.append(df)

    combined_df = pd.concat(data_frames)

    # Check for missing hours
    full_range = pd.date_range(
        start=combined_df.index.min(), end=combined_df.index.max(), freq="h"
    )
    missing_hours = full_range.difference(combined_df.index)

    if not missing_hours.empty:
        total_hours = len(full_range)
        missing_percentage = (len(missing_hours) / total_hours) * 100
        print(f"Percentage of missing hourly data: {missing_percentage:.2f}%")

    return combined_df


# test the function
if __name__ == "__main__":
    years = [2020, 2021, 2022, 2023]
    try:
        data = get_spp_rt_lmp(years)
        print("Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")