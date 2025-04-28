from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
import pandas as pd
import datetime
import pytz
import os

# Create a DataFrame to store the depth data
depth_data = []
csv_file = f"NIFTY25MAYFUT_depth_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv"

def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.
    """
    print("Connection opened")
    # Specify the data type and symbols you want to subscribe to
    mode = SubscriptionModes.DEPTH
    Channel = '1'
    # Subscribe to the specified symbols and data type
    symbols = ['NSE:NIFTY25MAYFUT']
    
    fyers.subscribe(symbol_tickers=symbols, channelNo=Channel, mode=mode)
    fyers.switchChannel(resume_channels=[Channel], pause_channels=[])

    # Keep the socket running to receive real-time data
    fyers.keep_running()

def on_depth_update(ticker, message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.
    """
    # Convert Unix timestamp to IST datetime
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.datetime.fromtimestamp(message.timestamp, tz=pytz.utc)
    ist_time = timestamp.astimezone(ist)
    
    # Create a dictionary with the depth data
    data = {
        'ticker': ticker,
        'timestamp': message.timestamp,
        'ist_datetime': ist_time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_buy_qty': message.tbq,
        'total_sell_qty': message.tsq,
        'snapshot': message.snapshot
    }
    
    # Add bid/ask price and quantity data
    for i in range(len(message.bidprice)):
        if i < len(message.bidprice):
            data[f'bid_price_{i+1}'] = message.bidprice[i]
            data[f'bid_qty_{i+1}'] = message.bidqty[i]
            data[f'bid_orders_{i+1}'] = message.bidordn[i]
        if i < len(message.askprice):
            data[f'ask_price_{i+1}'] = message.askprice[i]
            data[f'ask_qty_{i+1}'] = message.askqty[i]
            data[f'ask_orders_{i+1}'] = message.askordn[i]
    
    # Append the data to our list
    depth_data.append(data)
    
    # Save to CSV every 100 records (adjust as needed)
    if len(depth_data) % 100 == 0:
        save_to_csv()
        
    # Print some info to console
    print(f"Received depth update for {ticker} at {ist_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bid/Ask Spread: {message.askprice[0] - message.bidprice[0]}")
    print(f"Total records: {len(depth_data)}")

def save_to_csv():
    """
    Save the collected depth data to a CSV file
    """
    df = pd.DataFrame(depth_data)
    df.to_csv(csv_file, index=False)
    print(f"Saved {len(depth_data)} records to {csv_file}")

def onerror(message):
    print("Error:", message)
    # Save data collected so far
    save_to_csv()

def onclose(message):
    print("Connection closed:", message)
    # Save data collected so far
    save_to_csv()

def onerror_message(message):
    print("Error Message:", message)

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCb0R2WnNiQXlNeTNwSnpLZDgwY3pteUJTek5ET2xNLXd3cVg5cVNPRWhxOGxkdzgxR2hqcXppMmU3cS1mVTZhcWxlRm5uY3UtcjNxRzVDdmthdHQ1TUUtMUJCQWN2UG9hMVhoMEtMVk5lMDYxci1CZz0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkZWNhY2RhZDNmNzdjMGNkYTE0OThlNzY1MzdiMTMyYjcxNGMyZTg0NmQzNDFmMmZiYzkzZmY1YSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIyMDE4NSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzQ1ODg2NjAwLCJpYXQiOjE3NDU4MTEwNTIsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc0NTgxMTA1Miwic3ViIjoiYWNjZXNzX3Rva2VuIn0.d05XbKJGBlwRoj_lQDOGPlSMOym06xYt4MHsLkj0gLE"
fyers = FyersTbtSocket(
    access_token=access_token,  
    write_to_file=False,        
    log_path="",                
    on_open=onopen,          
    on_close=onclose,           
    on_error=onerror,           
    on_depth_update=on_depth_update,
    on_error_message=onerror_message         
)

try:
    print(f"Starting websocket connection, data will be saved to {csv_file}")
    fyers.connect()
except KeyboardInterrupt:
    print("Script terminated by user")
    save_to_csv()
    print("Data saved to CSV")
except Exception as e:
    print(f"An error occurred: {e}")
    save_to_csv()
    print("Data saved to CSV despite error")