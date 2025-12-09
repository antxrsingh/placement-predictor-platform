import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np
import joblib

# Features used by BOTH models (classifier + salary regressor)
FEATURES = [
    "ssc_p",      # 10th percentage
    "hsc_p",      # 12th percentage
    "degree_p",   # degree percentage
    "etest_p",    # employability test percent
    "workex_bin", # binary work experience
]

def main():
    data_path = os.path.join("data", "Placement_Data_Full_Class.csv")

    df = pd.read_csv(data_path)

    # --- 1. Preprocessing target (placement) ---
    # Map status: "Placed" -> 1, "Not Placed" -> 0
    df = df.dropna(subset=["status"])
    df["placed"] = (df["status"].str.strip().str.lower() == "placed").astype(int)

    # --- 2. Convert workex ("Yes"/"No") to 0/1 ---
    df["workex_bin"] = df["workex"].str.strip().str.lower().map(
        {"yes": 1, "no": 0}
    )
    df["workex_bin"] = df["workex_bin"].fillna(0)

    # --- 3. Handle numeric columns (drop rows missing important info) ---
    numeric_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p"]
    df = df.dropna(subset=numeric_cols)

    # --- 4. Train classification model (placement) ---
    X = df[FEATURES]
    y = df["placed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Classification model accuracy on test set: {acc:.2f}")

    # Save classifier
    joblib.dump(clf, "placement_model.pkl")
    print("💾 placement_model.pkl saved successfully.")

    # --- 5. Train salary regression model (only on placed students with salary) ---
    df_salary = df[(df["placed"] == 1) & (df["salary"].notna())]

    X_sal = df_salary[FEATURES]
    y_sal = df_salary["salary"]  # salary is in INR per annum

    X_sal_train, X_sal_test, y_sal_train, y_sal_test = train_test_split(
        X_sal, y_sal, test_size=0.2, random_state=42
    )

    reg = LinearRegression()
    reg.fit(X_sal_train, y_sal_train)

    y_sal_pred = reg.predict(X_sal_test)
    rmse = np.sqrt(mean_squared_error(y_sal_test, y_sal_pred))
    print(f"✅ Salary regression RMSE on test set: {rmse:.2f}")

    # Save salary model
    joblib.dump(reg, "salary_model.pkl")
    print("💾 salary_model.pkl saved successfully.")

    # --- 6. Also save FEATURES list for reference (optional good practice) ---
    joblib.dump(FEATURES, "model_features.pkl")
    print("💾 model_features.pkl saved successfully.")

if __name__ == "__main__":
    main()
