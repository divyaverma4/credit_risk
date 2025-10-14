import sqlite3
import pandas as pd

# CONFIG
db_file = "card_risk.db"
table_name = "CompanyCardholders"

# --- Clear old data ---
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute(f"DELETE FROM {table_name};")  # clears all rows
conn.commit()
conn.close()
print(f"Cleared existing data from '{table_name}'")

# --- Load CSVs ---
demographics = pd.read_csv("Comp_Demographics.csv")
demographics.columns = [
    "Location", "Age", "EntityID"
]

income = pd.read_csv("Comp_Income_Occ.csv")
income.columns = [
    "Income", "EmploymentStatus", "Savings", "Bankruptcies", "EntityID"
]

product = pd.read_csv("Comp_Product.csv")
product.columns = [
    "RepaymentHistory", "OpenCreditLines", "CardLimit", "CashAdvances", "ProductType", "EntityID"
]

# --- Merge all on EntityID ---
merged_df = demographics.merge(income, on="EntityID", how="left").merge(product, on="EntityID", how="left")

# --- Insert merged data into SQLite ---
conn = sqlite3.connect(db_file)
merged_df.to_sql(table_name, conn, if_exists='append', index=False)
conn.commit()
conn.close()

print(f"Imported merged company data ({len(merged_df)} rows) into '{table_name}' in {db_file}")
