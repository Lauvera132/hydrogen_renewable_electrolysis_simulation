# fetch wholesale electricity market prices (real-time LMP) for RTO/ISO regions from 2020 to 2023

import pandas as pd


def get_iso_ne_rt_lmp(years):
    data_frames = []
    column_rename_dict = {
        "Local Timestamp Eastern Time (Interval Beginning)": "local_time_int_start",
        "Local Timestamp Eastern Time (Interval Ending)": "local_time_int_end",
        "UTC Timestamp (Interval Ending)": "utc_time_int_end",
        "Local Date": "local_date",
        "Hour Number": "hour_number",
        "Internal Hub LMP": "hub_lmp[$/MWh]",
    }
    
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
        df.rename(columns=column_rename_dict, inplace=True)
        data_frames.append(df)
    
    combined_df = pd.concat(data_frames)
    
    # Check for missing hours
    full_range = pd.date_range(start=combined_df.index.min(), end=combined_df.index.max(), freq='h')
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
        data = get_iso_ne_rt_lmp(years)
        print("Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")
