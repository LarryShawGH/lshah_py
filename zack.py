import sqlite3

# Step 1: Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect('stocks.db')
cursor = conn.cursor()

# Step 2: Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
''')


cursor.executescript('''
     
    CREATE TABLE IF NOT EXISTS Companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    adr_type TEXT,             -- ADR / COM
    fiscal_year_end TEXT,      -- e.g., 'DEC', 'OCT'
    index_member BOOLEAN       -- TRUE if part of index (e.g., S&P 500)
    );

-- Table 2: Analyst Coverage
    CREATE TABLE IF NOT EXISTS AnalystCoverage (
    coverage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    snapshot_date DATE,
    num_analysts INTEGER,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)    
    );
               
-- Table 3: Sales Estimates
    CREATE TABLE SalesEstimates (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    fiscal_year INTEGER,
    estimate_value REAL,
    snapshot_date DATE,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
    );

-- Table 4: Financial Metrics (normalized multi-metric format)
    CREATE TABLE FinancialMetrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    fiscal_year INTEGER,
    metric_type TEXT,           -- e.g., 'ROE', 'EBIT Margin', 'EPS'
    value REAL,
    snapshot_date DATE,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
    );     

-- Table 5: Dividends
    CREATE TABLE Dividends (
    dividend_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    forward_annual_dividend REAL,
    ex_div_date DATE,
    pay_date DATE,
    snapshot_date DATE,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
    );
                   
-- Table 6: Stock Prices
    CREATE TABLE StockPrices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    price_date DATE,          -- Use NULL or generic period if exact date is not available
    price_type TEXT,          -- 'LOW', 'HIGH', 'CLOSE'
    value REAL,
    snapshot_date DATE,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
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
