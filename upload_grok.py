import pandas as pd
import sqlite3
from datetime import datetime

# File path to the Excel file (update this to your file path)
EXCEL_FILE = 'zack2.xlsx'

# SQLite database file (update this to your database file)
DB_FILE = 'grok_stocks.db'

# Load Excel file
excel_path = "zack2.xlsx"
df_raw = pd.read_excel(excel_path, sheet_name='DATA', header=None)


def standardize_date(date_str):
    """Convert date strings to YYYY-MM-DD format or return None for invalid dates."""
    if not date_str or date_str == '--/--/----' or pd.isna(date_str):
        return None
    try:
        # Handle numeric dates like 20250401
        if isinstance(date_str, (int, float)) or (isinstance(date_str, str) and date_str.isdigit()):
            date_str = str(int(date_str))
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        # Handle MM/DD/YYYY or similar
        return pd.to_datetime(date_str, errors='coerce').strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None

def clean_numeric(value):
    """Convert value to float or None if invalid (e.g., #NA)."""
    if pd.isna(value) or value == '#NA':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def main():
    # Read the Excel file
    df = pd.read_excel(EXCEL_FILE, na_values=['#NA'])
    
    # Print column names for debugging
    print("Columns in Excel file:", df.columns.tolist())
    print("Excelfile: ", df.head(6))  # Preview first 6 rows of the DataFrame

    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Define expected column names (UPDATE THESE TO MATCH YOUR EXCEL FILE)
    column_mapping = {
        'TICKER': 'TICKER',  # Replace with actual column name, e.g., 'SYMBOL'
        'NAME': 'NAME',     # e.g., 'COMPANY_NAME'
        'ADR': 'ADR',       # Optional, set to None if not present
        'FISCAL_YEAR_END': 'FY END',  # e.g., 'FISCAL_YEAR'
        'ANALYSTS': 'ANALYSTS',  # Optional, set to None if not present
        'IN_S&P500': 'IN_S&P500',  # e.g., 'SP500'
        'COUNTRY_CODE': 'COUNTRY_CODE',  # e.g., 'COUNTRY'
        'SECTOR_CODE': 'SECTOR_CODE',  # e.g., 'SECTOR_ID'
        'SECTOR': 'SECTOR',  # e.g., 'SECTOR_NAME'
        'INDUSTRY_CODE': 'INDUSTRY_CODE',  # e.g., 'INDUSTRY_ID'
        #'INDUSTRY': 'INDUSTRY',  # e.g., 'INDUSTRY_NAME'
        'EX-DIVIDEND_DATE': 'EX-DIVIDEND_DATE',  # e.g., 'EX_DIV_DATE'
        'PAYMENT_DATE': 'PAYMENT_DATE',  # e.g., 'PAY_DATE'
        'DIVIDEND_AMOUNT': 'DIVIDEND_AMOUNT',  # e.g., 'DIVIDEND'
        'ROE': 'ROE',  # e.g., 'RETURN_ON_EQUITY'
        'CURRENT_RATIO': 'CURRENT_RATIO',
        'QUICK_RATIO': 'QUICK_RATIO',
        'TOTAL_DEBT/EQUITY': 'TOTAL_DEBT/EQUITY',  # e.g., 'DEBT_EQUITY'
        'TOTAL_DEBT/CAPITAL': 'TOTAL_DEBT/CAPITAL',  # e.g., 'DEBT_CAPITAL'
        'EBIT_MARGIN': 'EBIT_MARGIN',
        'REPORT DATE': 'REPORT DATE'  # e.g., 'REPORT_DATE'
    }
        # 1. Insert into Companies
    company_cols = [
        column_mapping['TICKER'], column_mapping['NAME'], column_mapping['ADR'],
        column_mapping['FISCAL_YEAR_END'], column_mapping['ANALYSTS'], column_mapping['IN_S&P500'],
        column_mapping['COUNTRY_CODE'], column_mapping['SECTOR_CODE'], column_mapping['SECTOR'],
        column_mapping['INDUSTRY_CODE'], #column_mapping['INDUSTRY']
    ]
    # Filter out columns that don't exist in the DataFrame
    company_cols = [col for col in company_cols if col in df.columns]
    if not company_cols:
        print("Error: No valid company columns found. Check column_mapping.")
        return

    companies_data = df[company_cols].drop_duplicates()
    for _, row in companies_data.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO Companies (
                ticker, name, adr, fiscal_year_end, analysts, in_sp500, country_code,
                sector_code, sector_name, industry_code 
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row.get(column_mapping['TICKER'], None),
            row.get(column_mapping['NAME'], None),
            row.get(column_mapping['ADR'], None),
            row.get(column_mapping['FISCAL_YEAR_END'], None),
            clean_numeric(row.get(column_mapping['ANALYSTS'], None)),
            row.get(column_mapping['IN_S&P500'], None),
            row.get(column_mapping['COUNTRY_CODE'], None),
            clean_numeric(row.get(column_mapping['SECTOR_CODE'], None)),
            row.get(column_mapping['SECTOR'], None),
            clean_numeric(row.get(column_mapping['INDUSTRY_CODE'], None)),
            #row.get(column_mapping['INDUSTRY'], None)
        ))


    # 1. Insert into Companies
    # companies_data = df[[
    #     'TICKER', 'NAME', 'ADR', 'FISCAL_YEAR_END', 'ANALYSTS', 'IN_S&P500', 'COUNTRY_CODE',
    #     'SECTOR_CODE', 'SECTOR', 'INDUSTRY_CODE', 'INDUSTRY'
    # ]].drop_duplicates()

    # for _, row in companies_data.iterrows():
    #     cursor.execute('''
    #         INSERT OR REPLACE INTO Companies (
    #             ticker, name, adr, fiscal_year_end, analysts, in_sp500, country_code,
    #             sector_code, sector_name, industry_code, industry_name
    #         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #     ''', (
    #         row['TICKER'],
    #         row['NAME'],
    #         row['ADR'] if pd.notna(row['ADR']) else None,
    #         row['FISCAL_YEAR_END'] if pd.notna(row['FISCAL_YEAR_END']) else None,
    #         clean_numeric(row['ANALYSTS']),
    #         row['IN_S&P500'] if pd.notna(row['IN_S&P500']) else None,
    #         row['COUNTRY_CODE'] if pd.notna(row['COUNTRY_CODE']) else None,
    #         clean_numeric(row['SECTOR_CODE']),
    #         row['SECTOR'] if pd.notna(row['SECTOR']) else None,
    #         clean_numeric(row['INDUSTRY_CODE']),
    #         row['INDUSTRY'] if pd.notna(row['INDUSTRY']) else None
    #     ))

    # # 2. Insert into EarningsEstimates
    # earnings_columns = [col for col in df.columns if col.isdigit() and 1999 <= int(col) <= 2027]
    # for _, row in df.iterrows():
    #     ticker = row['TICKER']
    #     for year in earnings_columns:
    #         estimate = clean_numeric(row[year])
    #         if estimate is not None:  # Only insert if estimate is valid
    #             cursor.execute('''
    #                 INSERT OR REPLACE INTO EarningsEstimates (ticker, year, estimate)
    #                 VALUES (?, ?, ?)
    #             ''', (ticker, int(year), estimate))

    # # 3. Insert into StockPrices
    # stock_years = set(col.split('_')[-1] for col in df.columns if col.startswith(('LOW_', 'HIGH_', 'CLOSE_')))
    # for _, row in df.iterrows():
    #     ticker = row['TICKER']
    #     for year in stock_years:
    #         low_col = f'LOW_{year}'
    #         high_col = f'HIGH_{year}'
    #         close_col = f'CLOSE_{year}'
    #         low_price = clean_numeric(row.get(low_col))
    #         high_price = clean_numeric(row.get(high_col))
    #         close_price = clean_numeric(row.get(close_col))
    #         if any(price is not None for price in [low_price, high_price, close_price]):
    #             cursor.execute('''
    #                 INSERT OR REPLACE INTO StockPrices (ticker, year, low_price, high_price, close_price)
    #                 VALUES (?, ?, ?, ?, ?)
    #             ''', (ticker, int(year), low_price, high_price, close_price))

    # # 4. Insert into Dividends
    # dividend_cols = ['EX-DIVIDEND_DATE', 'PAYMENT_DATE', 'DIVIDEND_AMOUNT']
    # if all(col in df.columns for col in dividend_cols):
    #     for _, row in df.iterrows():
    #         ticker = row['TICKER']
    #         ex_dividend_date = standardize_date(row['EX-DIVIDEND_DATE'])
    #         payment_date = standardize_date(row['PAYMENT_DATE'])
    #         dividend_amount = clean_numeric(row['DIVIDEND_AMOUNT'])
    #         if ex_dividend_date and dividend_amount is not None:  # Only insert if key fields are valid
    #             cursor.execute('''
    #                 INSERT OR REPLACE INTO Dividends (ticker, ex_dividend_date, payment_date, dividend_amount)
    #                 VALUES (?, ?, ?, ?)
    #             ''', (ticker, ex_dividend_date, payment_date, dividend_amount))

    # # 5. Insert into FinancialMetrics
    # metric_cols = [
    #     'ROE', 'CURRENT_RATIO', 'QUICK_RATIO', 'TOTAL_DEBT/EQUITY',
    #     'TOTAL_DEBT/CAPITAL', 'EBIT_MARGIN', 'REPORT DATE'
    # ]
    # metric_cols = [col for col in metric_cols if col in df.columns]
    # for _, row in df.iterrows():
    #     ticker = row['TICKER']
    #     year = 2023  # Adjust based on your data; assuming metrics are for a specific year
    #     roe = clean_numeric(row.get('ROE'))
    #     current_ratio = clean_numeric(row.get('CURRENT_RATIO'))
    #     quick_ratio = clean_numeric(row.get('QUICK_RATIO'))
    #     total_debt_equity = clean_numeric(row.get('TOTAL_DEBT/EQUITY'))
    #     total_debt_capital = clean_numeric(row.get('TOTAL_DEBT/CAPITAL'))
    #     ebit_margin = clean_numeric(row.get('EBIT_MARGIN'))
    #     report_date = standardize_date(row.get('REPORT DATE'))
    #     if any(val is not None for val in [roe, current_ratio, quick_ratio, total_debt_equity, total_debt_capital, ebit_margin, report_date]):
    #         cursor.execute('''
    #             INSERT OR REPLACE INTO FinancialMetrics (
    #                 ticker, year, roe, current_ratio, quick_ratio, total_debt_equity,
    #                 total_debt_capital, ebit_margin, report_date
    #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    #         ''', (
    #             ticker, year, roe, current_ratio, quick_ratio, total_debt_equity,
    #             total_debt_capital, ebit_margin, report_date
    #         ))

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Data uploaded successfully to SQLite database.")

if __name__ == '__main__':
    main()