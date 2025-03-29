import yfinance as yf
import pandas as pd
import csv

def check_stocks_combined(stocks_file):
    # Read stock tickers from the provided file
    with open(stocks_file, 'r') as f:
        stocks = f.read().splitlines()

    # Lists to hold the stocks in different categories
    stocks_above_50dma = []
    stocks_above_200dma = []
    stocks_between_50dma_and_200dma = []
    stocks_below_50dma = []
    stocks_above_and_crossed_50dma = []
    stocks_above_and_crossed_200dma = []
    stocks_below_and_crossed_50dma = []
    stocks_below_and_crossed_200dma = []

    # CSV Data
    csv_data = []

    for stock in stocks:
        print(f"Processing stock: {stock}")

        # Fetch the stock data for the last 1 year (365 days), suppressing the progress bar
        data = yf.download(stock, period="1y", interval="1d", progress=False)

        # Skip stock if there's insufficient data
        if len(data) < 252:  # Less than 252 trading days means insufficient data
            print(f"Skipping stock {stock} due to insufficient data.")
            continue

        # Calculate the 50-day and 200-day moving averages
        data['50dma'] = data['Close'].rolling(window=50).mean()
        data['200dma'] = data['Close'].rolling(window=200).mean()

        # Get the latest stock price, 50-day, and 200-day moving averages
        latest_price = data['Close'].iloc[-1]
        latest_50dma = data['50dma'].iloc[-1]
        latest_200dma = data['200dma'].iloc[-1]

        # Ensure that all values are scalars
        if isinstance(latest_price, pd.Series):
            latest_price = latest_price.item()
        if isinstance(latest_50dma, pd.Series):
            latest_50dma = latest_50dma.item()
        if isinstance(latest_200dma, pd.Series):
            latest_200dma = latest_200dma.item()

        # Categorize stocks based on their position relative to the moving averages
        if latest_price > latest_50dma:
            stocks_above_50dma.append(stock)
        if latest_price > latest_200dma:
            stocks_above_200dma.append(stock)
        if latest_50dma < latest_price < latest_200dma:
            stocks_between_50dma_and_200dma.append(stock)
        if latest_price < latest_50dma:
            stocks_below_50dma.append(stock)

        # Check for crosses in the last 15 sessions
        recent_data = data.iloc[-16:]  # Last 16 sessions to check for crossovers

        crossed_above_50dma = False
        crossed_above_200dma = False
        crossed_below_50dma = False
        crossed_below_200dma = False
        sessions_50dma_ago = None
        sessions_200dma_ago = None

        for i in range(1, 16):  # Check for crosses within last 15 sessions
            prev_close = recent_data['Close'].iloc[i-1]
            prev_50dma = recent_data['50dma'].iloc[i-1]
            prev_200dma = recent_data['200dma'].iloc[i-1]
            curr_close = recent_data['Close'].iloc[i]
            curr_50dma = recent_data['50dma'].iloc[i]
            curr_200dma = recent_data['200dma'].iloc[i]

            # Check for crossing above the 50DMA
            if prev_close < prev_50dma and curr_close > curr_50dma:
                crossed_above_50dma = True
                sessions_50dma_ago = 15 - i

            # Check for crossing above the 200DMA
            if prev_close < prev_200dma and curr_close > curr_200dma:
                crossed_above_200dma = True
                sessions_200dma_ago = 15 - i

            # Check for crossing below the 50DMA
            if prev_close > prev_50dma and curr_close < curr_50dma:
                crossed_below_50dma = True

            # Check for crossing below the 200DMA
            if prev_close > prev_200dma and curr_close < curr_200dma:
                crossed_below_200dma = True

        # Add stock to corresponding lists based on crosses
        if crossed_above_50dma:
            stocks_above_and_crossed_50dma.append((stock, sessions_50dma_ago))
        if crossed_above_200dma:
            stocks_above_and_crossed_200dma.append((stock, sessions_200dma_ago))
        if crossed_below_50dma:
            stocks_below_and_crossed_50dma.append(stock)
        if crossed_below_200dma:
            stocks_below_and_crossed_200dma.append(stock)

        # Prepare data for CSV output
        price_above_50dma = "Yes" if latest_price > latest_50dma else "No"
        price_above_200dma = "Yes" if latest_price > latest_200dma else "No"
        price_below_50dma = "Yes" if latest_price < latest_50dma else "No"
        price_below_200dma = "Yes" if latest_price < latest_200dma else "No"

        # Check for price between 50dma and 200dma
        if latest_50dma < latest_price < latest_200dma:
            price_between_50_and_200dma = "Yes"
        else:
            price_between_50_and_200dma = "No"

        csv_data.append([
            stock,
            latest_price,
            latest_50dma,
            latest_200dma,
            price_above_50dma,
            price_above_200dma,
            price_below_50dma,
            price_below_200dma,
            price_between_50_and_200dma
        ])

    # Output the results to the screen
    print("\nStocks above the 50-day moving average:")
    for stock in stocks_above_50dma:
        print(stock)

    print("\nStocks above the 200-day moving average:")
    for stock in stocks_above_200dma:
        print(stock)

    print("\nStocks between the 50-day and 200-day moving averages:")
    for stock in stocks_between_50dma_and_200dma:
        print(stock)

    print("\nStocks below the 50-day moving average:")
    for stock in stocks_below_50dma:
        print(stock)

    print("\nStocks above the 50-day moving average and crossed above it in the last 15 trading sessions:")
    for stock, sessions_ago in stocks_above_and_crossed_50dma:
        print(f"{stock} - Crossed above 50DMA {sessions_ago} trading sessions ago")

    print("\nStocks above the 200-day moving average and crossed above it in the last 15 trading sessions:")
    for stock, sessions_ago in stocks_above_and_crossed_200dma:
        print(f"{stock} - Crossed above 200DMA {sessions_ago} trading sessions ago")

    print("\nStocks below the 50-day moving average and crossed below it in the last 15 trading sessions:")
    for stock in stocks_below_and_crossed_50dma:
        print(stock)

    print("\nStocks below the 200-day moving average and crossed below it in the last 15 trading sessions:")
    for stock in stocks_below_and_crossed_200dma:
        print(stock)

    # Write the data to a CSV file
    with open('stock_analysis.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Symbol', 'Current Price', '50DMA', '200DMA', 'Price Above 50DMA', 'Price Above 200DMA', 
            'Price Below 50DMA', 'Price Below 200DMA', 'Price Between 50DMA and 200DMA'
        ])
        for row in csv_data:
            writer.writerow(row)

# Call the function with the path to your stocks.txt file
check_stocks_combined('stocks.txt')

