# calculate the NPV of a hydrogen electrolysis project using wind/solar generation data

# calculate amount of hydrogen produced by electrolysis
electricity_input_per_kg_hydrogen = 55.5  # kWh
water_input_per_kg_hydrogen = 3.780  # gallons

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
data, wind_gen_capacity, solar_pv_gen_capacity = (
    fetch_renewables_generation_data_for_years(city, state, years)
)

# Add a 'year' column to the data
data["year"] = pd.to_datetime(data["time"]).dt.year

# Make the 'time' column the index
data.set_index("time", inplace=True)

# Calculate yearly capacity factor for wind and solar
days_per_year = data.groupby("year").size() / 24

yearly_capacity_factor_wind = data.groupby("year")["electricity_wind[kw]"].sum() / (
    wind_gen_capacity * days_per_year * 24
)
print("Yearly Capacity Factor Wind:")
print(yearly_capacity_factor_wind)

yearly_capacity_factor_solar_pv = data.groupby("year")[
    "electricity_solar_pv[kw]"
].sum() / (solar_pv_gen_capacity * days_per_year * 24)
print("Yearly Capacity Factor Solar PV:")
print(yearly_capacity_factor_solar_pv)

yearly_capacity_factor_combined = data.groupby("year")[
    "total_electricity_gen[kw]"
].sum() / ((wind_gen_capacity + solar_pv_gen_capacity) * days_per_year * 24)
print("Yearly Capacity Factor Combined:")
print(yearly_capacity_factor_combined)

# calculate amount of hydrogen produced by electrolysis
hydrogen_production_loss = 0.1  # 10% annual production loss
data["hydrogen_produced[kg]"] = (
    (data["total_electricity_gen[kw]"] * 1 / electricity_input_per_kg_hydrogen)
    * (1 - hydrogen_production_loss)
).round(1)
data["water_consumed[gallons]"] = (
    data["hydrogen_produced[kg]"] * water_input_per_kg_hydrogen
).round(1)

# sum up the total hydrogen produced and water consumed for each year
annual_hydrogen_produced = data.groupby("year")["hydrogen_produced[kg]"].sum().round(1)
daily_average_hydrogen_produced = (
    data.groupby("year")["hydrogen_produced[kg]"].mean().round(1)
)
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
    merged_data["total_electricity_gen[kw]"] * 1
    * merged_data[f"{iso_rto.lower()}_average_lmp[$/MWh]"]
    / 1000
).round(2)

merged_data["cost_of_water[$]"] = (
    merged_data["water_consumed[gallons]"] * 0.01
)  # $0.01 per gallon

annual_cost_of_electricity = (
    merged_data.groupby("year")["cost_of_electricity[$]"].sum().round(2)
)
annual_cost_of_water = merged_data.groupby("year")["cost_of_water[$]"].sum().round(2)

print("Cost of Electricity [$]:")
print(annual_cost_of_electricity)
print("Cost of Water [$]:")
print(annual_cost_of_water)

# npv assumptions
# financial assumptions
project_lifetime = 20  # 20 year project lifetime
discount_rate = 0.1  # 10% discount rate

# # wind plant assumptions
# wind_capex_per_kw = 1500  # $1500 per kW
# wind_itc_credit = 0.3  # 30% investment tax credit
# wind_fixed_yearly_opex_per_kw = 50  # $50 per kW
# wind_variable_yearly_opex_per_kwh = 0.01  # $0.01 per kWh

# # solar PV plant assumptions
# solar_pv_capex_per_kw = 2000  # $2000 per kW
# solar_pv_itc_credit = 0.26  # 26% investment tax credit
# solar_pv_fixed_yearly_opex_per_kw = 100  # $100 per kW
# solar_pv_variable_yearly_opex_per_kwh = 0.02  # $0.02 per kWh

# electrolyzer system plant assumptions
hydrogen_energy_density = 33.33  # 33.33 kWh/kg

electrolyzer_efficiency = hydrogen_energy_density / electricity_input_per_kg_hydrogen

electrolyzer_plant_size_kw = round(
    (wind_gen_capacity + solar_pv_gen_capacity) * electrolyzer_efficiency)

# Calculate the number of hours where hydrogen is produced for each year
hours_hydrogen_production = (data[data["hydrogen_produced[kg]"] > 0].groupby("year").size()) * (1 - hydrogen_production_loss)

electrolyzer_plant_utilization = hours_hydrogen_production / (days_per_year * 24)

# yearly electrolyzer plant revenue assumptions
hydrogen_sale_price_per_kg = 5  # $3 per kg of hydrogen
hydrogen_ptc_credit_per_kg = 3  # $3 per kg of hydrogen

# electrolyzer plant costs
electrolyzer_plant_capex_per_kw = 1000  # $1000 per kW
electrolyzer_plant_fixed_yearly_opex_per_kw = 100  # $100 per kW
electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen = 0.01  # $0.01 per kg of hydrogen

# calculate yearly revenue and costs
annual_hydrogen_revenue = (
    annual_hydrogen_produced * hydrogen_sale_price_per_kg
).round(2)
annual_hydrogen_ptc_credit = (
    annual_hydrogen_produced * hydrogen_ptc_credit_per_kg
).round(2)

annual_electrolyzer_plant_yearly_opex = ((
    electrolyzer_plant_size_kw * electrolyzer_plant_fixed_yearly_opex_per_kw
) + (annual_hydrogen_produced * electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen)).round(2)


