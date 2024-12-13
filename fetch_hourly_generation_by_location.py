# fetch hourly wind and solar generation by location using Renewables Ninja API
# assumes data fetch for multiple years with a separate API request for each year

import requests
import json
import pandas as pd
from io import StringIO
import time
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# assumptions for wind and solar PV systems
wind_capacity = 7500  # in kW
wind_hub_height = 100  # in meters
wind_turbine_model = 'GE 1.5sl'
solar_pv_capacity = 5000  # in kW
solar_system_loss = 0.1
solar_tracking = 0
solar_azimuth_angle = 180  # in degrees (due south for the northern hemisphere)

def get_coordinates_from_city_state(city, state):
    geocoding_url = "http://api.positionstack.com/v1/forward"
    params = {
        'access_key': '13724b6dbaad32abb6493e3bf1dcdabc',
        'query': f"{city}, {state}",
        'limit': 1
    }
    response = requests.get(geocoding_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching coordinates: {response.status_code}")
    data = response.json()
    if data and 'data' in data and len(data['data']) > 0:
        return data['data'][0]['latitude'], data['data'][0]['longitude']
    else:
        raise ValueError("Could not get coordinates for the given location")


def fetch_renewables_ninja_data(city, state, year):
    latitude, longitude = get_coordinates_from_city_state(city, state)
    token = 'a028a1d5cb59daddeaba99f3ed7b608bdfc0cad2'
    api_base = 'https://www.renewables.ninja/api/'
    
    s = requests.session()
    s.headers = {'Authorization': 'Token ' + token}
    
    # Fetch solar PV data
    url_pv = api_base + 'data/pv'
    args_pv = {
        'lat': latitude,
        'lon': longitude,
        'date_from': f'{year}-01-01',
        'date_to': f'{year}-12-31',
        'dataset': 'merra2',
        'capacity': solar_pv_capacity,
        'system_loss': solar_system_loss,
        'tracking': solar_tracking,
        'tilt': latitude, # tilt angle = latitude (degree)
        'azim': solar_azimuth_angle, 
        'format': 'json'
    }
    response_pv = s.get(url_pv, params=args_pv)
    if response_pv.status_code != 200:
        print(f"Request URL: {response_pv.url}")
        print(f"Response Status Code: {response_pv.status_code}")
        print(f"Response Text: {response_pv.text}")
        raise Exception(f"Error fetching data: {response_pv.status_code}")
    
    try:
        parsed_response_pv = json.loads(response_pv.text)
        data_pv = pd.read_json(StringIO(json.dumps(parsed_response_pv['data'])), orient='index')
        data_pv.reset_index(inplace=True)
        data_pv.rename(columns={'index': 'time'}, inplace=True)
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON response for solar PV data")
    
    # Fetch wind data
    url_wind = api_base + 'data/wind'
    args_wind = {
        'lat': latitude,
        'lon': longitude,
        'date_from': f'{year}-01-01',
        'date_to': f'{year}-12-31',
        'dataset': 'merra2',
        'capacity': wind_capacity,
        'height': wind_hub_height,
        'turbine': wind_turbine_model,
        'format': 'json'
    }
    response_wind = s.get(url_wind, params=args_wind)
    if response_wind.status_code != 200:
        print(f"Request URL: {response_wind.url}")
        print(f"Response Status Code: {response_wind.status_code}")
        print(f"Response Text: {response_wind.text}")
        raise Exception(f"Error fetching data: {response_wind.status_code}")
    
    try:
        parsed_response_wind = json.loads(response_wind.text)
        data_wind = pd.read_json(StringIO(json.dumps(parsed_response_wind['data'])), orient='index')
        data_wind.reset_index(inplace=True)
        data_wind.rename(columns={'index': 'time'}, inplace=True)
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON response for wind data")
    
    # Combine solar PV and wind data
    df_combined = pd.merge(data_pv, data_wind, on='time', suffixes=('_solar_pv[kw]', '_wind[kw]'))
    
    # Convert UTC time to local time
    tf = TimezoneFinder() # Create a TimezoneFinder object
    local_tz = pytz.timezone(tf.timezone_at(lat=latitude, lng=longitude)) # Get the local timezone using coordinates
    df_combined['time'] = pd.to_datetime(df_combined['time']) # Convert time to datetime

    # Calculate total generation and capacity factors
    df_combined['time'] = df_combined['time'].apply(lambda x: x.tz_localize(pytz.utc).astimezone(local_tz).replace(tzinfo=None)) # Convert time to local timezone
    df_combined['total_electricity_gen[kw]'] = df_combined['electricity_solar_pv[kw]'] + df_combined['electricity_wind[kw]']
    df_combined["capacity_factor_wind"] = df_combined["electricity_wind[kw]"] / (wind_capacity)
    df_combined["capacity_factor_solar_pv"] = df_combined["electricity_solar_pv[kw]"] / (solar_pv_capacity)
    df_combined["capacity_factor_combined"] = df_combined["total_electricity_gen[kw]"] / (wind_capacity + solar_pv_capacity)

    return df_combined

def fetch_renewables_generation_data_for_years(city, state, years):
    data_frames = []
    for year in years:
        try:
            df_combined = fetch_renewables_ninja_data(city, state, year)
            data_frames.append(df_combined)
            time.sleep(1)  # Wait for 1 second after each request
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON response for data in year {year}")
        except Exception as e:
            print(f"An error occurred for year {year}: {e}")
    
    # Combine all yearly data into a single DataFrame
    final_df = pd.concat(data_frames, ignore_index=True)
    return final_df, wind_capacity, solar_pv_capacity

# test the function with Austin, TX
if __name__ == "__main__":
    city = "Austin"
    state = "TX"
    years = [2021, 2022]
    try:
        data, wind_capacity, solar_pv_capacity = fetch_renewables_generation_data_for_years(city, state, years)
        print("Data:")
        print(data.head())
        print(data.tail())
        print(f"Wind Capacity: {wind_capacity} kW")
        print(f"Solar PV Capacity: {solar_pv_capacity} kW")
    except Exception as e:
        print(f"An error occurred: {e}")