import pandas as pd
import sqlite3
import os

# Ensure db folder exists
os.makedirs("db", exist_ok=True)
conn = sqlite3.connect("db/ecommerce.db")

ad_sales = pd.read_csv("data/ad_sales.csv")
total_sales = pd.read_csv("data/total_sales.csv")
eligibility = pd.read_csv("data/eligibility.csv")

ad_sales.to_sql("ad_sales", conn, if_exists="replace", index=False)
total_sales.to_sql("total_sales", conn, if_exists="replace", index=False)
eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)

conn.close()
print("CSV data loaded into SQLite successfully.")

