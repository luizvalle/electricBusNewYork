import numpy as np
import pandas as pd

def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return earth_radius * 2 * np.arcsin(np.sqrt(a)) * 1000

def extract_displacement_speed_acceleration(csv_filepath):
    df = pd.read_csv(csv_filepath)
    df["Timestamp"] = df["Timestamp"].str.replace(".000-04:00", "").apply(lambda t: datetime.strptime(t, "%Y-%m-%dT%H:%M:%S"))
    bus_ids = df["ID"].unique()
    result = pd.DataFrame(columns=df.columns)
    for bus_id in bus_ids:
        bus_df = df[df["ID"] == bus_id]
        bus_df.insert(2, "Time difference (s)", bus_df["Timestamp"].diff().apply(lambda t: t.total_seconds()), True)
        bus_df.insert(9, "Traveled (m)", haversine(bus_df.Latitude.shift(), bus_df.Longitude.shift(), bus_df.loc[:, "Latitude"], bus_df.loc[:, "Longitude"]), True) 
        bus_df.insert(10, "Speed (m/s)", bus_df.apply(lambda row: row["Traveled (m)"]/row["Time difference (s)"] if row["Time difference (s)"] > 0 else np.nan, axis=1), True)
        bus_df.insert(11, "Change in Speed (m/s)", bus_df["Speed (m/s)"].diff(), True)
        bus_df.insert(12, "Acceleration (m/s^2)", bus_df.apply(lambda row: row["Change in Speed (m/s)"]/row["Time difference (s)"] if row["Time difference (s)"] > 0 else np.nan, axis=1), True)
        result = pd.concat([result, bus_df])
    return result