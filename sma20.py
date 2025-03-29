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

    # Data for CSV and Excel output
    csv_data = []

    for stock in stocks:
        print(f"Processing stock: {stock}")
        # Fetch the stock data for the last 1 year
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

        # Determine the trend based on the 50DMA and 200DMA
        trend = "Up" if latest_50dma >= latest_200dma else "Down"

        # Categorize stocks based on their position relative to the moving averages
        if latest_price > latest_50dma:
            stocks_above_50dma.append(stock)
        if latest_price > latest_200dma:
            stocks_above_200dma.append(stock)
        if latest_50dma < latest_price < latest_200dma:
            stocks_between_50dma_and_200dma.append(stock)
        if latest_price < latest_50dma:
            stocks_below_50dma.append(stock)

        # Check if the stock crossed above the 50DMA or 200DMA in the last 15 sessions
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

            # Check for 50DMA cross below
            if prev_close > prev_50dma and curr_close < curr_50dma:
                crossed_below_50dma = True
                sessions_below_50dma_ago = 15 - i

            # Check for 200DMA cross below
            if prev_close > prev_200dma and curr_close < curr_200dma:
                crossed_below_200dma = True
                sessions_below_200dma_ago = 15 - i

        # Prepare the row for CSV and Excel
        above_50dma_last_15_sessions = sessions_50dma_ago if crossed_above_50dma else "No"
        above_200dma_last_15_sessions = sessions_200dma_ago if crossed_above_200dma else "No"
        below_50dma_last_15_sessions = sessions_below_50dma_ago if crossed_below_50dma else "No"
        below_200dma_last_15_sessions = sessions_below_200dma_ago if crossed_below_200dma else "No"

        # Flags for latest price > 50DMA and 200DMA
        flag_above_50dma = "Yes" if latest_price > latest_50dma else "No"
        flag_above_200dma = "Yes" if latest_price > latest_200dma else "No"

        # Append to CSV and Excel data
        csv_data.append([
            stock, latest_price, latest_50dma, latest_200dma, trend,
            flag_above_50dma, flag_above_200dma,
            above_50dma_last_15_sessions,
            above_200dma_last_15_sessions,
            below_50dma_last_15_sessions,
            below_200dma_last_15_sessions
        ])

    # Output the categorized stocks to the console (screen)
    print("\nStocks above the 50-day moving average:")
    for stock in stocks_above_50dma:
        print(stock)

    print("\nStocks above the 200-day moving average:")
    for stock in stocks_above_200dma:
        print(stock)

    print("\nStocks between the 50DMA and 200DMA:")
    for stock in stocks_between_50dma_and_200dma:
        print(stock)

    print("\nStocks below the 50-day moving average:")
    for stock in stocks_below_50dma:
        print(stock)

    # Output the results to CSV
    csv_file = 'stocks_summary.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Symbol", "Current Price", "50DMA", "200DMA", "Trend (50DMA vs 200DMA)",
            "Above 50DMA Flag", "Above 200DMA Flag",
            "Above 50DMA Last 15 Sessions", "Above 200DMA Last 15 Sessions",
            "Below 50DMA Last 15 Sessions", "Below 200DMA Last 15 Sessions"
        ])
        writer.writerows(csv_data)

    print(f"CSV file saved as {csv_file}")

    # Output the results to Excel
    excel_file = 'stocks_summary.xlsx'
    df = pd.DataFrame(csv_data, columns=[
        "Symbol", "Current Price", "50DMA", "200DMA", "Trend (50DMA vs 200DMA)",
        "Above 50DMA Flag", "Above 200DMA Flag",
        "Above 50DMA Last 15 Sessions", "Above 200DMA Last 15 Sessions",
        "Below 50DMA Last 15 Sessions", "Below 200DMA Last 15 Sessions"
    ])
    df.to_excel(excel_file, index=False)


    print(f"Excel file saved with formatting as {excel_file}")
    print(f"Excel file saved as {excel_file}")

# Call the function with the path to your stocks.txt file
check_stocks_combined('stocks.txt')

