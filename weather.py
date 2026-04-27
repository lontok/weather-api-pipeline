import os
import requests
import time
import pandas as pd

API_KEY = os.environ["WEATHER_API_KEY"]

api_url = "https://api.weatherapi.com/v1/current.json"

zip_codes = [
    "90045",  # Los Angeles, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
    "98101",  # Seattle, WA
    "33101",  # Miami, FL
    "77001",  # Houston, TX
    "85001",  # Phoenix, AZ
    "19101",  # Philadelphia, PA
    "78201",  # San Antonio, TX
    "92101",  # San Diego, CA
    "75201",  # Dallas, TX
    "95101",  # San Jose, CA
    "78701",  # Austin, TX
    "32099",  # Jacksonville, FL
    "43215",  # Columbus, OH
    "46201",  # Indianapolis, IN
    "28201",  # Charlotte, NC
    "94102",  # San Francisco, CA
    "80201",  # Denver, CO
    "20001",  # Washington, DC
]

weather_results = []

for zip_code in zip_codes:
    params = {
        "key": API_KEY,
        "q": zip_code,
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    result = {
        "zip_code": zip_code,
        "city": data["location"]["name"],
        "region": data["location"]["region"],
        "temp_f": data["current"]["temp_f"],
        "condition": data["current"]["condition"]["text"],
    }
    weather_results.append(result)

    print(f"{result['city']}, {result['region']}: {result['temp_f']}°F - {result['condition']}")

    time.sleep(1)

df = pd.DataFrame(weather_results)

print(f"\n{df.shape[0]} rows x {df.shape[1]} columns\n")
print(df.to_string(index=False))

df.to_csv("weather_data.csv", index=False)
print("\nSaved to weather_data.csv")


