import requests
import pandas as pd

URL = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"

print("Downloading Angel One Instrument Master...")

response = requests.get(URL, timeout=60)
response.raise_for_status()

data = response.json()

df = pd.DataFrame(data)

# Save complete master
df.to_csv("OpenAPIScripMaster.csv", index=False)

print(f"✅ Download Complete")
print(f"Total Instruments: {len(df)}")
print("Saved as: OpenAPIScripMaster.csv")