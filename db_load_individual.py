import sqlite3
import pandas as pd

# config
db_file = "card_risk.db"
table_name = "IndividualCardholders"

# clear old data
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute(f"DELETE FROM {table_name};")
conn.commit()
conn.close()
print(f"Cleared existing data from '{table_name}'")

# --- Load and merge CSVs ---
demographics = pd.read_csv("Indiv_Demographics.csv")
demographics.columns = [
    "Age", "Education", "Location", "MaritalStatus", "Citizenship",
    "Name", "AccountNumber", "CustomerID"
]

income = pd.read_csv("Indiv_Income_Occ.csv")
income.columns = [
    "Income", "EmploymentStatus", "Savings", "Bankruptcies", "CustomerID"
]

product = pd.read_csv("Indiv_Product.csv")
product.columns = [
    "RepaymentHistory", "OpenCreditLines", "CardLimit", "CashAdvances", "ProductType", "CustomerID"
]

# merge on CustomerID
merged_df = demographics.merge(income, on="CustomerID", how="left").merge(product, on="CustomerID", how="left")

# --- Insert into SQLite ---
conn = sqlite3.connect(db_file)
merged_df.to_sql(table_name, conn, if_exists='append', index=False)
conn.commit()
conn.close()

print(f"Imported merged data ({len(merged_df)} rows) into '{table_name}' in {db_file}")
