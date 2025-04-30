from fyers_apiv3 import fyersModel
import pandas as pd
import time
from datetime import datetime
import os
from tabulate import tabulate
import pytz
import sys
import signal

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Authentication credentials
client_id = "QGP6MO6UJQ-100"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCb0VabW5BWWp2OUVyallYZHpBeDZyZzZjb3BqTDBOYVRRdmhzcWZUWW9UTjRGX1RLUWUxNG5yc0czWDdrUVNxVnlmLWlXWFJFa3VoWkwtTjNGQ084SXB0SjFVS2RIVUI4Y2dMQjVOZzY2SVFIT2tSRT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkZWNhY2RhZDNmNzdjMGNkYTE0OThlNzY1MzdiMTMyYjcxNGMyZTg0NmQzNDFmMmZiYzkzZmY1YSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIyMDE4NSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzQ2MDU5NDAwLCJpYXQiOjE3NDU5ODM5MTEsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc0NTk4MzkxMSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.a5wafiJVZWC4eV1ATCIuJxYbJJP3mz4NBTA7MXJpxD0"
# Initialize Fyers API
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

# Symbol to track
SYMBOL = "NSE:NIFTY25MAYFUT"

# CSV filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"orderbook_{SYMBOL.replace(':', '_')}_{timestamp}.csv"

# Order book depth
DEPTH = 5

# Initialize CSV with headers
def initialize_csv():
    # Create column headers for bid and ask levels
    columns = ['timestamp', 'ist_datetime', 'ltp', 'chp', 'volume', 'oi', 'oipercent',
               'totalbuyqty', 'totalsellqty']
    
    # Add bid columns (price and quantity for each level)
    for i in range(1, DEPTH + 1):
        columns.extend([f'bid_price_{i}', f'bid_qty_{i}', f'bid_orders_{i}'])
    
    # Add ask columns (price and quantity for each level)
    for i in range(1, DEPTH + 1):
        columns.extend([f'ask_price_{i}', f'ask_qty_{i}', f'ask_orders_{i}'])
    
    # Add OHLC columns
    columns.extend(['open', 'high', 'low', 'close'])
    
    # Create DataFrame with columns and save empty CSV
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_filename, index=False)
    print(f"{Colors.GREEN}CSV file initialized: {csv_filename}{Colors.ENDC}")

# Function to fetch order book data
def fetch_orderbook():
    try:
        data = {
            "symbol": SYMBOL,
            "ohlcv_flag": "1"
        }
        
        response = fyers.depth(data=data)
        
        if response and 's' in response and response['s'] == 'ok':
            return response
        else:
            print(f"{Colors.RED}Error in API response: {response}{Colors.ENDC}")
            return None
    except Exception as e:
        print(f"{Colors.RED}Error fetching order book: {e}{Colors.ENDC}")
        return None

# Function to process order book data and save to CSV
def process_and_save(response):
    try:
        symbol_data = response['d'][SYMBOL]
        
        # Current timestamp
        timestamp = int(time.time())
        ist_datetime = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract OHLC data
        ohlc = {
            'open': symbol_data.get('o', 0),
            'high': symbol_data.get('h', 0),
            'low': symbol_data.get('l', 0),
            'close': symbol_data.get('c', 0)
        }
        
        # Extract order book data
        row_data = {
            'timestamp': timestamp,
            'ist_datetime': ist_datetime,
            'ltp': symbol_data.get('ltp', 0),
            'chp': symbol_data.get('chp', 0),
            'volume': symbol_data.get('v', 0),
            'oi': symbol_data.get('oi', 0),
            'oipercent': symbol_data.get('oipercent', 0),
            'totalbuyqty': symbol_data.get('totalbuyqty', 0),
            'totalsellqty': symbol_data.get('totalsellqty', 0),
            'open': ohlc['open'],
            'high': ohlc['high'],
            'low': ohlc['low'],
            'close': ohlc['close']
        }
        
        # Process bid levels
        bids = symbol_data.get('bids', [])
        for i in range(1, DEPTH + 1):
            if i <= len(bids):
                row_data[f'bid_price_{i}'] = bids[i-1].get('price', 0)
                row_data[f'bid_qty_{i}'] = bids[i-1].get('volume', 0)
                row_data[f'bid_orders_{i}'] = bids[i-1].get('ord', 0)
            else:
                row_data[f'bid_price_{i}'] = 0
                row_data[f'bid_qty_{i}'] = 0
                row_data[f'bid_orders_{i}'] = 0
        
        # Process ask levels
        asks = symbol_data.get('ask', [])
        for i in range(1, DEPTH + 1):
            if i <= len(asks):
                row_data[f'ask_price_{i}'] = asks[i-1].get('price', 0)
                row_data[f'ask_qty_{i}'] = asks[i-1].get('volume', 0)
                row_data[f'ask_orders_{i}'] = asks[i-1].get('ord', 0)
            else:
                row_data[f'ask_price_{i}'] = 0
                row_data[f'ask_qty_{i}'] = 0
                row_data[f'ask_orders_{i}'] = 0
        
        # Create DataFrame from row data
        df = pd.DataFrame([row_data])
        
        # Append to CSV
        df.to_csv(csv_filename, mode='a', header=False, index=False)
        
        return row_data, symbol_data
        
    except Exception as e:
        print(f"{Colors.RED}Error processing data: {e}{Colors.ENDC}")
        return None, None

