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

# calculate amount of hydrogen produced by electrolysis
data["hydrogen_produced[kg]"] = (data["total_electricity_gen[kwh]"] / 55.5).round(1)
data["water_consumed[gallons]"] = (data["hydrogen_produced[kg]"] * 3.780).round(1)

# sum up the total hydrogen produced and water consumed for each year
hydrogen_production_loss = 0.1  # 10% annual production loss
annual_hydrogen_produced = data.groupby("year")["hydrogen_produced[kg]"].sum() * (
    1 - hydrogen_production_loss)
annual_water_consumed = data.groupby("year")["water_consumed[gallons]"].sum() * (
    1 - hydrogen_production_loss)
print("Hydrogen Production [kg}:")
print(annual_hydrogen_produced)
print("Water Consumed [gallons]:")
print(annual_water_consumed)

# import electricity cost data
from fetch_rto_iso_from_state import (get_iso_rto)
from fetch_rto_iso_realtime_electricity_prices import (get_rto_iso_rt_lmp)
iso_rto = get_iso_rto(state)
print(iso_rto)
price_data = get_rto_iso_rt_lmp(iso_rto, years)



