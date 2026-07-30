import requests
import pandas as pd

# default values for testing

def get_climate_data(lat: float = 28.4, lon: float = 77.0, start_date: str = "20230101", end_date: str = "20231231"):
    
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,EVPTRNS",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    parameters = data["properties"]["parameter"]


    # SAFE extraction 
    df = pd.DataFrame({
        "date": list(parameters["T2M"].keys()),
        "T2M": list(parameters["T2M"].values()),
        "T2M_MAX": list(parameters["T2M_MAX"].values()),
        "T2M_MIN": list(parameters["T2M_MIN"].values()),
        "PRECTOTCORR": list(parameters["PRECTOTCORR"].values()),
        "RH2M": list(parameters["RH2M"].values()),
        "EVPTRNS": list(parameters["EVPTRNS"].values())
    })



    # Proper date parsing
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

    df["lat"] = lat
    df["lon"] = lon

    print("Fixed Data Sample:")
    print(df.head())

    return df