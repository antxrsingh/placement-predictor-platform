import os
import pandas as pd

def main():
    # 1. Load the dataset
    data_path = os.path.join("data", "Placement_Data_Full_Class.csv")

    if not os.path.exists(data_path):
        print(f"CSV not found at: {data_path}")
        return

    df = pd.read_csv(data_path)

    print("Dataset loaded successfully!")
    print("-" * 60)

    # 2. Basic shape
    print(f"Number of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")
    print("-" * 60)

    # 3. Columns
    print("Columns:")
    print(df.columns.tolist())
    print("-" * 60)

    # 4. First few rows
    print("Head (first 5 rows):")
    print(df.head())
    print("-" * 60)

    # 5. Info about types and nulls
    print("Info:")
    print(df.info())
    print("-" * 60)

    # 6. Placement outcome distribution
    if "status" in df.columns:
        print("Value counts for status (placement outcome):")
        print(df["status"].value_counts(dropna=False))
        print("-" * 60)

    # 7. Work experience distribution
    if "workex" in df.columns:
        print("Value counts for workex (work experience):")
        print(df["workex"].value_counts(dropna=False))
        print("-" * 60)

    # 8. Salary summary
    if "salary" in df.columns:
        print("Salary summary (only for placed students):")
        print(df["salary"].describe())
        print("-" * 60)

if __name__ == "__main__":
    main()
