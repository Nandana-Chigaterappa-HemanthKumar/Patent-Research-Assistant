import pandas as pd

# Path to the Parquet file
parquet_file_path = "/Users/nithinkeshav/Downloads/PRA/utility_patents.parquet"

# Load the Parquet file into a Pandas DataFrame
try:
    df = pd.read_parquet(parquet_file_path)

    # Display basic information about the DataFrame
    print("Parquet File Loaded Successfully!")
    print("Number of Records:", len(df))
    print("Columns:", df.columns.tolist())

    # Display a sample of the data
    print("\nSample Data:")
    print(df.head())

    # Optional: Display specific columns if needed
    print("\nSample Titles and Patent Numbers:")
    print(df[["title", "patent_number"]].head())

except Exception as e:
    print(f"Error reading the Parquet file: {e}")
