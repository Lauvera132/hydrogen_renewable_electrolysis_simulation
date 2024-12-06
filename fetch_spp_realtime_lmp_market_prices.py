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
    data_frames = {}
    for year in years:
        yearly_data_frames = []
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            file_path = f"spp_realtime_locational_marginal_prices/spp_lmp_rt_5min_hubs_{year}{quarter}.csv"
            try:
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

                # Add the new column for average LMP
                df['spp_average_lmp[$/MWh]'] = (df['north_hub_lmp[$/MWh]'] + df['south_hub_lmp[$/MWh]']) / 2

                # Select only numeric columns for resampling
                numeric_cols = df.select_dtypes(include='number').columns
                df_hourly = df[numeric_cols].resample('h').mean()

                yearly_data_frames.append(df_hourly)
            except FileNotFoundError:
                print(f"File not found: {file_path}. Skipping this file.")
        
        if yearly_data_frames:
            combined_yearly_df = pd.concat(yearly_data_frames)
            data_frames[year] = combined_yearly_df

            # Check for missing hours for the year
            full_range = pd.date_range(
                start=f'{year}-01-01', end=f'{year}-12-31 23:00:00', freq="h"
            )
            missing_hours = full_range.difference(combined_yearly_df.index)

            if not missing_hours.empty:
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
        data = get_spp_rt_lmp(years)
        print("Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")
