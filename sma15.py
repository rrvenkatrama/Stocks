import yfinance as yf
import pandas as pd

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
    stocks_below_50dma_and_crossed_below_50dma = []
    stocks_below_200dma_and_crossed_below_200dma = []

    for stock in stocks:
        # Fetch the stock data for the last 1 year, with progress bar suppressed
        data = yf.download(stock, period="1y", interval="1d", progress=False)

        # Calculate the 50-day and 200-day moving averages
        data['50dma'] = data['Close'].rolling(window=50).mean()
        data['200dma'] = data['Close'].rolling(window=200).mean()

        # Get the latest stock price, 50-day, and 200-day moving averages
        latest_price = data['Close'].iloc[-1]  # Get the latest closing price
        latest_50dma = data['50dma'].iloc[-1]  # Get the latest 50-day moving average
        latest_200dma = data['200dma'].iloc[-1]  # Get the latest 200-day moving average

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

        # Check if the stock crossed above or below the 50DMA or 200DMA in the last 15 sessions
        recent_data = data.iloc[-16:]  # Get the last 16 trading sessions (last 15 plus the current session)
        crossed_above_50dma = False
        crossed_above_200dma = False
        crossed_below_50dma = False
        crossed_below_200dma = False
        sessions_50dma_ago = None
        sessions_200dma_ago = None
        sessions_below_50dma_ago = None
        sessions_below_200dma_ago = None

        for i in range(1, 16):  # Check last 15 sessions
            prev_close = recent_data['Close'].iloc[i-1]
            prev_50dma = recent_data['50dma'].iloc[i-1]
            prev_200dma = recent_data['200dma'].iloc[i-1]
            curr_close = recent_data['Close'].iloc[i]
            curr_50dma = recent_data['50dma'].iloc[i]
            curr_200dma = recent_data['200dma'].iloc[i]

            # Ensure these are scalar values
            prev_close = prev_close.item() if isinstance(prev_close, pd.Series) else prev_close
            prev_50dma = prev_50dma.item() if isinstance(prev_50dma, pd.Series) else prev_50dma
            prev_200dma = prev_200dma.item() if isinstance(prev_200dma, pd.Series) else prev_200dma
            curr_close = curr_close.item() if isinstance(curr_close, pd.Series) else curr_close
            curr_50dma = curr_50dma.item() if isinstance(curr_50dma, pd.Series) else curr_50dma
            curr_200dma = curr_200dma.item() if isinstance(curr_200dma, pd.Series) else curr_200dma

            # Check for 50DMA crossover
            if prev_close < prev_50dma and curr_close > curr_50dma:
                crossed_above_50dma = True
                sessions_50dma_ago = 15 - i  # Number of trading sessions ago the crossover happened

            # Check for 200DMA crossover
            if prev_close < prev_200dma and curr_close > curr_200dma:
                crossed_above_200dma = True
                sessions_200dma_ago = 15 - i  # Number of trading sessions ago the crossover happened

            # Check for 50DMA crossing below
            if prev_close > prev_50dma and curr_close < curr_50dma:
                crossed_below_50dma = True
                sessions_below_50dma_ago = 15 - i  # Number of trading sessions ago the crossover happened

            # Check for 200DMA crossing below
            if prev_close > prev_200dma and curr_close < curr_200dma:
                crossed_below_200dma = True
                sessions_below_200dma_ago = 15 - i  # Number of trading sessions ago the crossover happened

        # Add to the respective lists if the stock crossed above or below in the last 15 sessions
        if crossed_above_50dma:
            stocks_above_and_crossed_50dma.append((stock, sessions_50dma_ago))
        if crossed_above_200dma:
            stocks_above_and_crossed_200dma.append((stock, sessions_200dma_ago))
        if crossed_below_50dma:
            stocks_below_50dma_and_crossed_below_50dma.append((stock, sessions_below_50dma_ago))
        if crossed_below_200dma:
            stocks_below_200dma_and_crossed_below_200dma.append((stock, sessions_below_200dma_ago))

    # Output the results, sorted by most recent crossings first
    print("\nStocks above the 50-day moving average:")
    for stock in sorted(stocks_above_50dma, key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True):
        print(stock)

    print("\nStocks above the 200-day moving average:")
    for stock in sorted(stocks_above_200dma, key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True):
        print(stock)

    print("\nStocks between the 50-day and 200-day moving averages:")
    for stock in sorted(stocks_between_50dma_and_200dma, key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True):
        print(stock)

    print("\nStocks below the 50-day moving average:")
    for stock in sorted(stocks_below_50dma, key=lambda x: x[1] if isinstance(x, tuple) else 0, reverse=True):
        print(stock)

    print("\nStocks above the 50-day moving average and crossed above it in the last 15 trading sessions:")
    for stock, sessions_ago in sorted(stocks_above_and_crossed_50dma, key=lambda x: x[1], reverse=True):
        print(f"{stock} - Crossed above 50DMA {sessions_ago} trading sessions ago")

    print("\nStocks above the 200-day moving average and crossed above it in the last 15 trading sessions:")
    for stock, sessions_ago in sorted(stocks_above_and_crossed_200dma, key=lambda x: x[1], reverse=True):
        print(f"{stock} - Crossed above 200DMA {sessions_ago} trading sessions ago")

    print("\nStocks below the 50-day moving average and crossed below it in the last 15 trading sessions:")
    for stock, sessions_ago in sorted(stocks_below_50dma_and_crossed_below_50dma, key=lambda x: x[1], reverse=True):
        print(f"{stock} - Crossed below 50DMA {sessions_ago} trading sessions ago")

    print("\nStocks below the 200-day moving average and crossed below it in the last 15 trading sessions:")
    for stock, sessions_ago in sorted(stocks_below_200dma_and_crossed_below_200dma, key=lambda x: x[1], reverse=True):
        print(f"{stock} - Crossed below 200DMA {sessions_ago} trading sessions ago")

# Call the function with the path to your stocks.txt file
check_stocks_combined('stocks.txt')

