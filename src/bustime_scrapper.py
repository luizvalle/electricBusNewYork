#!/usr/bin/env python
import sys
import requests
import json
import time
import pandas as pd

from datetime import datetime
from typing import List, Tuple, Dict
from csv import writer

class Location(object):
    def __init__(self, longitude:float, latitude:float):
        self.longitude = longitude
        self.latitude = latitude
    
    def dict_from_class(self):
        return {
            "longitude": self.longitude,
            "latitude": self.latitude
        }
    
    def __str__(self):
        s = "{\n"
        for key, value in self.dict_from_class().items():
            s += f"{key}: {value}\n"
        s += "}"
        return s

class BusData(object):
    def __init__(self, bus_id:int, timestamp:str, route_name:str, stop_name:str, destination:str, location:Location, bearing:float):
        self.id = bus_id
        self.timestamp = timestamp
        self.route_name = route_name
        self.stop_name = stop_name
        self.destination = destination
        self.bearing = bearing
        self.location = location
    
    def dict_from_class(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "route_name": self.route_name,
            "stop_name": self.stop_name,
            "destination": self.destination,
            "bearing": self.bearing,
            "location": self.location
        }

    def list_from_class(self) -> list:
        return [
            self.id,
            self.timestamp,
            self.route_name,
            self.stop_name,
            self.destination,
            self.bearing,
            self.location.longitude,
            self.location.latitude
        ]

    def __str__(self) -> str:
        s = "{\n"
        for key, value in self.dict_from_class().items():
            s += f"{key}: {value}\n"
        s += "}"
        return s


def log(message):
    print(f"{datetime.now()} {message}", file=sys.stderr, flush=True)

def get_bus_ids(data_filepath:str, makes:List[str]=[], models:List[str]=[], years:List[int]=[], depots:List[str]=[]) -> List[int]:
    df = pd.read_csv(data_filepath)
    all_makes, all_models, all_years, all_depots = df["Make"], df["Model"], df["Year"], df["Depot"]
    if makes != []:
        df = df[all_makes.isin(makes)]
    if models != []:
        df = df[all_models.isin(models)]
    if years != []:
        df = df[all_years.isin(years)]
    if depots != []:
        df = df[all_depots.isin(depots)]
    return df["ID"].tolist()


def get_bus_data(api_key:str, bus_id:int) -> BusData:
    url = f"http://bustime.mta.info/api/siri/vehicle-monitoring.json?key={api_key}&VehicleRef={bus_id}"

    try:
        request = requests.get(url)
    except:
        log(f"Error: Issue requesting data for bus {bus_id}")
        return None
   
    try:
        data = json.loads(request.text)["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["VehicleActivity"]
    except KeyError:
        log(f"Error: Issue getting data from JSON for bus {bus_id}")
        None

    if len(data) == 0:
        log(f"No VehicleActivity data for bus {bus_id}")
        return None

    data = data[0]

    try:
        timestamp = data["RecordedAtTime"]
    except KeyError:
        log(f"No timestamp for bus {bus_id}")
        return None

    try:
        journey_data = data["MonitoredVehicleJourney"]
    except KeyError:
        log(f"No MonitoredVehicleJoourney data for bus {bus_id}")
        return None

    try:
        route_name = journey_data["PublishedLineName"]
    except KeyError:
        route_name = ""

    try:
        stop_name = journey_data["MonitoredCall"]["StopPointName"]
    except KeyError:
        stop_name = ""

    try:
        destination = journey_data["DestinationName"]
    except KeyError:
        destination = ""

    try:
        location = Location(journey_data["VehicleLocation"]["Longitude"], journey_data["VehicleLocation"]["Latitude"])
    except:
        location = Location(float("NaN"), float("NaN"))
    
    try:
        bearing = journey_data["Bearing"]
    except KeyError:
        bearing = float("NaN")

    return BusData(bus_id, timestamp, route_name, stop_name, destination, location, bearing)

def store_data(file, data:BusData):
    csv_writer = writer(file)
    csv_writer.writerow(data.list_from_class())
    log(f"Data stored for bus {data.id}")

def main():
    argv = sys.argv
    
    if len(argv) != 4:
        log(f"usage: {argv[0]} <api_key> <bus_id_data> <store_file>")
        sys.exit()
    
    api_key = argv[1]
    data_filepath = argv[2]
    store_filepath = argv[3]

    bus_ids = get_bus_ids(data_filepath, models=["XE40 Xcelsior CHARGE", "XE60 Xcelsior CHARGE Articulated"])

    log(f"Monitoring {len(bus_ids)} buses\n")
    while True:
        with open(store_filepath, "a+", newline="") as store_file:
            for bus_id in bus_ids:
                data = get_bus_data(api_key, bus_id)
                if data != None:
                    store_data(store_file, data)
                time.sleep(0.5)
        log("Finished processing batch. Starting over...\n")
        time.sleep(1)

if __name__ == "__main__":
    main()