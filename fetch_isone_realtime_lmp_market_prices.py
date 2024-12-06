# Fetch wholesale electricity market prices for ISO-NE RTO/ISO region
# Yearly data files with hourly real-time LMP prices are available from 2020-2024
# ISO-NE: https://www.eia.gov/electricity/wholesalemarkets/data.php?rto=isone

import pandas as pd

# ISO-NE
# Dictionary to rename columns
column_rename_isone = {
    "Hour Number": "hour_number",
    "Internal Hub LMP": "isone_average_lmp[$/MWh]",
}


# Function to fetch ISO-NE real-time LMP data
def get_isone_rt_lmp(years):
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
            df.rename(columns=column_rename_isone, inplace=True)
            df.index.rename("local_time_int_start", inplace=True)
            df = df[list(column_rename_isone.values())]
            data_frames[year] = df

            # Check for missing hours for the year
            full_range = pd.date_range(
                start=f"{year}-01-01", end=f"{year}-12-31 23:00:00", freq="h"
            )
            missing_hours = full_range.difference(df.index)

            total_hours = len(full_range)
            missing_percentage = (len(missing_hours) / total_hours) * 100
            print(
                f"Year {year} ISO-NE: Percentage of missing hourly data: {missing_percentage:.2f}%"
            )
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
        isone_data = get_isone_rt_lmp(years)
        print("ISO-NE Data:")
        print(isone_data.head())
        print(isone_data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")
