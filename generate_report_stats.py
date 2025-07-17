import pandas as pd
import json
from collections import Counter

# Load data
df = pd.read_csv("csv/milyoner_data_final.csv")

# Basic stats
print("=== BASIC STATISTICS ===")
print(f"Total questions: {len(df)}")
print(f'Total contestants: {df["contestant"].nunique()}')
print(f'Total videos: {df["video_id"].nunique()}')
print(f'Overall accuracy: {(df["is_correct"].sum() / len(df)) * 100:.2f}%')
print(f'Total eliminated: {df["eliminated"].sum()}')

# Contestant final levels
contestant_final_levels = df.groupby("contestant")["level"].max()
print(f"Average final level: {contestant_final_levels.mean():.2f}")

# Category stats
print("\n=== CATEGORY ANALYSIS ===")
category_stats = (
    df.groupby("category")
    .agg({"is_correct": ["count", "sum", "mean"], "level": "mean"})
    .round(2)
)
category_stats.columns = [
    "Total_Questions",
    "Correct_Answers",
    "Accuracy_Rate",
    "Avg_Level",
]
print(category_stats.sort_values("Total_Questions", ascending=False))

# Level stats
print("\n=== LEVEL ANALYSIS ===")
level_stats = (
    df.groupby("level")
    .agg({"is_correct": ["count", "sum", "mean"], "eliminated": "sum"})
    .round(2)
)
level_stats.columns = [
    "Total_Questions",
    "Correct_Answers",
    "Accuracy_Rate",
    "Eliminations",
]
print(level_stats)

# Answer choice analysis
print("\n=== ANSWER CHOICE ANALYSIS ===")
correct_dist = df["correct_answer"].value_counts()
chosen_dist = df["contestant_answer"].value_counts()
print("Correct answer distribution:")
print(correct_dist)
print("\nContestant answer distribution:")
print(chosen_dist)

# Performance clusters
print("\n=== PERFORMANCE CLUSTERS ===")
final_level_dist = contestant_final_levels.value_counts().sort_index()
print("Final level distribution:")
print(final_level_dist)

high_performers = (contestant_final_levels >= 10).sum()
mid_performers = ((contestant_final_levels >= 5) & (contestant_final_levels < 10)).sum()
early_eliminators = (contestant_final_levels < 5).sum()

print(f"\nHigh performers (Level 10+): {high_performers}")
print(f"Mid performers (Level 5-9): {mid_performers}")
print(f"Early eliminators (<Level 5): {early_eliminators}")

# Before/After Level 7 analysis
print("\n=== BEFORE/AFTER LEVEL 7 ANALYSIS ===")
before_7 = df[df["level"] < 7]
after_7 = df[df["level"] >= 7]

print(
    f'Before Level 7: {len(before_7)} questions, {before_7["is_correct"].mean()*100:.1f}% accuracy'
)
print(
    f'Level 7+: {len(after_7)} questions, {after_7["is_correct"].mean()*100:.1f}% accuracy'
)

# Answer choice bias before/after level 7
print("\nAnswer choice bias before Level 7:")
before_7_choices = before_7["contestant_answer"].value_counts()
print(before_7_choices)

print("\nAnswer choice bias after Level 7:")
after_7_choices = after_7["contestant_answer"].value_counts()
print(after_7_choices)

# Top categories by question count
print("\n=== TOP CATEGORIES ===")
top_categories = df["category"].value_counts().head(10)
print(top_categories)
