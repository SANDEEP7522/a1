import os
from datetime import datetime

import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2


load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
PASSWORD = os.getenv("ANGEL_CLIENT_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Change only these values for another instrument
TOKEN = "560977"
SYMBOL = "CRUDEOIL19AUG26FUT"

# Angel One WebSocket constants
MCX_EXCHANGE_TYPE = 5
LTP_MODE = 1

CORRELATION_ID = "mcx_live_001"


def validate_env():
    required = {
        "ANGEL_API_KEY": API_KEY,
        "ANGEL_CLIENT_ID": CLIENT_ID,
        "ANGEL_CLIENT_PASSWORD": PASSWORD,
        "ANGEL_TOTP_SECRET": TOTP_SECRET,
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise ValueError(
            f"Missing values in .env: {', '.join(missing)}"
        )


validate_env()

# Generate current TOTP
totp = pyotp.TOTP(
    TOTP_SECRET.strip().replace(" ", "")
).now()

# Login
smart_api = SmartConnect(api_key=API_KEY)

session = smart_api.generateSession(
    CLIENT_ID,
    PASSWORD,
    totp,
)

if not session or not session.get("status"):
    raise RuntimeError(
        f"Angel One login failed: {session}"
    )

jwt_token = session["data"]["jwtToken"]
feed_token = smart_api.getfeedToken()

print("Login successful")
print(f"Symbol: {SYMBOL}")
print(f"Token: {TOKEN}")
print("Connecting to live WebSocket...\n")

# WebSocket instance
socket = SmartWebSocketV2(
    jwt_token,
    API_KEY,
    CLIENT_ID,
    feed_token,
    max_retry_attempt=5,
    retry_strategy=0,
    retry_delay=5,
    retry_duration=30,
)

token_list = [
    {
        "exchangeType": MCX_EXCHANGE_TYPE,
        "tokens": [TOKEN],
    }
]


def on_open(wsapp):
    print("WebSocket connected")
    print("Subscribed to live MCX data\n")

    socket.subscribe(
        CORRELATION_ID,
        LTP_MODE,
        token_list,
    )


def on_data(wsapp, message):
    """
    LTP message generally contains:
    subscription_mode
    exchange_type
    token
    sequence_number
    exchange_timestamp
    last_traded_price
    """

    raw_ltp = message.get("last_traded_price")

    # Angel One generally sends price in integer price units.
    # For many contracts, dividing by 100 gives displayed price.
    display_ltp = (
        raw_ltp / 100
        if isinstance(raw_ltp, (int, float))
        else raw_ltp
    )

    exchange_timestamp = message.get("exchange_timestamp")

    if exchange_timestamp:
        tick_time = datetime.fromtimestamp(
            exchange_timestamp / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
    else:
        tick_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    print(
        f"{tick_time} | "
        f"{SYMBOL} | "
        f"Token: {message.get('token')} | "
        f"LTP: {display_ltp} | "
        f"Raw LTP: {raw_ltp}"
    )


def on_error(wsapp, error):
    print(f"WebSocket error: {error}")


def on_close(wsapp):
    print("\nWebSocket connection closed")


def on_control_message(wsapp, message):
    print(f"Control message: {message}")


socket.on_open = on_open
socket.on_data = on_data
socket.on_error = on_error
socket.on_close = on_close
socket.on_control_message = on_control_message


try:
    socket.connect()

except KeyboardInterrupt:
    print("\nStopping live feed...")
    socket.close_connection()

except Exception as error:
    print(f"Connection failed: {error}")
    socket.close_connection()