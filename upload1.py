import sqlite3
import pandas as pd
import os

# === CONFIGURATION ===
EXCEL_FILE = "zack1.xlsm"
SHEET_NAME = "DATA AFTER REFRESH"
DB_FILE = "zacks.db"
TABLE_NAME = "zacks_data"

# === LOAD AND PREPARE DATA ===
print(f"Loading data from {EXCEL_FILE}...")

df_raw = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=None)

# # FIX: Coerce to string before combining
# multi_header = df_raw.iloc[0].astype(str).fillna('') + ' ' + df_raw.iloc[1].astype(str).fillna('')
# headers = [col.strip().upper().replace(" ", "_").replace("__", "_") for col in multi_header]

# Combine first two rows safely as string headers
multi_header = df_raw.iloc[0].astype(str).fillna('') + ' ' + df_raw.iloc[1].astype(str).fillna('')
raw_headers = [col.strip().upper().replace(" ", "_").replace("__", "_") for col in multi_header]

# Ensure column names are unique
headers = []
seen = set()
for i, col in enumerate(raw_headers):
    col = col if col and col != "NAN" else f"COL_{i}"
    if col in seen:
        suffix = 1
        new_col = f"{col}_{suffix}"
        while new_col in seen:
            suffix += 1
            new_col = f"{col}_{suffix}"
        col = new_col
    seen.add(col)
    headers.append(col)



df = pd.DataFrame(df_raw.iloc[2:].values, columns=headers)
df = df.dropna(axis=1, how='all')  # Optional cleanup

# Optional: drop completely empty columns
df = df.dropna(axis=1, how='all')

print(f"Data loaded with {len(df)} rows and {len(df.columns)} columns.")

# === CONNECT TO SQLITE ===
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# === CREATE TABLE IF NOT EXISTS ===
def infer_sql_type(value):
    try:
        float(value)
        return "REAL"
    except:
        return "TEXT"

column_defs = []
sample_row = df.iloc[0]

for col in df.columns:
    sample_val = sample_row[col]
    sql_type = infer_sql_type(sample_val)
    col_clean = col.replace("-", "_").replace("/", "_")
    column_defs.append(f'"{col_clean}" {sql_type}')

create_stmt = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    {', '.join(column_defs)}
);
"""
cursor.execute(create_stmt)
conn.commit()
print(f"Table '{TABLE_NAME}' created or verified.")


# === INSERT DATA ===
df = df.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)

placeholders = ", ".join(["?"] * len(df.columns))
insert_sql = f"INSERT INTO {TABLE_NAME} VALUES ({placeholders})"
cursor.executemany(insert_sql, df.values.tolist())


print("Inserting data...")
cursor.executemany(insert_sql, df.values.tolist())
conn.commit()

print(f"Inserted {len(df)} rows into '{TABLE_NAME}'.")

# === DONE ===
conn.close()
print("Upload complete.")
