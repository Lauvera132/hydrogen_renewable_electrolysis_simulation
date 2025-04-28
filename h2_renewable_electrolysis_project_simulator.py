# calculate the NPV of a hydrogen electrolysis project using wind/solar generation data

# calculate amount of hydrogen produced by electrolysis
# sourced from NREL H2A-Lite: Hydrogen Analysis Lite Production Model
# https://www.nrel.gov/hydrogen/h2a-lite.html
electricity_input_per_kg_hydrogen = 55.5  # kWh
water_input_per_kg_hydrogen = 3.780  # gallons

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fetch_hourly_generation_by_location import (
    fetch_renewables_generation_data_for_years,
)

# Prompt user for input
city = input("Please enter the US city name: ")
# city = "Houston"
state = input("Please enter the US state 2-letter abbreviation: ")
# state = "TX"
years = [
    2021,
    2022,
    2023,
]  # years of available historical data; this can be adjusted when more data is available
print("Historical Data Available for Years: ", years)
print("Processing expected to take 30 sec...")

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
# print("Yearly Capacity Factor Wind:")
# print(yearly_capacity_factor_wind)

yearly_capacity_factor_solar_pv = data.groupby("year")[
    "electricity_solar_pv[kw]"
].sum() / (solar_pv_gen_capacity * days_per_year * 24)
# print("Yearly Capacity Factor Solar PV:")
# print(yearly_capacity_factor_solar_pv)

yearly_capacity_factor_combined = data.groupby("year")[
    "total_electricity_gen[kw]"
].sum() / ((wind_gen_capacity + solar_pv_gen_capacity) * days_per_year * 24)
average_yearly_capacity_factor_combined = yearly_capacity_factor_combined.mean() * 100
print(
    f"Average Yearly Combined Capacity Factor for Wind/Solar: {average_yearly_capacity_factor_combined:.2f}%"
)
# print(yearly_capacity_factor_combined)

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

# print("Annual Hydrogen Production [kg}:")
# print(annual_hydrogen_produced)
# print("Water Consumed [gallons]:")
# print(annual_water_consumed)

# import electricity cost data
from fetch_rto_iso_from_state import get_iso_rto
from fetch_rto_iso_realtime_electricity_prices import get_rto_iso_rt_lmp
import sys

iso_rto = get_iso_rto(state)
print(f"ISO/RTO: {iso_rto}")
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
    merged_data["total_electricity_gen[kw]"]
    * 1
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

# print("Annual Cost of Electricity [$]:")
# print(annual_cost_of_electricity)
# print("Annual Cost of Water [$]:")
# print(annual_cost_of_water)

# Net Present Value (NPV) Assumptions

# financial assumptions; same as NREL H2A-Lite model
print("Financial Assumptions:")
project_lifetime = 20  # 20 year project lifetime
print(f"Project Lifetime: {project_lifetime} years")
discount_rate = 0.1  # 10% discount rate
print(f"Discount Rate: {discount_rate * 100}%")
total_income_tax_rate = 0.21  # 25% total income tax rate
print(f"Total Income Tax Rate: {total_income_tax_rate * 100}%")
project_start_year = 2020

# electrolyzer system plant assumptions
hydrogen_energy_density = 33.33  # 33.33 kWh/kg (Lower Heating Value of H2)
electrolyzer_efficiency = hydrogen_energy_density / electricity_input_per_kg_hydrogen
# Calculate the default electrolyzer plant size
default_electrolyzer_plant_size_kw = round(
    (wind_gen_capacity + solar_pv_gen_capacity)
    * yearly_capacity_factor_combined.mean()
    * electrolyzer_efficiency
)
print(f"Assuming Wind Generation Capacity [kW]: {wind_gen_capacity}")
print(f"Assuming Solar PV Generation Capacity [kW]: {solar_pv_gen_capacity}")
print(f"Default Electrolyzer Plant Size [kW]: {default_electrolyzer_plant_size_kw}")

