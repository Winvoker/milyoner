import json
import pandas as pd
import csv
import os
import re
from glob import glob


def process_raw_output_file(file_path):
    """Process a single debug raw output file"""
    print(f"Processing {os.path.basename(file_path)}")

    # Extract video ID from filename
    video_id = re.search(r"debug_raw_output_([^.]+)\.txt", file_path).group(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            return []

        # Clean JSON content
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"\s*```", "", content)
        start_idx = content.find("[")
        end_idx = content.rfind("]") + 1
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx:end_idx]

        # Parse JSON
        data = json.loads(content)
        if isinstance(data, dict):
            data = [data]

        rows = []
        for entry in data:
            contestant_name = entry.get("contestant", "").strip()

            # Skip host
            if "oktay" in contestant_name.lower():
                continue

            # Handle nested format
            if "questions_answered" in entry:
                for q in entry.get("questions_answered", []):
                    rows.append(
                        {
                            "video_id": video_id,
                            "contestant": contestant_name,
                            "question": q.get("question", ""),
                            "options": q.get("options", []),
                            "correct_answer": q.get("correct_answer", ""),
                            "contestant_answer": q.get("contestant_answer", ""),
                            "category": q.get("category", "Genel Kültür"),
                            "level": q.get("level", 0),
                            "amount": q.get("amount", 0),
                            "joker_used": q.get("joker_used", "yok"),
                            "is_correct": q.get("is_correct", False),
                            "eliminated": q.get("eliminated", False),
                        }
                    )
            else:
                # Handle flat format
                if entry.get("contestant") and entry.get("question"):
                    entry["video_id"] = video_id
                    rows.append(entry)

        print(f"Extracted {len(rows)} entries")
        return rows

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def clean_dataframe(df):
    """Clean the dataframe"""
    print("Cleaning data...")

    # Remove duplicates and clean
    df = df.drop_duplicates(subset=["video_id", "contestant", "question"], keep="first")
    df["contestant"] = df["contestant"].str.strip().str.title()

    # # Fill missing values and convert types
    # defaults = {
    #     "category": "Genel Kültür",
    #     "level": 0,
    #     "joker_used": "yok",
    #     "is_correct": False,
    #     "eliminated": False,
    # }
    # for col, default in defaults.items():
    #     df[col] = df[col].fillna(default)
    # dropna
    df = df.dropna(subset=["video_id", "contestant", "question"])

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["level"] = pd.to_numeric(df["level"], errors="coerce").fillna(0)
    df["is_correct"] = df["is_correct"].astype(bool)
    df["eliminated"] = df["eliminated"].astype(bool)

    print(f"Cleaned data: {len(df)} entries")
    return df


def main():
    """Main function to process all debug raw output files"""
    raw_files = glob("raw_output/debug_raw_output_*.txt")

    if not raw_files:
        print("No debug raw output files found!")
        return

    print(f"Found {len(raw_files)} debug raw output files")
    os.makedirs("csv", exist_ok=True)

    # Process all files
    all_rows = []
    for file_path in raw_files:
        all_rows.extend(process_raw_output_file(file_path))

    if not all_rows:
        print("No data extracted!")
        return

    # Create and clean DataFrame
    df = pd.DataFrame(all_rows)
    print(f"\nTotal entries: {len(df)}")

    # Ensure all columns exist
    expected_columns = [
        "video_id",
        "contestant",
        "question",
        "options",
        "correct_answer",
        "contestant_answer",
        "category",
        "level",
        "amount",
        "joker_used",
        "is_correct",
        "eliminated",
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    df = clean_dataframe(df)

    # Save main files
    df.to_csv(
        "csv/milyoner_data_from_raw.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
    )
    print("Main CSV saved: csv/milyoner_data_from_raw.csv")

    # Generate and save stats
    stats = (
        df.groupby(["video_id", "contestant"], as_index=False)
        .agg(
            {
                "question": "count",
                "is_correct": "sum",
                "amount": "max",
                "eliminated": "max",
                "level": "max",
            }
        )
        .rename(
            columns={
                "question": "total_questions",
                "is_correct": "correct_answers",
                "amount": "max_amount",
                "level": "max_level",
            }
        )
    )

    stats.to_csv(
        "csv/milyoner_contestant_stats_from_raw.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    print("Stats CSV saved: csv/milyoner_contestant_stats_from_raw.csv")

    # Save individual video files
    for video_id in df["video_id"].unique():
        video_df = df[df["video_id"] == video_id]
        video_df.to_csv(
            f"csv/{video_id}_from_raw.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
        )

        video_stats = (
            video_df.groupby(["video_id", "contestant"], as_index=False)
            .agg(
                {
                    "question": "count",
                    "is_correct": "sum",
                    "amount": "max",
                    "eliminated": "max",
                    "level": "max",
                }
            )
            .rename(
                columns={
                    "question": "total_questions",
                    "is_correct": "correct_answers",
                    "amount": "max_amount",
                    "level": "max_level",
                }
            )
        )

        video_stats.to_csv(
            f"csv/{video_id}_stats_from_raw.csv",
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
        )

    print(f"Individual video files saved for {df['video_id'].nunique()} videos")

    # Create final combined CSV
    create_final_csv(df)


def create_final_csv(raw_df):
    """Create final combined CSV file"""
    print("\nCreating final combined CSV...")

    final_df = raw_df.copy()

    # Combine with existing data if available
    existing_csv = "csv/milyoner_data_all.csv"
    if os.path.exists(existing_csv):
        print(f"Found existing CSV: {existing_csv}")
        try:
            existing_df = pd.read_csv(existing_csv)
            final_df = pd.concat([existing_df, raw_df], ignore_index=True)
            final_df = final_df.drop_duplicates(
                subset=["video_id", "contestant", "question"], keep="first"
            )
            print(f"Combined data: {len(final_df)} entries after deduplication")
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    # Save final CSV
    final_df.to_csv(
        "csv/milyoner_data_final.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
    )
    print(f"Final CSV saved: csv/milyoner_data_final.csv ({len(final_df)} entries)")

    # Show summary
    print(f"\n=== SUMMARY ===")
    print(f"Total questions: {len(final_df)}")
    print(f"Total contestants: {final_df['contestant'].nunique()}")
    print(f"Total videos: {final_df['video_id'].nunique()}")
    print(
        f"Avg questions per contestant: {len(final_df) / final_df['contestant'].nunique():.1f}"
    )

    # Show top performers
    stats = (
        final_df.groupby(["video_id", "contestant"], as_index=False)
        .agg({"question": "count", "is_correct": "sum", "amount": "max"})
        .rename(
            columns={
                "question": "total_questions",
                "is_correct": "correct_answers",
                "amount": "max_amount",
            }
        )
    )

    stats["max_amount"] = pd.to_numeric(stats["max_amount"], errors="coerce").fillna(0)
    top_performers = stats.nlargest(5, "max_amount")[
        ["contestant", "max_amount", "correct_answers", "total_questions"]
    ]

    print(f"\nTop 5 performers:")
    print(top_performers.to_string(index=False))


if __name__ == "__main__":
    main()
