import sqlite3

# Create (or connect to) a database file
conn = sqlite3.connect("card_risk.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS IndividualCardholders")
cur.execute("DROP TABLE IF EXISTS CompanyCardholders")


# Create table for individual cardholders
cur.execute("""
CREATE TABLE IF NOT EXISTS IndividualCardholders (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Age INT,
    Education TEXT,
    Location TEXT,
    MaritalStatus TEXT,
    Citizenship TEXT,
    Name TEXT,
    AccountNumber INT,
    CustomerID TEXT,
    Income INT,
    EmploymentStatus TEXT,
    Savings INT,
    Bankruptcies INT,
    RepaymentHistory TEXT,
    OpenCreditLines INT,
    CardLimit INT,
    CashAdvances INT,
    ProductType TEXT
);
""")

# Create table for company cardholders
cur.execute("""
CREATE TABLE IF NOT EXISTS CompanyCardholders (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Location TEXT,
    Age INT,
    EntityID TEXT,
    Income INT,
    EmploymentStatus TEXT,
    Savings INT,
    Bankruptcies INT,
    RepaymentHistory TEXT,
    OpenCreditLines INT,
    CardLimit INT,
    CashAdvances INT,
    ProductType TEXT
);
""")

conn.commit()
conn.close()

