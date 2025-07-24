import pandas as pd
import sqlite3
import os

os.makedirs("db", exist_ok=True)
conn = sqlite3.connect("db/ecommerce.db")

data_files = {
    "ad_sales": "data/ad_sales.csv",
    "total_sales": "data/total_sales.csv",
    "eligibility": "data/eligibility.csv"
}

for table, path in data_files.items():
    df = pd.read_csv(path)
    df.to_sql(table, conn, if_exists="replace", index=False)

conn.close()
print("✅ Data imported successfully.")
