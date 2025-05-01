import pandas as pd
import sqlite3
from datetime import datetime
import time

# File path to the Excel file (update this to your file path)
EXCEL_FILE = 'zack2.xlsx'

# SQLite database file (update this to your database file)
DB_FILE = 'grok_stocks.db'

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
    try:
        df = pd.read_excel(EXCEL_FILE, na_values=['#NA'])
    except FileNotFoundError:
        print(f"Error: Excel file '{EXCEL_FILE}' not found.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Print column names for debugging
    #print("Columns in Excel file:", df.columns.tolist())

    # Define expected column names (UPDATE THESE TO MATCH YOUR EXCEL FILE)
    column_mapping = {
        'TICKER': 'TICKER',  # Replace with actual column name, e.g., 'SYMBOL'
        'NAME': 'NAME',     # e.g., 'COMPANY_NAME'
        'ADR': None,        # Optional, set to None if not present
        'FISCAL_YEAR_END': None,  # e.g., 'FISCAL_YEAR'
        'ANALYSTS': None,   # Optional, set to None if not present
        'IN_S&P500': None,  # e.g., 'SP500'
        'COUNTRY_CODE': None,  # e.g., 'COUNTRY'
        'SECTOR_CODE': None,  # e.g., 'SECTOR_ID'
        'SECTOR': 'SECTOR',  # e.g., 'SECTOR_NAME'
        'INDUSTRY_CODE': None,  # e.g., 'INDUSTRY_ID'
        'INDUSTRY': 'INDUSTRY',  # e.g., 'INDUSTRY_NAME'
        'EX-DIVIDEND_DATE': 'EX-DIVIDEND_DATE',  # e.g., 'EX_DIV_DATE'
        'PAYMENT_DATE': 'PAYMENT_DATE',  # e.g., 'PAY_DATE'
        'DIVIDEND_AMOUNT': 'DIVIDEND_AMOUNT',  # e.g., 'DIVIDEND'
        'ROE': 'ROE',  # e.g., 'RETURN_ON_EQUITY'
        'CURRENT_RATIO': None,
        'QUICK_RATIO': None,
        'TOTAL_DEBT/EQUITY': None,  # e.g., 'DEBT_EQUITY'
        'TOTAL_DEBT/CAPITAL': None,  # e.g., 'DEBT_CAPITAL'
        'EBIT_MARGIN': None,
        'REPORT DATE': 'REPORT DATE'  # e.g., 'REPORT_DATE'
    }

    # Connect to SQLite database with a higher timeout (30 seconds)
    max_attempts = 3
    attempt = 1
    conn = None
    while attempt <= max_attempts:
        try:
            conn = sqlite3.connect(DB_FILE, timeout=30)
            cursor = conn.cursor()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Database is locked, attempt {attempt}/{max_attempts}. Retrying in 5 seconds...")
                time.sleep(5)
                attempt += 1
            else:
                raise
    if conn is None:
        print("Error: Could not connect to database after multiple attempts.")
        return

    with conn:
        try:
            # 1. Insert into Companies
            company_cols = [
                column_mapping['TICKER'], column_mapping['NAME'], column_mapping['ADR'],
                column_mapping['FISCAL_YEAR_END'], column_mapping['ANALYSTS'], column_mapping['IN_S&P500'],
                column_mapping['COUNTRY_CODE'], column_mapping['SECTOR_CODE'], column_mapping['SECTOR'],
                column_mapping['INDUSTRY_CODE'], column_mapping['INDUSTRY']
            ]
            company_cols = [col for col in company_cols if col and col in df.columns]
            if not company_cols:
                print("Error: No valid company columns found. Check column_mapping.")
                return

            companies_data = df[company_cols].drop_duplicates()
            for _, row in companies_data.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO Companies (
                        ticker, name, adr, fiscal_year_end, analysts, in_sp500, country_code,
                        sector_code, sector_name, industry_code, industry_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    row.get(column_mapping['INDUSTRY'], None)
                ))

            # 2. Insert into EarningsEstimates
            earnings_columns = [col for col in df.columns if col.isdigit() and 1999 <= int(col) <= 2027]
            for _, row in df.iterrows():
                ticker = row[column_mapping['TICKER']]
                for year in earnings_columns:
                    estimate = clean_numeric(row[year])
                    if estimate is not None:
                        cursor.execute('''
                            INSERT OR REPLACE INTO EarningsEstimates (ticker, year, estimate)
                            VALUES (?, ?, ?)
                        ''', (ticker, int(year), estimate))

            # 3. Insert into StockPrices
            stock_years = set(col.split('_')[-1] for col in df.columns if col.startswith(('LOW_', 'HIGH_', 'CLOSE_')))
            for _, row in df.iterrows():
                ticker = row[column_mapping['TICKER']]
                for year in stock_years:
                    low_col = f'LOW_{year}'
                    high_col = f'HIGH_{year}'
                    close_col = f'CLOSE_{year}'
                    low_price = clean_numeric(row.get(low_col)) if low_col in df.columns else None
                    high_price = clean_numeric(row.get(high_col)) if high_col in df.columns else None
                    close_price = clean_numeric(row.get(close_col)) if close_col in df.columns else None
                    if any(price is not None for price in [low_price, high_price, close_price]):
                        cursor.execute('''
                            INSERT OR REPLACE INTO StockPrices (ticker, year, low_price, high_price, close_price)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (ticker, int(year), low_price, high_price, close_price))

            # 4. Insert into Dividends
            dividend_cols = [
                column_mapping['EX-DIVIDEND_DATE'],
                column_mapping['PAYMENT_DATE'],
                column_mapping['DIVIDEND_AMOUNT']
            ]
            dividend_cols = [col for col in dividend_cols if col and col in df.columns]
            if dividend_cols:
                for _, row in df.iterrows():
                    ticker = row[column_mapping['TICKER']]
                    ex_dividend_date = standardize_date(row.get(column_mapping['EX-DIVIDEND_DATE']))
                    payment_date = standardize_date(row.get(column_mapping['PAYMENT_DATE']))
                    dividend_amount = clean_numeric(row.get(column_mapping['DIVIDEND_AMOUNT']))
                    if ex_dividend_date and dividend_amount is not None:
                        cursor.execute('''
                            INSERT OR REPLACE INTO Dividends (ticker, ex_dividend_date, payment_date, dividend_amount)
                            VALUES (?, ?, ?, ?)
                        ''', (ticker, ex_dividend_date, payment_date, dividend_amount))

            # 5. Insert into FinancialMetrics
            metric_cols = [
                column_mapping['ROE'], column_mapping['CURRENT_RATIO'], column_mapping['QUICK_RATIO'],
                column_mapping['TOTAL_DEBT/EQUITY'], column_mapping['TOTAL_DEBT/CAPITAL'],
                column_mapping['EBIT_MARGIN'], column_mapping['REPORT DATE']
            ]
            metric_cols = [col for col in metric_cols if col and col in df.columns]
            for _, row in df.iterrows():
                ticker = row[column_mapping['TICKER']]
                year = 2023  # Adjust based on your data
                roe = clean_numeric(row.get(column_mapping['ROE'])) if column_mapping['ROE'] in df.columns else None
                current_ratio = clean_numeric(row.get(column_mapping['CURRENT_RATIO'])) if column_mapping['CURRENT_RATIO'] in df.columns else None
                quick_ratio = clean_numeric(row.get(column_mapping['QUICK_RATIO'])) if column_mapping['QUICK_RATIO'] in df.columns else None
                total_debt_equity = clean_numeric(row.get(column_mapping['TOTAL_DEBT/EQUITY'])) if column_mapping['TOTAL_DEBT/EQUITY'] in df.columns else None
                total_debt_capital = clean_numeric(row.get(column_mapping['TOTAL_DEBT/CAPITAL'])) if column_mapping['TOTAL_DEBT/CAPITAL'] in df.columns else None
                ebit_margin = clean_numeric(row.get(column_mapping['EBIT_MARGIN'])) if column_mapping['EBIT_MARGIN'] in df.columns else None
                report_date = standardize_date(row.get(column_mapping['REPORT DATE'])) if column_mapping['REPORT DATE'] in df.columns else None
                if any(val is not None for val in [roe, current_ratio, quick_ratio, total_debt_equity, total_debt_capital, ebit_margin, report_date]):
                    cursor.execute('''
                        INSERT OR REPLACE INTO FinancialMetrics (
                            ticker, year, roe, current_ratio, quick_ratio, total_debt_equity,
                            total_debt_capital, ebit_margin, report_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker, year, roe, current_ratio, quick_ratio, total_debt_equity,
                        total_debt_capital, ebit_margin, report_date
                    ))

            # Commit changes
            conn.commit()
            print("Data uploaded successfully to SQLite database.")

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("Error: Database is locked. Ensure no other processes are accessing the database.")
            else:
                raise
        except Exception as e:
            print(f"Error during database operations: {e}")
            raise

if __name__ == '__main__':
    main()