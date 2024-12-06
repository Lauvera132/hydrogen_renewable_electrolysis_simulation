# Fetch wholesale electricity market prices for ISO-NE RTO/ISO region
# Yearly data files with hourly real-time LMP prices are available from 2020-2024
# MISO: https://www.eia.gov/electricity/wholesalemarkets/data.php?rto=miso


import pandas as pd

# MISO
# Dictionary to rename columns
column_rename_miso = {
    "Hour Number": "hour_number",
    "Arkansas Hub LMP": "arkansas_lmp[$/MWh]",
    "Illinois Hub LMP": "illinois_lmp[$/MWh]",
    "Indiana Hub LMP": "indiana_lmp[$/MWh]",
    "Louisiana Hub LMP": "louisiana_lmp[$/MWh]",
    "Michigan Hub LMP": "michigan_lmp[$/MWh]",
    "Minnesota Hub LMP": "minnesota_lmp[$/MWh]",
    "Mississippi Hub LMP": "mississippi_lmp[$/MWh]",
    "Texas Hub LMP": "texas_lmp[$/MWh]",
}

# Function to fetch MISO real-time LMP data
def get_miso_rt_lmp(years):
    data_frames = {}

    for year in years:
        file_path = f"miso_realtime_locational_marginal_prices/miso_lmp_rt_hr_hubs_{year}.csv"
        try:
            df = pd.read_csv(
                file_path,
                skiprows=3,
                usecols=range(13),
                parse_dates=["Local Timestamp Eastern Standard Time (Interval Beginning)"],
                index_col="Local Timestamp Eastern Standard Time (Interval Beginning)",
            )
            df.rename(columns=column_rename_miso, inplace=True)
            df.index.rename("local_time_int_start", inplace=True)
            df = df[list(column_rename_miso.values())]

            # Add a new column for average LMP
            df["miso_average_lmp[$/MWh]"] = (
                df["arkansas_lmp[$/MWh]"]
                + df["illinois_lmp[$/MWh]"]
                + df["indiana_lmp[$/MWh]"]
                + df["louisiana_lmp[$/MWh]"]
                + df["michigan_lmp[$/MWh]"]
                + df["minnesota_lmp[$/MWh]"]
                + df["mississippi_lmp[$/MWh]"]
                + df["texas_lmp[$/MWh]"]
            ) / 8

            data_frames[year] = df

            # Check for missing hours for the year
            full_range = pd.date_range(
                start=f"{year}-01-01", end=f"{year}-12-31 23:00:00", freq="h"
            )
            missing_hours = full_range.difference(df.index)

            total_hours = len(full_range)
            missing_percentage = (len(missing_hours) / total_hours) * 100
            print(
                f"Year {year} MISO: Percentage of missing hourly data: {missing_percentage:.2f}%"
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
        miso_data = get_miso_rt_lmp(years)
        print("MISO Data:")
        print(miso_data.head())
        print(miso_data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")
