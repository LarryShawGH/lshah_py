import pandas as pd
import sqlite3

# Load Excel file
excel_path = "zack1.xlsm"
df_raw = pd.read_excel(excel_path, sheet_name='DATA AFTER REFRESH', header=None)



# Option 2: Use multi-level headers (if the two rows represent hierarchical headers)
# Read the Excel file with the first two rows as headers
df = pd.read_excel('zack1.xlsm', header=[0, 1])
# If you need to flatten the multi-index columns
df.columns = ['_'.join(str(x) for x in col).strip() for col in df.columns.values]

#df.columns = ['_'.join(col).strip() for col in df.columns.values]
print("header ", df.columns)

# Extract headers and data
headers = df_raw.iloc[0].values
df = pd.DataFrame(df_raw.iloc[2:].values, columns=headers)
#print("Header", headers)
print(df.head(6))  # Preview first 6 rows of the DataFrame

# Load the newly uploaded Excel file to inspect the updated structure

xls = pd.ExcelFile(excel_path)

# Preview sheet names and load the relevant one
sheet_name = 'DATA AFTER REFRESH'
df_preview = xls.parse(sheet_name, header=None)
df_preview.head(6)  # View first 6 rows to identify new header and data structure

print(df_preview.head(6))

# # Strip and clean column headers
# df.columns = [str(col).strip().upper() for col in df.columns]
# print("Available columns:", df.columns.tolist())

# Clean column names: remove whitespace and make all uppercase
df.columns = [str(col).strip().upper() for col in df.columns]

# Print column names to verify they are as expected
# print("COLUMNS FOUND IN EXCEL FILE:")
# for col in df.columns:
#     print(repr(col))


# Connect to SQLite DB (ensure 'company_data.db' exists and has the required tables)
conn = sqlite3.connect("company_data.db")
cursor = conn.cursor()

# Insert into Companies
# company_data = []
# for _, row in df.iterrows():
#     company_data.append((
#         row['TICKER'],
#         row['NAME'],
#         row['ADR'],
#         row['END'],
#         row['Index?'] == 'Y'
#     ))

# print("Inserting company data...", company_data)

# cursor.executemany("""
#     INSERT INTO Companies (ticker, name, adr_type, fiscal_year_end, index_member)
#     VALUES (?, ?, ?, ?, ?)
# """, company_data)
# conn.commit()

# # Map tickers to company_id
# cursor.execute("SELECT company_id, ticker FROM Companies")
# company_map = {ticker: cid for cid, ticker in cursor.fetchall()}

# # Insert into AnalystCoverage
# coverage_data = []
# for _, row in df.iterrows():
#     ticker = row['TICKER']
#     if pd.notna(row['Analysts']):
#         coverage_data.append((
#             company_map.get(ticker),
#             row['DATE'],
#             int(row['Analysts'])
#         ))

# cursor.executemany("""
#     INSERT INTO AnalystCoverage (company_id, snapshot_date, num_analysts)
#     VALUES (?, ?, ?)
# """, coverage_data)
# conn.commit()

# # Insert into SalesEstimates (for columns like 2026, 2025, etc.)
# sales_years = [col for col in df.columns if str(col).isdigit()]
# sales_data = []
# for _, row in df.iterrows():
#     ticker = row['TICKER']
#     company_id = company_map.get(ticker)
#     snapshot_date = row['DATE']
#     for year in sales_years:
#         value = row[year]
#         if pd.notna(value):
#             sales_data.append((company_id, int(year), float(value), snapshot_date))

# cursor.executemany("""
#     INSERT INTO SalesEstimates (company_id, fiscal_year, estimate_value, snapshot_date)
#     VALUES (?, ?, ?, ?)
# """, sales_data)
conn.commit()

print("Data load complete.")
conn.close()
