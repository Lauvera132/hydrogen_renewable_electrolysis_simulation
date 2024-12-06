# fetch wholesale electricity market prices (real-time LMP) for ISO-NE RTO/ISO region

import pandas as pd

# Dictionary to rename columns
column_rename_dict = {
    "Local Timestamp Eastern Time (Interval Ending)": "local_time_int_end",
    "UTC Timestamp (Interval Ending)": "utc_time_int_end",
    "Local Date": "local_date",
    "Hour Number": "hour_number",
    "Internal Hub LMP": "average_hub_lmp[$/MWh]",
}

def get_iso_ne_rt_lmp(years):
    data_frames = {}
    
    for year in years:
        file_path = f"iso_ne_realtime_locational_marginal_prices/isone_lmp_rt_hr_hubs_{year}.csv"
        try:
            df = pd.read_csv(
                file_path,
                skiprows=3,
                usecols=range(9),
                parse_dates=["Local Timestamp Eastern Time (Interval Beginning)"],
                index_col="Local Timestamp Eastern Time (Interval Beginning)",
            )
            df.rename(columns=column_rename_dict, inplace=True)
            df.index.rename("local_time_int_start", inplace=True)
            df = df[list(column_rename_dict.values())]
            data_frames[year] = df

            # Check for missing hours for the year
            full_range = pd.date_range(
                start=f'{year}-01-01', end=f'{year}-12-31 23:00:00', freq="h"
            )
            missing_hours = full_range.difference(df.index)

            if not missing_hours.empty:
                total_hours = len(full_range)
                missing_percentage = (len(missing_hours) / total_hours) * 100
                print(f"Year {year}: Percentage of missing hourly data: {missing_percentage:.2f}%")
        except FileNotFoundError:
            print(f"File not found: {file_path}. Skipping this file.")
    
    if data_frames:
        combined_df = pd.concat(data_frames.values())
        return combined_df
    else:
        print("No data frames to combine. All files might be missing.")
        return pd.DataFrame()

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
