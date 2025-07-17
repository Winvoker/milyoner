#!/usr/bin/env python3
"""
Script to anonymize contestant names in the milyoner dataset
"""

import pandas as pd
import hashlib
from collections import defaultdict


def anonymize_contestants(input_file, output_file):
    """
    Anonymize contestant names by replacing them with anonymous IDs
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Create a mapping of contestant names to anonymous IDs
    contestant_mapping = {}
    contestant_counter = 1

    # Generate anonymous IDs for each unique contestant
    for contestant in df["contestant"].unique():
        if pd.notna(contestant):  # Check if not NaN
            contestant_mapping[contestant] = f"Contestant_{contestant_counter:03d}"
            contestant_counter += 1

    # Replace contestant names with anonymous IDs
    df["contestant"] = df["contestant"].map(contestant_mapping)

    # Save the anonymized dataset
    df.to_csv(output_file, index=False)

    print(f"✅ Anonymized dataset saved to: {output_file}")
    print(f"📊 Total unique contestants anonymized: {len(contestant_mapping)}")
    print(f"📈 Total records processed: {len(df)}")

    # Print some statistics
    print("\n📋 Dataset Statistics:")
    print(f"   - Videos: {df['video_id'].nunique()}")
    print(f"   - Questions: {len(df)}")
    print(f"   - Categories: {df['category'].nunique()}")
    print(f"   - Difficulty levels: {df['level'].nunique()}")

    # Show contestant mapping (first 10 for verification)
    print("\n🔀 Sample contestant mapping:")
    for i, (original, anonymous) in enumerate(list(contestant_mapping.items())[:10]):
        print(f"   {original} → {anonymous}")
    if len(contestant_mapping) > 10:
        print(f"   ... and {len(contestant_mapping) - 10} more")

    return df, contestant_mapping


if __name__ == "__main__":
    input_file = "csv/milyoner_data_final.csv"
    output_file = "milyoner_data.csv"

    anonymized_df, mapping = anonymize_contestants(input_file, output_file)
