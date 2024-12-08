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
years = [2021, 2022, 2023]

# determine electricity available from wind/solar hourly generation for user location
data, wind_gen_capacity, solar_pv_gen_capacity = (
    fetch_renewables_generation_data_for_years(city, state, years)
)

# Make the 'time' column the index
data.set_index("time", inplace=True)

# Add a 'year' column to the data
data["year"] = data.index.year

# Calculate yearly capacity factor for wind and solar
days_per_year = data.groupby("year").size() / 24

# Remove any years from data that have less than 310 days
valid_years = days_per_year[days_per_year >= 310].index
data = data[data["year"].isin(valid_years)]

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
data.loc[:, "hydrogen_produced[kg]"] = (
    (data["total_electricity_gen[kw]"] * 1 / electricity_input_per_kg_hydrogen)
    * (1 - hydrogen_production_loss)
).round(1)
data.loc[:, "water_consumed[gallons]"] = (
    data["hydrogen_produced[kg]"] * water_input_per_kg_hydrogen
).round(1)

# sum up the total hydrogen produced and water consumed for each year
annual_hydrogen_produced = data.groupby("year")["hydrogen_produced[kg]"].sum().round(1)
daily_average_hydrogen_produced = (
    data.groupby("year")["hydrogen_produced[kg]"].mean().round(1)
)
annual_hydrogen_produced_average = annual_hydrogen_produced.mean().round(1)

annual_water_consumed = data.groupby("year")["water_consumed[gallons]"].sum().round(1)
annual_water_consumed_average = annual_water_consumed.mean().round(1)

print("Annual Hydrogen Production [kg}:")
print(annual_hydrogen_produced)
print("Water Consumed [gallons]:")
print(annual_water_consumed)

# import electricity cost data
from fetch_rto_iso_from_state import get_iso_rto
from fetch_rto_iso_realtime_electricity_prices import get_rto_iso_rt_lmp

iso_rto = get_iso_rto(state)
print("ISO/RTO:")
print(iso_rto)
price_data = get_rto_iso_rt_lmp(iso_rto, years)

# merge the wind and solar generation with price data
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

print("Annual Cost of Electricity [$]:")
print(annual_cost_of_electricity)
print("Annual Cost of Water [$]:")
print(annual_cost_of_water)

# Net Present Value (NPV) Assumptions

# financial assumptions
project_lifetime = 20  # 20 year project lifetime
discount_rate = 0.1  # 10% discount rate
total_income_tax_rate = 0.21  # 25% total income tax rate
project_start_year = 2020

# electrolyzer system plant assumptions
hydrogen_energy_density = 33.33  # 33.33 kWh/kg
electrolyzer_efficiency = hydrogen_energy_density / electricity_input_per_kg_hydrogen
electrolyzer_plant_size_kw = round(
    (wind_gen_capacity + solar_pv_gen_capacity) * yearly_capacity_factor_combined.mean() * electrolyzer_efficiency)
print(f"Electrolyzer Plant Size [kW]: {electrolyzer_plant_size_kw}")

# Calculate the number of hours where hydrogen is produced for each year
hours_hydrogen_production = (data[data["hydrogen_produced[kg]"] > 0].groupby("year").size()) * (1 - hydrogen_production_loss)
electrolyzer_plant_utilization = hours_hydrogen_production / (days_per_year * 24)

# yearly electrolyzer plant revenue assumptions
hydrogen_sale_price_per_kg = 5  # $5 per kg of hydrogen
hydrogen_ptc_credit_per_kg = 3  # $3 per kg of hydrogen

# electrolyzer plant costs
electrolyzer_plant_capex_per_kw = 1000  # $1000 per kW
electrolyzer_plant_fixed_yearly_opex_per_kw = 100  # $100 per kW
electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen = 0.01  # $0.01 per kg of hydrogen

# calculate yearly revenue and costs
annual_hydrogen_sales_revenue = (
    annual_hydrogen_produced * hydrogen_sale_price_per_kg
).round(2)
print("Annual Hydrogen Sales Revenue [$]:")
print(annual_hydrogen_sales_revenue)

annual_income_tax = total_income_tax_rate * annual_hydrogen_sales_revenue
print("Annual Income Tax [$]:")
print(annual_income_tax)

annual_electrolyzer_plant_yearly_opex = ((
    electrolyzer_plant_size_kw * electrolyzer_plant_fixed_yearly_opex_per_kw
) + (annual_hydrogen_produced * electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen)).round(2)
print("Annual Electrolyzer Plant Yearly OPEX [$]:")
print(annual_electrolyzer_plant_yearly_opex)

# Calculate annual cash flows
annual_cash_flows = []
for year in range(1, project_lifetime + 1):
    if year <= len(years):
        annual_hydrogen_ptc_credit = (
            annual_hydrogen_produced * hydrogen_ptc_credit_per_kg
        ).round(2)
        annual_revenue = annual_hydrogen_sales_revenue + annual_hydrogen_ptc_credit - annual_income_tax
        annual_costs = annual_electrolyzer_plant_yearly_opex + annual_cost_of_electricity + annual_cost_of_water 
    else:
        annual_revenue = annual_hydrogen_sales_revenue.mean() + (annual_hydrogen_produced.mean() * hydrogen_ptc_credit_per_kg) - annual_income_tax.mean()
        annual_costs = annual_electrolyzer_plant_yearly_opex.mean() + annual_cost_of_electricity.mean() + annual_cost_of_water.mean()
    
    annual_cash_flow = annual_revenue - annual_costs
    annual_cash_flows.append(annual_cash_flow)

# Calculate NPV
npv = sum([cf / (1 + discount_rate) ** year for year, cf in enumerate(annual_cash_flows, start=1)])

print(f"Net Present Value (NPV): ${npv:.2f}")
