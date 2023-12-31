import requests
import json
import math

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    R = 6371

    return R * c

def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to download file from {url}")

routes_url = "http://api.travelpayouts.com/data/routes.json"
airports_url = "http://api.travelpayouts.com/data/en/airports.json"

routes_data = download_file(routes_url)
airports_data = download_file(airports_url)

airport_coordinates = {airport['code']: airport['coordinates'] for airport in airports_data}

new_routes_data = []
for route in routes_data:
    departure_code = route['departure_airport_iata']
    arrival_code = route['arrival_airport_iata']
    departure_coordinates = airport_coordinates.get(departure_code)
    arrival_coordinates = airport_coordinates.get(arrival_code)

    if departure_coordinates and arrival_coordinates:

        distance = haversine(departure_coordinates['lat'], departure_coordinates['lon'], 
                             arrival_coordinates['lat'], arrival_coordinates['lon'])
        new_route = {
            "airline": route['airline_iata'],
            "departure": departure_code,
            "departure_coordinate": departure_coordinates,
            "arrival": arrival_code,
            "arrival_coordinate": arrival_coordinates,
            "distance": distance,
            "planes": route['planes']
        }
        new_routes_data.append(new_route)

with open('processed_routes_with_distance.json', 'w') as file:
    json.dump(new_routes_data, file)

print("File saved as 'processed_routes_with_distance.json'")