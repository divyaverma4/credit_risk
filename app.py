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

    # Prepare summaries
    def summarize(data, id_key):
        summary = [
            (d[id_key], d.get("Age"), d.get("Income"), d.get("EmploymentStatus"), d.get("RiskCategory"))
            for d in data
        ]
        # Split by risk
        high = [d for d in summary if str(d[4]).strip().lower() == "high risk"]
        medium = [d for d in summary if str(d[4]).strip().lower() == "medium risk"]
        low = [d for d in summary if str(d[4]).strip().lower() == "low risk"]
        counts = [len(high), len(medium), len(low)]
        return summary, high, medium, low, counts

    ind_summary, ind_high, ind_medium, ind_low, ind_counts = summarize(individuals, "CustomerID")
    comp_summary, comp_high, comp_medium, comp_low, comp_counts = summarize(companies, "EntityID")

    # Example predicted credit limits
    predictions = [
        {"customer_id": 'CUST-1001', "credit_limit": 5000},
        {"customer_id": 'CUST-1002', "credit_limit": 12000},
        {"customer_id": 'ENT-5001', "credit_limit": 8000},
        {"customer_id": 'ENT-5002', "credit_limit": 10000}
    ]

    return render_template(
        "index.html",
        ind_high=ind_high, ind_medium=ind_medium, ind_low=ind_low,
        comp_high=comp_high, comp_medium=comp_medium, comp_low=comp_low,
        full_individuals=individuals,
        full_companies=companies,
        ind_counts=ind_counts,
        comp_counts=comp_counts,
        predictions=predictions  # <-- pass predictions here
    )

# -------------------- Run Flask --------------------
if __name__ == "__main__":
    app.run(debug=True)
