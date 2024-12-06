# fetch wholesale electricity market prices ERCOT RTO/ISO region
# Quarterly data files are available for 15 minute time intervals
# https://www.eia.gov/electricity/wholesalemarkets/data.php?rto=ercot

import pandas as pd

#ERCOT
# Dictionary to rename columns
column_rename_dict = {
    "Local Timestamp Central Time (Interval Ending)": "local_time_int_end",
    "UTC Timestamp (Interval Ending)": "utc_time_int_end",
    "Local Date": "local_date",
    "Hour Number": "hour_number",
    "Bus average LMP": "bus_average_lmp[$/MWh]",
    "Houston LMP": "houston_lmp[$/MWh]",
    "Hub average LMP": "ercot_average_lmp[$/MWh]",
    "North LMP": "north_lmp[$/MWh]",
    "Panhandle LMP": "panhandle_lmp[$/MWh]",
    "South LMP": "south_lmp[$/MWh]",
    "West LMP": "west_lmp[$/MWh]",
}

def get_ercot_rt_lmp(years):
    data_frames = {}
    for year in years:
        yearly_data_frames = []
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            file_path = f"ercot_realtime_locational_marginal_prices/ercot_lmp_rt_15min_hubs_{year}{quarter}.csv"
            try:
                df = pd.read_csv(
                    file_path,
                    skiprows=3,
                    usecols=range(12),
                    parse_dates=["Local Timestamp Central Time (Interval Beginning)"],
                    index_col="Local Timestamp Central Time (Interval Beginning)",
                )
                df.rename(columns=column_rename_dict, inplace=True)
                df.index.rename("local_time_int_start", inplace=True)
                df = df[list(column_rename_dict.values())]

                # Select only numeric columns for resampling
                numeric_columns = df.select_dtypes(include=[float, int]).columns
                df_hourly = df[numeric_columns].resample("h").mean()

                yearly_data_frames.append(df_hourly)
            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping this file.")
        
        if yearly_data_frames:
            combined_yearly_df = pd.concat(yearly_data_frames)
            data_frames[year] = combined_yearly_df

            # Check for missing hours for the year
            full_range = pd.date_range(
                start=f'{year}-01-01', end=f'{year}-12-31 23:45:00', freq="h"
            )
            missing_hours = full_range.difference(combined_yearly_df.index)

            total_hours = len(full_range)
            missing_percentage = (len(missing_hours) / total_hours) * 100
            print(f"Year {year}: Percentage of missing hourly data: {missing_percentage:.2f}%")
        else:
            print(f"No data frames to combine for year {year}. All files might be missing.")

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
        data = get_ercot_rt_lmp(years)
        print("ERCOT Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")