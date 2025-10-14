from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
DB_FILE = "card_risk.db"

# -------------------- SQLite Helpers --------------------
def fetch_table(table_name, columns):
    """Fetch specified columns from a table and return a list of dicts."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # dictionary-like access
    cursor = conn.cursor()

    # Build SELECT query dynamically
    col_str = ", ".join(columns)
    query = f"SELECT {col_str} FROM {table_name}"
    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_individuals():
    columns = ["CustomerID", "Age", "Income", "EmploymentStatus", "RiskCategory"]
    return fetch_table("IndividualCardholders", columns)

def get_companies():
    columns = ["EntityID", "Age", "Income", "EmploymentStatus", "RiskCategory"]
    return fetch_table("CompanyCardholders", columns)

# -------------------- Flask Route --------------------
@app.route("/")
def index():
    individuals = get_individuals()
    companies = get_companies()

    # --- Prepare summaries ---
    ind_summary = [
        (i.get("CustomerID"), i.get("Age"), i.get("Income"), i.get("EmploymentStatus"), i.get("RiskCategory"))
        for i in individuals
    ]
    comp_summary = [
        (c.get("EntityID"), c.get("Age"), c.get("Income"), c.get("EmploymentStatus"), c.get("RiskCategory"))
        for c in companies
    ]

    # --- Split by risk category dynamically ---
    def split_by_risk(data):
        high = [d for d in data if str(d[4]).strip().lower() == "high"]
        medium = [d for d in data if str(d[4]).strip().lower() == "medium"]
        low = [d for d in data if str(d[4]).strip().lower() == "low"]
        return high, medium, low

    ind_high, ind_medium, ind_low = split_by_risk(ind_summary)
    comp_high, comp_medium, comp_low = split_by_risk(comp_summary)

    return render_template(
        "index.html",
        ind_high=ind_high, ind_medium=ind_medium, ind_low=ind_low,
        comp_high=comp_high, comp_medium=comp_medium, comp_low=comp_low,
        full_individuals=individuals,
        full_companies=companies
    )

# -------------------- Run Flask --------------------
if __name__ == "__main__":
    app.run(debug=True)
