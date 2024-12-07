# calculate the NPV of a hydrogen electrolysis project using wind/solar generation data

# calculate amount of hydrogen produced by electrolysis
# 55.5 kwh of electricity per kg of hydrogen
# 3.780 gallons of water per kg of hydrogen

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fetch_hourly_generation_by_location import (
    fetch_renewables_generation_data_for_years,
)

# Prompt user for input
# city = input("Please enter the US city: ")
city = "Houston"
# state = input("Please enter the US state abbreviation: ")
state = "TX"
years = [2021, 2022]

# determine electricity available from wind/solar hourly generation for user location
data = fetch_renewables_generation_data_for_years(city, state, years)
data["total_electricity_gen[kwh]"] = (
    data["electricity_wind[kw]"] + data["electricity_solar_pv[kw]"]
) * 1  # kw * 1 hr = kwh

# Add a 'year' column to the data
data["year"] = pd.to_datetime(data["time"]).dt.year

# Make the 'time' column the index
data.set_index("time", inplace=True)

# Calculate yearly capacity factor for wind and solar
data["capacity_factor_wind"] = data["electricity_wind[kw]"] / (1500)
data["capacity_factor_solar_pv"] = data["electricity_solar_pv[kw]"] / (1000)
data["capacity_factor_combined"] = data["total_electricity_gen[kwh]"] / (2500)
yearly_capacity_factor_wind = data.groupby("year")["electricity_wind[kw]"].sum() / (1500 * 8760)
print("Yearly Capacity Factor Wind:")
print(yearly_capacity_factor_wind)
yearly_capacity_factor_solar_pv = data.groupby("year")["electricity_solar_pv[kw]"].sum() / (1000 * 8760)
print("Yearly Capacity Factor Solar PV:")
print(yearly_capacity_factor_solar_pv)
yearly_capacity_factor_combined = data.groupby("year")["total_electricity_gen[kwh]"].sum() / (2500 * 8760)
print("Yearly Capacity Factor Combined:")
print(yearly_capacity_factor_combined)

# calculate amount of hydrogen produced by electrolysis
hydrogen_production_loss = 0.1  # 10% annual production loss
data["hydrogen_produced[kg]"] = (
    (data["total_electricity_gen[kwh]"] / 55.5) * (1 - hydrogen_production_loss)
).round(1)
data["water_consumed[gallons]"] = (data["hydrogen_produced[kg]"] * 3.780).round(1)

# sum up the total hydrogen produced and water consumed for each year
annual_hydrogen_produced = data.groupby("year")["hydrogen_produced[kg]"].sum().round(1)
daily_average_hydrogen_produced = data.groupby("year")["hydrogen_produced[kg]"].mean().round(1)
annual_water_consumed = data.groupby("year")["water_consumed[gallons]"].sum().round(1)
print("Hydrogen Production [kg}:")
print(annual_hydrogen_produced)
print("Water Consumed [gallons]:")
print(annual_water_consumed)

# import electricity cost data
from fetch_rto_iso_from_state import get_iso_rto
from fetch_rto_iso_realtime_electricity_prices import get_rto_iso_rt_lmp

iso_rto = get_iso_rto(state)
print(iso_rto)
price_data = get_rto_iso_rt_lmp(iso_rto, years)

# merge the data
if data.index.name == "time" and price_data.index.name == "local_time_int_start":
    merged_data = data.merge(price_data, left_index=True, right_index=True)
else:
    missing_indices = []
    if data.index.name != "time":
        missing_indices.append("time index in data")
    if price_data.index.name != "local_time_int_start":
        missing_indices.append("local_time_int_start index in price_data")
    raise KeyError(f"Missing indices for merging: {', '.join(missing_indices)}")

# calculate cost of electricity and water used
merged_data["cost_of_electricity[$]"] = (
    merged_data["total_electricity_gen[kwh]"] * merged_data[f"{iso_rto.lower()}_average_lmp[$/MWh]"] / 1000
).round(2)
merged_data["cost_of_water[$]"] = merged_data["water_consumed[gallons]"] * 0.01 # $0.01 per gallon
annual_cost_of_electricity = merged_data.groupby("year")["cost_of_electricity[$]"].sum().round(2)
annual_cost_of_water = merged_data.groupby("year")["cost_of_water[$]"].sum().round(2)
print("Cost of Electricity [$]:")
print(annual_cost_of_electricity)
print("Cost of Water [$]:")
print(annual_cost_of_water)



