from googlemaps import Client
from tqdm import tqdm
import pandas as pd
import sys

GOOGLE_MAPS_API_KEY = "AIzaSyBwYEBoH69t8CucOq_Gep30HMMtIInjrRU"
STOPS_BY_ROUTE_PATH = "../../data/stop_data/stops_by_route.csv"

def get_stops(route):
    stops_by_route_df = pd.read_csv(STOPS_BY_ROUTE_PATH)
    stops_by_route_df = stops_by_route_df.set_index(["Route", "Direction"])
    desired_stops = stops_by_route_df.loc[route]
    direction1, direction2 = desired_stops.iloc[0].dropna().str.upper(), desired_stops.iloc[1].dropna().str.upper()
    return direction1, direction2

def get_graph_table(direction1, direction2):
    all_stops = list(set(direction1.tolist() + direction2.tolist()))
    graph = pd.DataFrame(columns=all_stops, index=all_stops)
    return graph

def get_distance(origin, destination, gmaps):
    distance = gmaps.distance_matrix(origin, destination)["rows"][0]["elements"][0]["distance"]["value"]
    return distance

def main():
    bus_route = input()
    gmaps = Client(GOOGLE_MAPS_API_KEY)
    direction1, direction2 = get_stops(bus_route)
    graph = get_graph_table(direction1, direction2)
    for i in tqdm(range(direction1.size - 1), desc=direction1.name): # Iterate from first stop to second-to-last stop
        origin, destination = direction1.iloc[i], direction1.iloc[i + 1]
        distance = get_distance(origin + ", New York, NY", destination + ", New York, NY", gmaps)
        graph.loc[origin, destination] = str(distance) + " " + direction1.name
    for i in tqdm(range(direction2.size - 1), desc=direction2.name):
        origin, destination = direction2.iloc[i], direction2.iloc[i + 1]
        distance = get_distance(origin + ", New York, Ny", destination + ", New York, NY", gmaps)
        graph.loc[origin, destination] = str(distance) + " " + direction2.name
    graph.to_csv(sys.stdout)

if __name__ == "__main__":
    main()
