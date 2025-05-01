import sqlite3

# Step 1: Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect('grok_stocks.db')
cursor = conn.cursor()

# Step 2: Create  table
cursor.executescript('''
     
-- Companies table to store company details, including sector and industry information
    CREATE TABLE Companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    adr TEXT, -- Can be NULL if not applicable
    fiscal_year_end TEXT, -- e.g., 'DEC', 'SEP'
    analysts INTEGER, -- Number of analysts, can be NULL
    in_sp500 TEXT, -- 'Y' or 'N', can be NULL
    country_code TEXT, -- e.g., 'USA', 'CHN'
    sector_code INTEGER, -- Sector code, e.g., 4 for MEDICAL
    sector_name TEXT, -- Sector name, e.g., 'MEDICAL'
    industry_code INTEGER, -- Industry code, e.g., 104 for MEDICAL PRODUCTS
    industry_name TEXT -- Industry name, e.g., 'MEDICAL PRODUCTS'
    );

-- EarningsEstimates table to store yearly earnings estimates
    CREATE TABLE EarningsEstimates (
    ticker TEXT,
    year INTEGER,
    estimate REAL, -- Earnings estimate value, NULL for #NA
    PRIMARY KEY (ticker, year),
    FOREIGN KEY (ticker) REFERENCES Companies(ticker)
    );

-- StockPrices table to store yearly stock price data
    CREATE TABLE StockPrices (
    ticker TEXT,
    year INTEGER,
    low_price REAL, -- LOW price, NULL for #NA
    high_price REAL, -- HIGH price, NULL for #NA
    close_price REAL, -- CLOSE price, NULL for #NA
    PRIMARY KEY (ticker, year),
    FOREIGN KEY (ticker) REFERENCES Companies(ticker)
    );

-- Dividends table to store dividend payment details
    CREATE TABLE Dividends (
    ticker TEXT,
    ex_dividend_date TEXT, -- YYYY-MM-DD, NULL for invalid dates
    payment_date TEXT, -- YYYY-MM-DD, NULL for invalid dates
    dividend_amount REAL, -- Dividend amount, NULL if not applicable
    PRIMARY KEY (ticker, ex_dividend_date),
    FOREIGN KEY (ticker) REFERENCES Companies(ticker)
    );

-- FinancialMetrics table to store financial metrics by year, now including report_date
    CREATE TABLE FinancialMetrics (
    ticker TEXT,
    year INTEGER,
    roe REAL, -- Return on Equity, NULL for #NA
    current_ratio REAL, -- Current Ratio, NULL for #NA
    quick_ratio REAL, -- Quick Ratio, NULL for #NA
    total_debt_equity REAL, -- Total Debt / Total Equity, NULL for #NA
    total_debt_capital REAL, -- Total Debt / Total Capital, NULL for #NA
    ebit_margin REAL, -- EBIT Margin, NULL for #NA
    report_date TEXT, -- YYYY-MM-DD, NULL for invalid dates
    PRIMARY KEY (ticker, year),
    FOREIGN KEY (ticker) REFERENCES Companies(ticker)
    );
    

''')

# Commit the changes
conn.commit()

# Step 4: Read data
 

# Step 5: Update data
 

# Step 6: Delete data
 

# Final read to see changes
print("Final read of all tables:")
# cursor.execute("SELECT * FROM Companies")

# Close connection
conn.close()