# Function to display order book in a nice table format
def display_orderbook(row_data, symbol_data):
    if not row_data:
        return
    
    # Clear terminal
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Format timestamp
    ist_time = row_data['ist_datetime']
    
    # Print header
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} LIVE ORDER BOOK: {SYMBOL} {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD} {ist_time} {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    # Market data
    ltp = row_data['ltp']
    chp = row_data['chp']
    volume = row_data['volume']
    oi = row_data['oi']
    oipercent = row_data['oipercent']
    
    # Print market data
    print(f"{Colors.BOLD}LTP: {Colors.ENDC}{Colors.GREEN if chp >= 0 else Colors.RED}{ltp} ({chp:+.2f}%){Colors.ENDC} | "
          f"{Colors.BOLD}Volume: {Colors.ENDC}{volume:,} | "
          f"{Colors.BOLD}OI: {Colors.ENDC}{oi:,} ({Colors.GREEN if oipercent >= 0 else Colors.RED}{oipercent:+.2f}%{Colors.ENDC})")
    print(f"{Colors.BOLD}OHLC: {Colors.ENDC}{row_data['open']} / {row_data['high']} / {row_data['low']} / {row_data['close']}")
    print()
    
    # Prepare order book table
    book_data = []
    
    # Calculate cumulative quantities
    bid_cumulative = 0
    ask_cumulative = 0
    
    # Prepare order book rows
    for i in range(DEPTH, 0, -1):
        ask_price = row_data[f'ask_price_{i}']
        ask_qty = row_data[f'ask_qty_{i}']
        ask_orders = row_data[f'ask_orders_{i}']
        ask_cumulative += ask_qty
        
        # Empty row for alignment
        book_data.append([
            "", "", "", "",
            f"{Colors.RED}{ask_price:.1f}{Colors.ENDC}",
            f"{Colors.RED}{ask_qty}{Colors.ENDC}",
            f"{Colors.RED}{ask_orders}{Colors.ENDC}",
            f"{Colors.RED}{ask_cumulative}{Colors.ENDC}"
        ])
    
    # Add spread row
    spread = row_data['ask_price_1'] - row_data['bid_price_1']
    spread_pct = (spread / row_data['bid_price_1']) * 100
    book_data.append([
        "", "", "", "",
        f"{Colors.YELLOW}{Colors.BOLD}==SPREAD=={Colors.ENDC}",
        f"{Colors.YELLOW}{Colors.BOLD}{spread:.1f}{Colors.ENDC}",
        f"{Colors.YELLOW}{Colors.BOLD}{spread_pct:.3f}%{Colors.ENDC}",
        ""
    ])
    
    # Reset cumulative for bids
    bid_cumulative = 0
    
    # Add bid rows
    for i in range(1, DEPTH + 1):
        bid_price = row_data[f'bid_price_{i}']
        bid_qty = row_data[f'bid_qty_{i}']
        bid_orders = row_data[f'bid_orders_{i}']
        bid_cumulative += bid_qty
        
        book_data.append([
            f"{Colors.GREEN}{bid_price:.1f}{Colors.ENDC}",
            f"{Colors.GREEN}{bid_qty}{Colors.ENDC}",
            f"{Colors.GREEN}{bid_orders}{Colors.ENDC}",
            f"{Colors.GREEN}{bid_cumulative}{Colors.ENDC}",
            "", "", "", ""
        ])
    
    # Print order book table
    print(tabulate(
        book_data,
        headers=[
            "Bid Price", "Quantity", "Orders", "Cumulative",
            "Ask Price", "Quantity", "Orders", "Cumulative"
        ],
        tablefmt="fancy_grid"
    ))
    
    # Print totals
    print(f"\n{Colors.BOLD}Total Buy Qty: {Colors.GREEN}{row_data['totalbuyqty']:,}{Colors.ENDC} | "
          f"{Colors.BOLD}Total Sell Qty: {Colors.RED}{row_data['totalsellqty']:,}{Colors.ENDC}")
    
    # Calculate Order Book Imbalance (OBI)
    total_bid = row_data['totalbuyqty']
    total_ask = row_data['totalsellqty']
    if (total_bid + total_ask) > 0:
        obi = (total_bid - total_ask) / (total_bid + total_ask)
        obi_color = Colors.GREEN if obi > 0 else Colors.RED
        print(f"{Colors.BOLD}Order Book Imbalance: {obi_color}{obi:.4f}{Colors.ENDC}")
    
    # Show data collection status
    print(f"\n{Colors.BLUE}Data being collected to: {csv_filename}{Colors.ENDC}")
    print(f"{Colors.BLUE}Press Ctrl+C to stop data collection{Colors.ENDC}")

# Handle keyboard interrupt gracefully
def signal_handler(sig, frame):
    print(f"\n{Colors.YELLOW}Data collection stopped by user.{Colors.ENDC}")
    print(f"{Colors.GREEN}Data saved to: {csv_filename}{Colors.ENDC}")
    sys.exit(0)

# Main function
def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Colors.HEADER}Starting live order book data collection for {SYMBOL}{Colors.ENDC}")
    
    # Initialize CSV file
    initialize_csv()
    
    try:
        # Initial check to ensure API is working
        response = fetch_orderbook()
        if response is None:
            print(f"{Colors.RED}Failed to fetch initial data. Check your API connection.{Colors.ENDC}")
            return
        
        # Main data collection loop
        while True:
            start_time = time.time()
            
            # Fetch order book
            response = fetch_orderbook()
            if response:
                # Process and save data
                row_data, symbol_data = process_and_save(response)
                
                # Display order book
                if row_data and symbol_data:
                    display_orderbook(row_data, symbol_data)
            
            # Calculate time taken and sleep for remaining time to maintain 1 second interval
            elapsed = time.time() - start_time
            sleep_time = max(0, 1.0 - elapsed)  # Ensure at least 1 second between requests
            time.sleep(sleep_time)
            
    except Exception as e:
        print(f"{Colors.RED}Error in main loop: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()