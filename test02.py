from datetime import datetime
import pandas as pd

CSV_FILE = "OpenAPIScripMaster.csv"

df = pd.read_csv(CSV_FILE, dtype={"token": str})

# Column values clean karo
df["exch_seg"] = df["exch_seg"].astype(str).str.strip().str.upper()
df["name"] = df["name"].astype(str).str.strip().str.upper()
df["instrumenttype"] = (
    df["instrumenttype"].astype(str).str.strip().str.upper()
)

# Sirf CRUDEOIL MCX futures
crude_futures = df[
    (df["exch_seg"] == "MCX")
    & (df["name"] == "CRUDEOIL")
    & (df["instrumenttype"] == "FUTCOM")
].copy()

if crude_futures.empty:
    print("CRUDEOIL future record nahi mila.")
    print("\nAvailable similar names:")

    similar = df[
        df["name"].str.contains("CRUDE", case=False, na=False)
        | df["symbol"].str.contains("CRUDE", case=False, na=False)
    ]

    print(
        similar[
            [
                "token",
                "symbol",
                "name",
                "expiry",
                "instrumenttype",
                "exch_seg",
            ]
        ].to_string(index=False)
    )

    raise SystemExit

# Angel master mein expiry usually 25JUL2026 jaisi ho sakti hai
crude_futures["expiry_date"] = pd.to_datetime(
    crude_futures["expiry"],
    errors="coerce",
    dayfirst=True,
)

today = pd.Timestamp.now().normalize()

# Sirf non-expired contracts
active_contracts = crude_futures[
    crude_futures["expiry_date"] >= today
].copy()

active_contracts = active_contracts.sort_values("expiry_date")

if active_contracts.empty:
    print("Koi active CRUDEOIL future contract nahi mila.")
    raise SystemExit

# Nearest expiry = current/near-month future
current_future = active_contracts.iloc[0]

print("\nCurrent CRUDEOIL Future")
print("-----------------------")
print(f"Token:       {current_future['token']}")
print(f"Symbol:      {current_future['symbol']}")
print(f"Name:        {current_future['name']}")
print(f"Expiry:      {current_future['expiry']}")
print(f"Lot size:    {current_future['lotsize']}")
print(f"Instrument:  {current_future['instrumenttype']}")

print("\nAll active CRUDEOIL futures:")
print(
    active_contracts[
        ["token", "symbol", "expiry", "lotsize", "instrumenttype"]
    ].to_string(index=False)
)