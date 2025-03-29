import yfinance as yf
import pandas as pd

def check_stocks_above_50dma(stocks_file):
    # Read stock tickers from the provided file
    with open(stocks_file, 'r') as f:
        stocks = f.read().splitlines()
    
    # List to hold the stocks that are above their 50-day moving average
    stocks_above_50dma = []
    
    for stock in stocks:
        # Fetch the stock data for the last 1 year
        data = yf.download(stock, period="2y", interval="1d")
        
        # Calculate the 50-day moving average
        data['50dma'] = data['Close'].rolling(window=50).mean()
        
        # Get the latest stock price and the 50-day moving average
        latest_price = data['Close'].iloc[-1]  # Get the latest closing price
        latest_50dma = data['50dma'].iloc[-1]  # Get the latest 50-day moving average
        
        # Debug statement to display the latest price and 50-day moving average
        print(f"Debug: {stock} - Latest Price: {latest_price}, Latest 50-Day MA: {latest_50dma}")
        
        # Ensure that both values are scalars (use .item() to ensure you're working with a scalar)
        if isinstance(latest_price, pd.Series):
            latest_price = latest_price.item()
        if isinstance(latest_50dma, pd.Series):
            latest_50dma = latest_50dma.item()
        
        # Check if the latest price is above the 50-day moving average
        if latest_price > latest_50dma:
            stocks_above_50dma.append(stock)
    
    # Output the results
    if stocks_above_50dma:
        print("\nStocks above the 50-day moving average:")
        for stock in stocks_above_50dma:
            print(stock)
    else:
        print("No stocks are above the 50-day moving average.")

# Call the function with the path to your stocks.txt file
check_stocks_above_50dma('stocks.txt')

