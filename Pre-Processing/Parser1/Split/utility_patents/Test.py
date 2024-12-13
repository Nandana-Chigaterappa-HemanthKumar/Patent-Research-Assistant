# import pandas as pd
# from tabulate import tabulate  # For table display

# def check_na_distribution(df):
#     """
#     Check for 'N/A' values in each column and display results as a table.
#     """
#     print("\nChecking 'N/A' distribution across columns...")

#     # Create a DataFrame to store results
#     results = []

#     for column in df.columns:
#         na_count = df[column].apply(lambda x: str(x).strip() == "N/A").sum()
#         na_percentage = (na_count / len(df)) * 100
#         results.append({"Column": column, "N/A Count": na_count, "N/A Percentage": f"{na_percentage:.2f}%"})

#     # Convert results to DataFrame
#     results_df = pd.DataFrame(results)

#     # Print the results as a table
#     print(tabulate(results_df, headers="keys", tablefmt="pretty"))

# def main():
#     # Path to the Parquet file
#     parquet_file_path = "/Users/nithinkeshav/Downloads/utility_patents (2).parquet"

#     try:
#         # Load the Parquet file into a Pandas DataFrame
#         df = pd.read_parquet(parquet_file_path)
#         print("Parquet File Loaded Successfully!")
#         print("Number of Records:", len(df))
#         print("Columns:", df.columns.tolist())

#         # Check 'N/A' distribution
#         check_na_distribution(df)

#     except Exception as e:
#         print(f"Error reading the Parquet file: {e}")

# if __name__ == "__main__":
#     main()

import pandas as pd

# Path to the locally downloaded Parquet file
parquet_file_path = ""

# Function to check for null values and 'N/A' in each column
def validate_parquet(file_path):
    try:
        # Load the Parquet file into a Pandas DataFrame
        df = pd.read_parquet(file_path)

        # Display basic information
        print("Parquet File Loaded Successfully!")
        print("Number of Records:", len(df))
        print("Columns:", df.columns.tolist())

        # Check for null values in each column
        null_counts = df.isnull().sum()
        print("\nNull Value Counts per Column:")
        print(null_counts)

        # Check for 'N/A' values in each column
        na_counts = df.apply(lambda col: col.astype(str).str.upper().eq("N/A").sum())
        print("\n'N/A' Value Counts per Column:")
        print(na_counts)

        # Display a summary of missing values
        print("\nSummary of Missing Data:")
        summary = pd.DataFrame({
            "Null Counts": null_counts,
            "'N/A' Counts": na_counts,
            "Total Missing": null_counts + na_counts,
            "% Missing": ((null_counts + na_counts) / len(df)) * 100
        })
        print(summary)

        # Display the first few rows for review
        print("\nSample Data (First 5 Rows):")
        print(df.head())

        # Optional: Check for columns with significant missing data
        significant_missing = summary[summary["% Missing"] > 20]
        if not significant_missing.empty:
            print("\nColumns with >20% Missing Data:")
            print(significant_missing)
        else:
            print("\nNo columns have more than 20% missing data.")

    except Exception as e:
        print(f"Error validating the Parquet file: {e}")

# Call the function to validate the Parquet file
validate_parquet(parquet_file_path)
