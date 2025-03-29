import yfinance as yf
import pandas as pd
import csv
import openpyxl
from openpyxl.styles import Alignment, Font

def calculate_macd(data, fastperiod=12, slowperiod=26, signalperiod=9):
    # Calculate MACD and Signal line using simple moving averages
    data['EMA_fast'] = data['Close'].ewm(span=fastperiod, adjust=False).mean()
    data['EMA_slow'] = data['Close'].ewm(span=slowperiod, adjust=False).mean()
    data['MACD'] = data['EMA_fast'] - data['EMA_slow']
    data['Signal'] = data['MACD'].ewm(span=signalperiod, adjust=False).mean()
    return data

def calculate_rsi(data, period=14):
    # Calculate RSI using rolling window and price changes
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

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
        data = yf.download(stock, period="1y", interval="1d", progress=False)

        if data.empty:
           print(f"Warning: No data available for {stock}. Skipping...")
           continue  # Skip to the next stock


        # Calculate the 50-day and 200-day moving averages
        data['50dma'] = data['Close'].rolling(window=50).mean()
        data['200dma'] = data['Close'].rolling(window=200).mean()

        # Calculate 50EMA and 200EMA
        data['50EMA'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['200EMA'] = data['Close'].ewm(span=200, adjust=False).mean()


        # Calculate MACD and RSI
        data = calculate_macd(data)
        data = calculate_rsi(data)

        # Get the latest stock price, 50-day, and 200-day moving averages
        latest_price = data['Close'].iloc[-1]
        latest_50dma = data['50dma'].iloc[-1]
        latest_200dma = data['200dma'].iloc[-1]
        latest_macd = data['MACD'].iloc[-1]
        latest_signal = data['Signal'].iloc[-1]
        latest_rsi = data['RSI'].iloc[-1]

        # Calculate the latest 50EMA and 200EMA
        latest_50EMA = data['50EMA'].iloc[-1]
        latest_200EMA = data['200EMA'].iloc[-1]

        # Ensure that all values are scalars
        if isinstance(latest_50EMA, pd.Series):
          latest_50EMA = latest_50EMA.item()
        if isinstance(latest_200EMA, pd.Series):
          latest_200EMA = latest_200EMA.item()

        # Ensure that all values are scalars
        if isinstance(latest_price, pd.Series):
            latest_price = latest_price.item()
        if isinstance(latest_50dma, pd.Series):
            latest_50dma = latest_50dma.item()
        if isinstance(latest_200dma, pd.Series):
            latest_200dma = latest_200dma.item()
        if isinstance(latest_macd, pd.Series):
            latest_macd = latest_macd.item()
        if isinstance(latest_signal, pd.Series):
            latest_signal = latest_signal.item()
        if isinstance(latest_rsi, pd.Series):
            latest_rsi = latest_rsi.item()

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


        # Check for Golden Cross (50DMA > 200DMA) in the last 15 sessions
        golden_cross_sessions_ago = "No"
        for i in range(1, 16):  # Check the last 15 sessions
            prev_50dma = recent_data['50dma'].iloc[i - 1]
            prev_200dma = recent_data['200dma'].iloc[i - 1]
            curr_50dma = recent_data['50dma'].iloc[i]
            curr_200dma = recent_data['200dma'].iloc[i]

            # Ensure these are scalar values
            prev_50dma = prev_50dma.item() if isinstance(prev_50dma, pd.Series) else prev_50dma
            prev_200dma = prev_200dma.item() if isinstance(prev_200dma, pd.Series) else prev_200dma
            curr_50dma = curr_50dma.item() if isinstance(curr_50dma, pd.Series) else curr_50dma
            curr_200dma = curr_200dma.item() if isinstance(curr_200dma, pd.Series) else curr_200dma

            # Check for Golden Cross
            if prev_50dma <= prev_200dma and curr_50dma > curr_200dma:
                golden_cross_sessions_ago = 15 - i  # Sessions ago the Golden Cross occurred
                break  # Stop checking once a Golden Cross is found

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
        
        # Determine MACD Trend (Up or Down)
        macd_trend = "Up" if latest_macd > latest_signal else "Down"

        # Append to CSV and Excel data

        csv_data.append([
            stock, latest_price, latest_50EMA, latest_200EMA, latest_50dma, latest_200dma, trend,
            golden_cross_sessions_ago,  # Add Golden Cross Over column
            flag_above_50dma, flag_above_200dma,
            above_50dma_last_15_sessions,
            above_200dma_last_15_sessions,
            below_50dma_last_15_sessions,
            below_200dma_last_15_sessions,
            latest_macd, latest_signal, macd_trend, latest_rsi
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
        "Symbol", "Current Price", "50EMA", "200EMA", "50DMA", "200DMA", "Trend (50DMA vs 200DMA)", 
        "Golden Cross Sessions Ago", "Above 50DMA Flag", "Above 200DMA Flag",
        "Above 50DMA Last 15 Sessions", "Above 200DMA Last 15 Sessions",
        "Below 50DMA Last 15 Sessions", "Below 200DMA Last 15 Sessions",
        "MACD", "Signal", "MACD Trend", "RSI"
        ])
        writer.writerows(csv_data)

    print(f"CSV file saved as {csv_file}")

    # Output the results to Excel
    excel_file = 'stocks_summary.xlsx'
    df = pd.DataFrame(csv_data, columns=[
        "Symbol", "Current Price", "50EMA", "200EMA", "50DMA", "200DMA", "Trend (50DMA vs 200DMA)", 
        "Golden Cross Sessions Ago", "Above 50DMA Flag", "Above 200DMA Flag",
        "Above 50DMA Last 15 Sessions", "Above 200DMA Last 15 Sessions",
        "Below 50DMA Last 15 Sessions", "Below 200DMA Last 15 Sessions",
        "MACD", "Signal", "MACD Trend", "RSI"
    ])


    # Save the DataFrame to an Excel file first
    df.to_excel(excel_file, index=False)

    # Open the workbook using openpyxl to modify formatting
    wb = openpyxl.load_workbook(excel_file)
    ws = wb.active

    # Set font size to 14 and left-align all columns
    for row in ws.iter_rows():
        for cell in row:
            cell.font = Font(size=14)
            cell.alignment = Alignment(horizontal='left')

    # Set column width to 20 for all columns
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)  # Add some padding
        ws.column_dimensions[column].width = 20

    # Apply auto filter
    ws.auto_filter.ref = ws.dimensions


    # Apply freezing to the first row and first column
    ws.freeze_panes = 'B2'  # Freeze column A and row 1

    # Save the workbook with the applied formatting
    wb.save(excel_file)
    print(f"Excel file saved as {excel_file}")

# Call the function with the path to your stocks.txt file
check_stocks_combined('stocks.txt')

