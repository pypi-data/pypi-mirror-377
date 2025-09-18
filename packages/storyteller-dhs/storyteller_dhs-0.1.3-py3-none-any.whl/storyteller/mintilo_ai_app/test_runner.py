import os

from storyteller.mintilo_ai_app.processor import build_dataset
from storyteller.mintilo_ai_app.exporter import export_csv, export_metadata


# == Config
DB_PATH = r"D:\data\DHS\FullDHSDatabase\ET_2005\database\ET_2005_DHS_07082021_1930_58107.db"


if __name__ == "__main__":
    print("INFO - Running Mintilo AI App in debug mode...")
    df, queries = build_dataset(DB_PATH)

    print(f"INFO - Dataset shape: {df.shape}")
    print(df.head())

    csv_path = export_csv(df, DB_PATH)
    metadata_path = export_metadata(DB_PATH, queries)
    print(f"INFO - CSV exported: {csv_path}")
    print(f"INFO - Metadata exported: {metadata_path}")
