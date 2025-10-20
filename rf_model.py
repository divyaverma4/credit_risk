import sqlite3
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error
from crr_model import compute_crr, risk_category


# ---------- 1. LOAD ----------
def load_data(db_file, table_name):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    conn.close()
    return df


# ---------- 2. PREPROCESS ----------
def preprocess_data(df):
    df = df.copy()

    # Compute rule-based CRR if missing
    if "CRR_Score" not in df.columns:
        df["CRR_Score"] = df.apply(compute_crr, axis=1)
        df["RiskCategory"] = df["CRR_Score"].apply(risk_category)

    # Fill missing values
    num_cols = df.select_dtypes(include="number").columns
    cat_cols = df.select_dtypes(exclude="number").columns

    num_imputer = SimpleImputer(strategy="median")
    cat_imputer = SimpleImputer(strategy="most_frequent")

    df[num_cols] = num_imputer.fit_transform(df[num_cols])
    df[cat_cols] = cat_imputer.fit_transform(df[cat_cols])

    # One-hot encode categorical
    df = pd.get_dummies(df, drop_first=True)

    return df


# ---------- 3. TRAIN OR LOAD RANDOM FOREST ----------
def get_rf_model(df, model_path="rf_crr_model.pkl", retrain=False):
    if os.path.exists(model_path) and not retrain:
        print(f"Loading existing model: {model_path}")
        model, feature_names = joblib.load(model_path)
        return model, feature_names

    print("Training new Random Forest model...")
    X = df.drop(columns=["CRR_Score", "RiskCategory"], errors="ignore")
    y = df["CRR_Score"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=250, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"R² Score: {r2_score(y_test, y_pred):.3f}")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.3f}")

    # Save model *and* feature names used in training
    joblib.dump((model, list(X.columns)), model_path)
    print(f"Model and feature list saved to {model_path}")
    return model, list(X.columns)


# ---------- 4. HYBRID PREDICTION ----------
def hybrid_predict(df_original, model, feature_names, alpha=0.6):
    """
    alpha = weight for ML model (0.0–1.0)
    (1 - alpha) = weight for rule-based CRR
    """
    df_features = preprocess_data(df_original)

    # Align columns to match model training
    # Find any missing columns
    missing_cols = [col for col in feature_names if col not in df_features.columns]

    # Add them all at once as a DataFrame of zeros
    if missing_cols:
        zero_df = pd.DataFrame(0, index=df_features.index, columns=missing_cols)
        df_features = pd.concat([df_features, zero_df], axis=1)

    # Reorder columns to match training
    df_features = df_features[feature_names].copy()

    # ML predictions
    preds_rf = model.predict(df_features)

    # Ensure rule-based CRR is available
    if "CRR_Score" not in df_original.columns:
        df_original["CRR_Score"] = df_original.apply(compute_crr, axis=1)

    # Store ML predictions separately
    df_original["ML_CRR_Pred"] = preds_rf

    # Combine both scores
    df_original["Hybrid_CRR"] = (alpha * df_original["ML_CRR_Pred"]) + (
        (1 - alpha) * df_original["CRR_Score"]
    )

    # Risk category
    df_original["Hybrid_Risk"] = df_original["Hybrid_CRR"].apply(
        lambda x: "Low Risk" if x >= 75 else "Medium Risk" if x >= 50 else "High Risk"
    )

    return df_original


# ---------- 5. UPDATE DATABASE ----------
def update_table(db_file, table_name, df):
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Updated {table_name} with ML_CRR_Pred, Hybrid_CRR, and Hybrid_Risk columns.")


# ---------- 6. MAIN ----------
if __name__ == "__main__":
    db_file = "card_risk.db"

    for table in ["IndividualCardholders", "CompanyCardholders"]:
        df = load_data(db_file, table)
        df_proc = preprocess_data(df)

        model, feature_names = get_rf_model(df_proc, retrain=False)
        df_hybrid = hybrid_predict(df, model, feature_names, alpha=0.6)

        # Update DB with new columns
        update_table(db_file, table, df_hybrid)
