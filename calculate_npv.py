# calculate the NPV of a hydrogen electrolysis project using wind/solar generation data

# calculate amount of hydrogen produced by electrolysis
# 55 kwh of electricity per kg of hydrogen
# 3.780 gallons of water per kg of hydrogen

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fetch_hourly_generation_by_location import fetch_renewables_generation_data_for_years

# Prompt user for input
# city = input("Please enter the US city: ")
city = "Houston"
# state = input("Please enter the US state abbreviation: ")
state = "TX"
years = [2021, 2022]

# determine electricity available from wind/solar hourly generation for user location
data = fetch_renewables_generation_data_for_years(city, state, years)
# data['total_generation'] = generation_data['electricity_wind'] + generation_data['electricity_solar_pv']