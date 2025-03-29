import yfinance as yf
import pandas as pd

def check_stocks_position_in_moving_averages(stocks_file):
    # Read stock tickers from the provided file
    with open(stocks_file, 'r') as f:
        stocks = f.read().splitlines()

    # Lists to hold the stocks in different categories
    stocks_between_50_and_200dma = []
    stocks_above_200dma = []
    stocks_below_50dma = []

    for stock in stocks:
        # Fetch the stock data for the last 2 years
        data = yf.download(stock, period="2y", interval="1d")

        # Calculate the 50-day and 200-day moving averages
        data['50dma'] = data['Close'].rolling(window=50).mean()
        data['200dma'] = data['Close'].rolling(window=200).mean()

        # Get the latest stock price and the moving averages
        latest_price = data['Close'].iloc[-1]  # Get the latest closing price
        latest_50dma = data['50dma'].iloc[-1]  # Get the latest 50-day moving average
        latest_200dma = data['200dma'].iloc[-1]  # Get the latest 200-day moving average

        # Debug statement to display the latest price and moving averages
        print(f"Debug: {stock} - Latest Price: {latest_price}, Latest 50-Day MA: {latest_50dma}, Latest 200-Day MA: {latest_200dma}")

        # Ensure that all values are scalars (use .item() to ensure you're working with a scalar)
        if isinstance(latest_price, pd.Series):
            latest_price = latest_price.item()
        if isinstance(latest_50dma, pd.Series):
            latest_50dma = latest_50dma.item()
        if isinstance(latest_200dma, pd.Series):
            latest_200dma = latest_200dma.item()

        # Categorize the stock based on its position relative to the moving averages
        if latest_50dma < latest_price < latest_200dma:
            stocks_between_50_and_200dma.append(stock)
        elif latest_price > latest_200dma:
            stocks_above_200dma.append(stock)
        elif latest_price < latest_50dma:
            stocks_below_50dma.append(stock)

    # Output the results
    if stocks_between_50_and_200dma:
        print("\nStocks between the 50-day and 200-day moving average:")
        for stock in stocks_between_50_and_200dma:
            print(stock)
    else:
        print("No stocks are between the 50-day and 200-day moving average.")

    if stocks_above_200dma:
        print("\nStocks above the 200-day moving average:")
        for stock in stocks_above_200dma:
            print(stock)
    else:
        print("No stocks are above the 200-day moving average.")

    if stocks_below_50dma:
        print("\nStocks below the 50-day moving average:")
        for stock in stocks_below_50dma:
            print(stock)
    else:
        print("No stocks are below the 50-day moving average.")

# Call the function with the path to your stocks.txt file
check_stocks_position_in_moving_averages('stocks.txt')

