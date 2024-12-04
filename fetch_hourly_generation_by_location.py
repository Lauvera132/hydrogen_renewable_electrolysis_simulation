# Laura Rivera LR28372
# final project for ME 397: Too Big to Excel

# fetch hourly wind and solar generation by location using Renewables Ninja API
# assumes data fetch for multiple years with a separate API request for each year
# assumes 1000 kw solar and 1500 kw wind capacity

import requests
import json
import pandas as pd
from io import StringIO

def get_coordinates_from_city_state(city, state):
    geocoding_url = "http://api.positionstack.com/v1/forward"
    params = {
        'access_key': '1db5a937b624043d89aecd08a833abee',
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
        'capacity': 1000,
        'system_loss': 0.1,
        'tracking': 0,
        'tilt': latitude,
        'azim': 180,
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
        'capacity': 1500,
        'height': 100,
        'turbine': 'GE 1.5sl', #https://en.wind-turbine-models.com/turbines/20-ge-vernova-ge-1.5sl
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
    df_combined = pd.merge(data_pv, data_wind, on='time', suffixes=('_pv', '_wind'))
    return df_combined

def fetch_data_for_years(city, state, years):
    data_frames = []
    for year in years:
        try:
            df_combined = fetch_renewables_ninja_data(city, state, year)
            data_frames.append(df_combined)
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON response for data in year {year}")
        except Exception as e:
            print(f"An error occurred for year {year}: {e}")
    
    # Combine all yearly data into a single DataFrame
    final_df = pd.concat(data_frames, ignore_index=True)
    return final_df

# test the function with Austin, TX
if __name__ == "__main__":
    city = "Austin"
    state = "TX"
    years = [2021, 2022]
    try:
        data = fetch_data_for_years(city, state, years)
        print("Data:")
        print(data.head())
        print(data.tail())
    except Exception as e:
        print(f"An error occurred: {e}")