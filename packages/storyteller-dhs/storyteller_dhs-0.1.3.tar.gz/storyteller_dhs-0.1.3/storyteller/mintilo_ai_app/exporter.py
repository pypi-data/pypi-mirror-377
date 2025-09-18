import os
import json

import pandas as pd
from storyteller.mintilo_ai_app.mapping_sheet import MAPPING_CHILD, MAPPING_HOUSEHOLD, MAPPING_MOTHER


def serialize_mapping(mapping):
    """Convert Python types in mapping to JSON-safe strings."""
    serialized = {}
    for key, val in mapping.items():
        serialized[key] = val.copy()
        if "dtype" in serialized[key]:
            serialized[key]["dtype"] = serialized[key]["dtype"].__name__  # int -> "int"
    return serialized


def export_csv(df, db_path):
    """Export dataset as CSV using consistent naming convention."""
    db_filename = os.path.basename(db_path).replace(".db", "")
    output_dir = os.path.dirname(db_path)

    csv_filename = f"mintiloai - {db_filename} - data.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    df.to_csv(csv_path, index=False, encoding="utf-8")
    return csv_path


def export_metadata(db_path, queries):
    """Export mapping and queries as JSON for reproducibility."""
    db_filename = os.path.basename(db_path).replace(".db", "")
    output_dir = os.path.dirname(db_path)

    metadata = {
        "database": os.path.basename(db_path),
        "queries": queries,
        "mapping": {
            "child": serialize_mapping(MAPPING_CHILD),
            "household": serialize_mapping(MAPPING_HOUSEHOLD),
            "mother": serialize_mapping(MAPPING_MOTHER),
        }
    }

    metadata_filename = f"mintiloai - {db_filename} - metadata.json"
    metadata_path = os.path.join(output_dir, metadata_filename)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    return metadata_path
