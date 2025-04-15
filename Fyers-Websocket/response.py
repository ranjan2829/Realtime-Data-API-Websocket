from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta
import pandas as pd
import pytz

client_id = "QGP6MO6UJQ-100"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCbl9reU4wMGh5SGwwdzdZbzQ5YzZPQmpSZjA4cFE0akZDLWpKSDNobDZoT2VZSkkxRy0yZ1VVQko4SThhU1BWbjJNUDZ1LTRkbXdUdGhWamtUZUN0MkR6TDRkeE8ydzlyYUdORjBsNGZPbjI2aEtLOD0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkZWNhY2RhZDNmNzdjMGNkYTE0OThlNzY1MzdiMTMyYjcxNGMyZTg0NmQzNDFmMmZiYzkzZmY1YSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIyMDE4NSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzQ0NzYzNDAwLCJpYXQiOjE3NDQ3MTg5ODksImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc0NDcxODk4OSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.ayLNhN8hOoB9FHunCm20P1WF4_BimeKX-Noepo71g0U"
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

# Get today's date
today = datetime.now()

# Try with a different resolution and date format to debug
history_data = {
    "symbol": "NSE:NIFTY25APRFUT",
    "resolution": "5S",  # 5 second candles
    "date_format": "1",  # Using date format 1 for YYYY-MM-DD
    "range_from": "2025-04-15",
    "range_to": "2025-04-15",
    "cont_flag": "1"  # Continuous data
}

try:
    # Make the API call to get historical data
    print("Sending request for historical data...")
    response = fyers.history(data=history_data)
    
    if response and isinstance(response, dict) and response.get("s") == "ok" and "candles" in response:
        # Extract the candles data
        candles = response["candles"]
        
        # Convert candles to DataFrame
        data = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        
        # Convert timestamp to IST timezone (UTC+5:30)
        # First convert to UTC timezone
        data["datetime"] = pd.to_datetime(data["timestamp"], unit="s", utc=True)
        
        # Then convert to Asia/Kolkata timezone
        ist = pytz.timezone('Asia/Kolkata')
        data["datetime"] = data["datetime"].dt.tz_convert(ist)
        
        # Remove timezone info for cleaner display
        data["datetime"] = data["datetime"].dt.tz_localize(None)
        
        print(f"Retrieved {len(data)} candles")
        print(data.head())  # Show the first few rows
        
        # Save to CSV
        csv_filename = f"NIFTY25APRFUT_data_{today.strftime('%Y%m%d')}.csv"
        data.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")
    else:
        print(f"Error retrieving data: {response}")
        
except Exception as e:
    import traceback
    print(f"An error occurred: {e}")
    print(traceback.format_exc())  # Print the full stack trace