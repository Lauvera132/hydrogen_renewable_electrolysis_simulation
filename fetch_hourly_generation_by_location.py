# Laura Rivera LR28372
# final project for ME 397: Too Big to Excel

# fetch hourly generation by location

import requests
import json
import pandas as pd

def get_coordinates(city, state):
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

def fetch_renewables_ninja_data(city, state):
    latitude, longitude = get_coordinates(city, state)
    token = 'a028a1d5cb59daddeaba99f3ed7b608bdfc0cad2'
    api_base = 'https://www.renewables.ninja/api/'
    
    s = requests.session()
    s.headers = {'Authorization': 'Token ' + token}
    
    url = api_base + 'data/pv'
    
    args = {
        'lat': latitude,
        'lon': longitude,
        'date_from': '2020-01-01',
        'date_to': '2020-12-31',
        'dataset': 'merra2',
        'capacity': 100,
        'system_loss': 0.1,
        'tracking': 0,
        'tilt': latitude,
        'azim': 180,
        'format': 'json'
    }
    
    r = s.get(url, params=args)
    
    if r.status_code != 200:
        print(f"Request URL: {r.url}")
        print(f"Response Status Code: {r.status_code}")
        print(f"Response Text: {r.text}")
        raise Exception(f"Error fetching data: {r.status_code}")
    
    try:
        parsed_response = json.loads(r.text)
        data = pd.read_json(StringIO(json.dumps(parsed_response['data'])), orient='index')
        metadata = parsed_response['metadata']
        return data, metadata
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON response")

if __name__ == "__main__":
    city = "Austin"
    state = "TX"
    try:
        data, metadata = fetch_renewables_ninja_data(city, state)
        print("Data:")
        print(data)
        print("\nMetadata:")
        print(metadata)
    except Exception as e:
        print(f"An error occurred: {e}")