# Prompt user to enter their own electrolyzer plant size or use the default
user_input = input(
    f"Enter the electrolyzer plant size in kW (or press Enter to use the default size of {default_electrolyzer_plant_size_kw} kW): "
)

try:
    if user_input:
        electrolyzer_plant_size_kw = int(user_input)
        if electrolyzer_plant_size_kw > (wind_gen_capacity + solar_pv_gen_capacity):
            raise ValueError(
                "Electrolyzer plant size cannot exceed the total wind + solar PV generation capacity."
            )
    else:
        electrolyzer_plant_size_kw = default_electrolyzer_plant_size_kw
except ValueError as e:
    print(
        f"Invalid input: {e}. Using default size of {default_electrolyzer_plant_size_kw} kW."
    )
    electrolyzer_plant_size_kw = default_electrolyzer_plant_size_kw

print(f"Electrolyzer Plant Size [kW]: {electrolyzer_plant_size_kw}")

# Calculate the number of hours where hydrogen is produced for each year
hours_hydrogen_production = (
    data[data["hydrogen_produced[kg]"] > 0].groupby("year").size()
) * (1 - hydrogen_production_loss)
electrolyzer_plant_utilization = hours_hydrogen_production / (days_per_year * 24)

# yearly electrolyzer plant revenue assumptions
try:
    hydrogen_sale_price_per_kg = float(
        input("Please enter expected hydrogen sales price [$/kg_H2]: ")
    )
    hydrogen_sale_price_per_kg = int(hydrogen_sale_price_per_kg)
except ValueError:
    print("Invalid input. Using default value of 7 $/kg_h2.")
    hydrogen_sale_price_per_kg = 7.0  # default price per kg of hydrogen
hydrogen_ptc_credit_per_kg = 3  # $3 per kg of hydrogen

# electrolyzer plant costs
electrolyzer_plant_capex_per_kw = 2000  # $2000 per kW
electrolyzer_plant_fixed_yearly_opex_per_kw = 200  # 200 per kW
electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen = (
    0.05  # $0.05 per kg of hydrogen
)

# calculate yearly revenue and costs
annual_hydrogen_sales_revenue = (
    annual_hydrogen_produced * hydrogen_sale_price_per_kg
).round(2)
# print("Annual Hydrogen Sales Revenue [$]:")
# print(annual_hydrogen_sales_revenue)

annual_income_tax = total_income_tax_rate * annual_hydrogen_sales_revenue
# print("Annual Income Tax [$]:")
# print(annual_income_tax)

annual_electrolyzer_plant_yearly_opex = (
    (electrolyzer_plant_size_kw * electrolyzer_plant_fixed_yearly_opex_per_kw)
    + (
        annual_hydrogen_produced
        * electrolyzer_plant_variable_yearly_opex_per_kg_hydrogen
    )
).round(2)
# print("Annual Electrolyzer Plant Yearly OPEX [$]:")
# print(annual_electrolyzer_plant_yearly_opex)

# Calculate annual cash flows
annual_cash_flows = []  # Initialize list to store annual cash flows
annual_costs = [
    electrolyzer_plant_size_kw * electrolyzer_plant_capex_per_kw
]  # Initial CAPEX in year 0
annual_revenues = [0]
annual_hydrogen_production_kg = [0]

