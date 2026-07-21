import os
from datetime import datetime

import pandas as pd
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect

load_dotenv()

# Login
smart = SmartConnect(api_key=os.getenv("ANGEL_API_KEY"))

totp = pyotp.TOTP(os.getenv("ANGEL_TOTP_SECRET")).now()

session = smart.generateSession(
    os.getenv("ANGEL_CLIENT_ID"),
    os.getenv("ANGEL_CLIENT_PASSWORD"),
    totp,
)

if not session["status"]:
    raise Exception(session)

print("Login Successful")

# ======================================
# CHANGE ONLY THESE
# ======================================

TOKEN = "560977"          # Instrument Token
EXCHANGE = "MCX"
INTERVAL = "ONE_MINUTE"

today = datetime.now().strftime("%Y-%m-%d")

# ======================================

params = {
    "exchange": EXCHANGE,
    "symboltoken": TOKEN,
    "interval": INTERVAL,
    "fromdate": f"{today} 00:00",
    "todate": datetime.now().strftime("%Y-%m-%d %H:%M"),
}

response = smart.getCandleData(params)

if not response["status"]:
    raise Exception(response)

candles = response["data"]

df = pd.DataFrame(
    candles,
    columns=[
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
)

filename = f"{TOKEN}_1min.csv"

df.to_csv(filename, index=False)

print(f"\nDownloaded {len(df)} candles")
print(f"Saved -> {filename}")

print(df.tail())