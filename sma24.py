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

    # Data for CSV and Excel output
    csv_data = []

    for stock in stocks:
        print(f"Processing stock: {stock}")
        # Fetch the stock data for the last 1 year
        data = yf.download(stock, period="1y", interval="1d", progress=False)

        # Calculate the 50-day, 200-day moving averages, and EMAs
        data['50dma'] = data['Close'].rolling(window=50).mean()
        data['200dma'] = data['Close'].rolling(window=200).mean()
        data['50ema'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['200ema'] = data['Close'].ewm(span=200, adjust=False).mean()

        # Calculate MACD and RSI
        data = calculate_macd(data)
        data = calculate_rsi(data)

        # Get the latest stock price, 50-day, 200-day moving averages and EMAs
        latest_price = data['Close'].iloc[-1]
        latest_50dma = data['50dma'].iloc[-1]
        latest_200dma = data['200dma'].iloc[-1]
        latest_50ema = data['50ema'].iloc[-1]
        latest_200ema = data['200ema'].iloc[-1]
        latest_macd = data['MACD'].iloc[-1]
        latest_signal = data['Signal'].iloc[-1]
        latest_rsi = data['RSI'].iloc[-1]

        # Determine the trend based on the 50DMA and 200DMA
        trend = "Up" if latest_50dma >= latest_200dma else "Down"

        # Check for Golden Cross (50DMA > 200DMA) in the last 15 sessions
        recent_data = data.iloc[-16:]  # Get the last 16 trading sessions
        golden_cross_sessions_ago = "No"
        for i in range(1, 16):
            prev_50dma = recent_data['50dma'].iloc[i - 1]
            prev_200dma = recent_data['200dma'].iloc[i - 1]
            curr_50dma = recent_data['50dma'].iloc[i]
            curr_200dma = recent_data['200dma'].iloc[i]

            if prev_50dma <= prev_200dma and curr_50dma > curr_200dma:
                golden_cross_sessions_ago = 15 - i
                break

        # Check for crossovers in the last 15 sessions
        crossed_above_50dma = False
        crossed_above_200dma = False
        crossed_below_50dma = False
        crossed_below_200dma = False
        sessions_50dma_ago = None
        sessions_200dma_ago = None
        sessions_below_50dma_ago = None
        sessions_below_200dma_ago = None

        for i in range(1, 16):
            prev_close = recent_data['Close'].iloc[i - 1]
            prev_50dma = recent_data['50dma'].iloc[i - 1]
            prev_200dma = recent_data['200dma'].iloc[i - 1]
            curr_close = recent_data['Close'].iloc[i]
            curr_50dma = recent_data['50dma'].iloc[i]
            curr_200dma = recent_data['200dma'].iloc[i]

            if prev_close < prev_50dma and curr_close > curr_50dma:
                crossed_above_50dma = True
                sessions_50dma_ago = 15 - i

            if prev_close < prev_200dma and curr_close > curr_200dma:
                crossed_above_200dma = True
                sessions_200dma_ago = 15 - i

            if prev_close > prev_50dma and curr_close < curr_50dma:
                crossed_below_50dma = True
                sessions_below_50dma_ago = 15 - i

            if prev_close > prev_200dma and curr_close < curr_200dma:
                crossed_below_200dma = True
                sessions_below_200dma_ago = 15 - i

        # Prepare the row for CSV and Excel
        above_50dma_last_15_sessions = sessions_50dma_ago if crossed_above_50dma else "No"
        above_200dma_last_15_sessions = sessions_200dma_ago if crossed_above_200dma else "No"
        below_50dma_last_15_sessions = sessions_below_50dma_ago if crossed_below_50dma else "No"
        below_200dma_last_15_sessions = sessions_below_200dma_ago if crossed_below_200dma else "No"

        flag_above_50dma = "Yes" if latest_price > latest_50dma else "No"
        flag_above_200dma = "Yes" if latest_price > latest_200dma else "No"

        macd_trend = "Up" if latest_macd > latest_signal else "Down"

        csv_data.append([
            stock, latest_price, latest_50ema, latest_200ema, latest_50dma,
            latest_200dma, trend, golden_cross_sessions_ago,
            flag_above_50dma, flag_above_200dma, above_50dma_last_15_sessions,
            above_200dma_last_15_sessions, below_50dma_last_15_sessions,
            below_200dma_last_15_sessions, latest_macd, latest_signal,
            macd_trend, latest_rsi
        ])

    # Output the results to CSV
    csv_file = 'stocks_summary.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Symbol", "Current Price", "50EMA", "200EMA", "50DMA",
            "200DMA", "Trend (50DMA vs 200DMA)", "Golden Cross Sessions Ago",
            "Above 50DMA Flag", "Above 200DMA Flag",
            "Above 50DMA Last 15 Sessions", "Above 200DMA Last 15 Sessions",
            "Below 50DMA Last 15 Sessions", "Below 200DMA Last 15 Sessions",
            "MACD", "Signal", "MACD Trend", "RSI"
        ])
        writer.writerows(csv_data)

    # Output the results to Excel
    excel_file = 'stocks_summary.xlsx'
    df = pd.DataFrame(csv_data, columns=[
        "Symbol", "Current Price", "50EMA", "200EMA", "50DMA",
        "200DMA", "Trend (50DMA vs 200DMA)", "Golden Cross Sessions Ago",
        "Above 50DMA Flag", "Above 200DMA Flag",
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