for year in range(1, project_lifetime + 1):
    if year <= len(years):
        year_index = year - 1
        if year <= 10:
            annual_hydrogen_ptc_credit = (
                annual_hydrogen_produced.iloc[year_index] * hydrogen_ptc_credit_per_kg
            ).round(2)
        else:
            annual_hydrogen_ptc_credit = 0

        annual_revenue = annual_hydrogen_sales_revenue.iloc[year_index]
        annual_cost = (
            annual_electrolyzer_plant_yearly_opex.iloc[year_index]
            + annual_cost_of_electricity.iloc[year_index]
            + annual_cost_of_water.iloc[year_index]
            + annual_income_tax.iloc[year_index]
            - annual_hydrogen_ptc_credit
        )
        annual_hydrogen_production = annual_hydrogen_produced.iloc[year_index]
    else:
        if year <= 10:
            annual_hydrogen_ptc_credit = (
                annual_hydrogen_produced.mean() * hydrogen_ptc_credit_per_kg
            ).round(2)
        else:
            annual_hydrogen_ptc_credit = 0
        annual_revenue = annual_hydrogen_sales_revenue.mean()
        annual_cost = (
            annual_electrolyzer_plant_yearly_opex.mean()
            + annual_cost_of_electricity.mean()
            + annual_cost_of_water.mean()
            + annual_income_tax.mean()
            - annual_hydrogen_ptc_credit
        )
        annual_hydrogen_production = [annual_hydrogen_produced.mean()]

        annual_hydrogen_production = annual_hydrogen_produced.mean()
    annual_revenues.append(annual_revenue)
    annual_costs.append(annual_cost)
    annual_hydrogen_production_kg.append(annual_hydrogen_production)
    annual_cash_flows = [
        annual_revenues[i] - annual_costs[i] for i in range(len(annual_revenues))
    ]

# Convert annual cash flows to millions of dollars
annual_cash_flows_millions = []
annual_costs_millions = []
annual_revenues_millions = []
annual_cash_flows_millions = [cf / 1e6 for cf in annual_cash_flows]
annual_costs_millions = [cf / 1e6 for cf in annual_costs]
annual_revenues_millions = [cf / 1e6 for cf in annual_revenues]

# Calculate NPV
npv = sum(
    [
        cf / (1 + discount_rate) ** year
        for year, cf in enumerate(annual_cash_flows, start=1)
    ]
)

print(f"Project Net Present Value (NPV): ${npv:,.0f}")

# Calculate Levelized Cost of Hydrogen (LCOH)
npv_costs = sum(
    [cf / (1 + discount_rate) ** year for year, cf in enumerate(annual_costs, start=1)]
)

npv_hydrogen_produced = sum(
    [
        cf / (1 + discount_rate) ** year
        for year, cf in enumerate(annual_hydrogen_production_kg, start=1)
    ]
)

lcoh = npv_costs / npv_hydrogen_produced
print(
    f"Levelized Cost of Hydrogen (LCOH) w/ 10-year 45V PTC): ${lcoh:,.2f} per kg of hydrogen"
)

# Plot annual cash flows vs project lifetime as bars
plt.figure(figsize=(12, 8))

# Change bar color based on value
colors = ["g" if cf >= 0 else "darkred" for cf in annual_cash_flows_millions]
bars = plt.bar(range(project_lifetime + 1), annual_cash_flows_millions, color=colors)

# Add a dashed horizontal line at $0
plt.axhline(0, color="w", linestyle="--")

# Set plot title and labels
plt.title(
    f"Hydrogen Renewable Electrolysis {electrolyzer_plant_size_kw} kW Project Annual Cash Flow for {city}, {state}",
    color="w",
)
plt.xlabel("Year", color="w")
plt.ylabel("Annual Cash Flow [Millions of $]", color="w")

# Ensure x-axis uses whole numbers
plt.xticks(range(project_lifetime + 1), color="w")
plt.yticks(color="w")

# Set plot and figure background to black
plt.gca().set_facecolor("k")
plt.gcf().set_facecolor("k")

# Set border colors to white
plt.gca().spines["top"].set_color("w")
plt.gca().spines["right"].set_color("w")
plt.gca().spines["bottom"].set_color("w")
plt.gca().spines["left"].set_color("w")

# Add values above each bar
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        color="w",
    )

# Save the plot as a .png file
plt.savefig(
    f"Hydrogen_Renewable_Electrolysis_Project_Cash_Flows_for_{city}_{state}.png",
    format="png",
    dpi=300,
    bbox_inches="tight",
)
print(
    f"Project cash flows plot saved as Hydrogen_Renewable_Electrolysis_Project_Cash_Flows_for_{city}_{state}.png"
)
# Stop the program after saving plot
# sys.exit()

# Show the plot
# plt.show()
