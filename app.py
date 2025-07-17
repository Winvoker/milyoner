from flask import Flask, render_template, jsonify
import pandas as pd
import json
from collections import Counter, defaultdict
import numpy as np

app = Flask(__name__)


# Load the data
def load_data():
    df = pd.read_csv("csv/milyoner_data_final.csv")
    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    df = load_data()

    # Convert DataFrame to JSON
    data = df.to_dict("records")
    return jsonify(data)


@app.route("/api/stats")
def get_stats():
    df = load_data()

    # Basic overview statistics
    # Calculate average final level reached by contestants (not average level of all questions)
    contestant_final_levels = df.groupby("contestant")["level"].max()

    stats = {
        "total_questions": int(len(df)),
        "total_contestants": int(df["contestant"].nunique()),
        "total_videos": int(df["video_id"].nunique()),
        "overall_accuracy": float((df["is_correct"].sum() / len(df)) * 100),
        "total_eliminated": int(df["eliminated"].sum()),
        "average_level": float(contestant_final_levels.mean()),
    }

    return jsonify(stats)


@app.route("/api/category_stats")
def get_category_stats():
    df = load_data()

    # Detailed category analysis
    category_stats = []
    for category in df["category"].unique():
        cat_data = df[df["category"] == category]

        # Level distribution for this category
        level_distribution = {}
        for level in range(1, 16):
            level_questions = cat_data[cat_data["level"] == level]
            level_distribution[f"level_{level}"] = int(len(level_questions))

        # Before level 7 vs after level 7
        before_level_7 = cat_data[cat_data["level"] < 7]
        level_7_and_after = cat_data[cat_data["level"] >= 7]

        category_stats.append(
            {
                "category": str(category),
                "total_questions": int(len(cat_data)),
                "accuracy": float((cat_data["is_correct"].sum() / len(cat_data)) * 100),
                "average_level": float(cat_data["level"].mean()),
                "before_level_7": int(len(before_level_7)),
                "level_7_and_after": int(len(level_7_and_after)),
                "before_level_7_accuracy": (
                    float(
                        (before_level_7["is_correct"].sum() / len(before_level_7)) * 100
                    )
                    if len(before_level_7) > 0
                    else 0
                ),
                "level_7_and_after_accuracy": (
                    float(
                        (level_7_and_after["is_correct"].sum() / len(level_7_and_after))
                        * 100
                    )
                    if len(level_7_and_after) > 0
                    else 0
                ),
                "level_distribution": level_distribution,
            }
        )

    return jsonify(category_stats)


@app.route("/api/level_stats")
def get_level_stats():
    df = load_data()

    # Detailed level analysis
    level_stats = []
    for level in sorted(df["level"].unique()):
        level_data = df[df["level"] == level]

        # Category distribution for this level
        category_distribution = {}
        for category in df["category"].unique():
            cat_questions = level_data[level_data["category"] == category]
            category_distribution[category] = int(len(cat_questions))

        # Elimination analysis
        eliminated_at_level = level_data[level_data["eliminated"] == True]

        level_stats.append(
            {
                "level": int(level),
                "total_questions": int(len(level_data)),
                "accuracy": float(
                    (level_data["is_correct"].sum() / len(level_data)) * 100
                ),
                "amount": float(
                    level_data["amount"].iloc[0] if len(level_data) > 0 else 0
                ),
                "eliminated_count": int(len(eliminated_at_level)),
                "elimination_rate": (
                    float((len(eliminated_at_level) / len(level_data)) * 100)
                    if len(level_data) > 0
                    else 0
                ),
                "category_distribution": category_distribution,
                "most_common_category": (
                    max(category_distribution.items(), key=lambda x: x[1])[0]
                    if category_distribution
                    else None
                ),
            }
        )

    return jsonify(level_stats)


@app.route("/api/joker_stats")
def get_joker_stats():
    df = load_data()

    # Joker usage statistics
    joker_counts = df["joker_used"].value_counts().to_dict()

    # Accuracy with and without jokers
    joker_accuracy = []
    for joker in df["joker_used"].unique():
        joker_data = df[df["joker_used"] == joker]
        joker_accuracy.append(
            {
                "joker": str(joker),
                "count": int(len(joker_data)),
                "accuracy": float(
                    (joker_data["is_correct"].sum() / len(joker_data)) * 100
                    if len(joker_data) > 0
                    else 0
                ),
            }
        )

    return jsonify(joker_accuracy)


@app.route("/api/contestant_performance")
def get_contestant_performance():
    df = load_data()

    # Contestant performance
    contestant_stats = []
    for contestant in df["contestant"].unique():
        contestant_data = df[df["contestant"] == contestant]
        max_level = contestant_data["level"].max()

        # Calculate final winnings (highest level with correct answer)
        correct_answers = contestant_data[contestant_data["is_correct"] == True]
        if len(correct_answers) > 0:
            max_correct_level = correct_answers["level"].max()
            total_winnings = correct_answers[
                correct_answers["level"] == max_correct_level
            ]["amount"].iloc[0]
        else:
            total_winnings = 0

        contestant_stats.append(
            {
                "contestant": str(contestant),
                "total_questions": int(len(contestant_data)),
                "correct_answers": int(contestant_data["is_correct"].sum()),
                "accuracy": float(
                    (contestant_data["is_correct"].sum() / len(contestant_data)) * 100
                ),
                "max_level": int(max_level),
                "total_winnings": float(total_winnings),
                "eliminated": bool(contestant_data["eliminated"].any()),
            }
        )

    # Sort by total winnings
    contestant_stats.sort(key=lambda x: x["total_winnings"], reverse=True)

    return jsonify(contestant_stats)


@app.route("/api/answer_choice_stats")
def get_answer_choice_stats():
    df = load_data()

    # Answer choice distribution analysis
    correct_answer_dist = df["correct_answer"].value_counts().to_dict()
    contestant_answer_dist = df["contestant_answer"].value_counts().to_dict()

    # Accuracy by answer choice
    choice_accuracy = {}
    for choice in ["A", "B", "C", "D"]:
        choice_data = df[df["correct_answer"] == choice]
        if len(choice_data) > 0:
            choice_accuracy[choice] = {
                "total_questions": int(len(choice_data)),
                "accuracy": float(
                    (choice_data["is_correct"].sum() / len(choice_data)) * 100
                ),
                "times_correct": int(choice_data["is_correct"].sum()),
                "times_chosen": int(len(df[df["contestant_answer"] == choice])),
            }

    # Most selected vs most correct
    most_selected = (
        max(contestant_answer_dist.items(), key=lambda x: x[1])
        if contestant_answer_dist
        else ("", 0)
    )
    most_correct = (
        max(correct_answer_dist.items(), key=lambda x: x[1])
        if correct_answer_dist
        else ("", 0)
    )

    return jsonify(
        {
            "correct_answer_distribution": {
                k: int(v) for k, v in correct_answer_dist.items()
            },
            "contestant_answer_distribution": {
                k: int(v) for k, v in contestant_answer_dist.items()
            },
            "choice_accuracy": choice_accuracy,
            "most_selected_choice": {
                "choice": most_selected[0],
                "count": int(most_selected[1]),
            },
            "most_correct_choice": {
                "choice": most_correct[0],
                "count": int(most_correct[1]),
            },
            "bias_analysis": {
                "a_bias": float((contestant_answer_dist.get("A", 0) / len(df)) * 100),
                "b_bias": float((contestant_answer_dist.get("B", 0) / len(df)) * 100),
                "c_bias": float((contestant_answer_dist.get("C", 0) / len(df)) * 100),
                "d_bias": float((contestant_answer_dist.get("D", 0) / len(df)) * 100),
            },
        }
    )


@app.route("/api/elimination_analysis")
def get_elimination_analysis():
    df = load_data()

    # Elimination patterns
    eliminated_df = df[df["eliminated"] == True]

    # By level
    elimination_by_level = {}
    # Use actual levels from the data instead of hardcoded range
    for level in sorted(df["level"].unique()):
        level_eliminations = eliminated_df[eliminated_df["level"] == level]
        elimination_by_level[f"level_{level}"] = int(len(level_eliminations))

    # By category
    elimination_by_category = {}
    for category in df["category"].unique():
        cat_eliminations = eliminated_df[eliminated_df["category"] == category]
        elimination_by_category[category] = int(len(cat_eliminations))

    # Critical levels (most eliminations)
    level_elimination_counts = [
        (level, count) for level, count in elimination_by_level.items()
    ]
    level_elimination_counts.sort(key=lambda x: x[1], reverse=True)

    return jsonify(
        {
            "total_eliminations": int(len(eliminated_df)),
            "elimination_by_level": elimination_by_level,
            "elimination_by_category": elimination_by_category,
            "most_dangerous_levels": level_elimination_counts[:5],
            "most_dangerous_category": (
                max(elimination_by_category.items(), key=lambda x: x[1])
                if elimination_by_category
                else ("", 0)
            ),
            "safe_passage_rate": {
                "before_level_5": (
                    float(
                        (
                            (
                                len(df[df["level"] < 5])
                                - len(eliminated_df[eliminated_df["level"] < 5])
                            )
                            / len(df[df["level"] < 5])
                        )
                        * 100
                    )
                    if len(df[df["level"] < 5]) > 0
                    else 0
                ),
                "level_5_to_10": (
                    float(
                        (
                            (
                                len(df[(df["level"] >= 5) & (df["level"] < 10)])
                                - len(
                                    eliminated_df[
                                        (eliminated_df["level"] >= 5)
                                        & (eliminated_df["level"] < 10)
                                    ]
                                )
                            )
                            / len(df[(df["level"] >= 5) & (df["level"] < 10)])
                        )
                        * 100
                    )
                    if len(df[(df["level"] >= 5) & (df["level"] < 10)]) > 0
                    else 0
                ),
                "level_10_and_above": (
                    float(
                        (
                            (
                                len(df[df["level"] >= 10])
                                - len(eliminated_df[eliminated_df["level"] >= 10])
                            )
                            / len(df[df["level"] >= 10])
                        )
                        * 100
                    )
                    if len(df[df["level"] >= 10]) > 0
                    else 0
                ),
            },
        }
    )


@app.route("/api/topic_preparation_guide")
def get_topic_preparation_guide():
    df = load_data()

    # Preparation recommendations
    preparation_guide = {}

    for category in df["category"].unique():
        cat_data = df[df["category"] == category]

        # Frequency by level ranges
        early_levels = cat_data[cat_data["level"] <= 5]
        mid_levels = cat_data[(cat_data["level"] > 5) & (cat_data["level"] <= 10)]
        late_levels = cat_data[cat_data["level"] > 10]

        preparation_guide[category] = {
            "total_questions": int(len(cat_data)),
            "difficulty_assessment": (
                "Easy"
                if cat_data["is_correct"].mean() > 0.7
                else "Medium" if cat_data["is_correct"].mean() > 0.5 else "Hard"
            ),
            "accuracy_rate": float(cat_data["is_correct"].mean() * 100),
            "early_levels_count": int(len(early_levels)),
            "mid_levels_count": int(len(mid_levels)),
            "late_levels_count": int(len(late_levels)),
            "priority_score": float(
                len(cat_data) * (1 - cat_data["is_correct"].mean())
            ),  # High frequency + low accuracy = high priority
            "elimination_risk": int(len(cat_data[cat_data["eliminated"] == True])),
            "common_levels": [
                int(level) for level in cat_data["level"].mode().tolist()[:3]
            ],
            "preparation_recommendation": (
                "High Priority"
                if len(cat_data) > 20 and cat_data["is_correct"].mean() < 0.6
                else "Medium Priority" if len(cat_data) > 10 else "Low Priority"
            ),
        }

    # Sort by priority score
    sorted_categories = sorted(
        preparation_guide.items(), key=lambda x: x[1]["priority_score"], reverse=True
    )

    return jsonify(
        {
            "categories": preparation_guide,
            "priority_order": [cat[0] for cat in sorted_categories],
            "study_recommendations": {
                "focus_categories": [cat[0] for cat in sorted_categories[:3]],
                "review_categories": [cat[0] for cat in sorted_categories[3:6]],
                "maintenance_categories": [cat[0] for cat in sorted_categories[6:]],
            },
        }
    )


@app.route("/api/detailed_answer_analysis")
def get_detailed_answer_analysis():
    df = load_data()

    # Comprehensive answer choice analysis
    analysis = {
        "overall_bias": {},
        "level_bias": {},
        "category_bias": {},
        "difficulty_bias": {},
        "before_after_level_7": {},
        "elimination_pattern_bias": {},
        "correct_vs_chosen_analysis": {},
    }  # Overall bias analysis
    total_questions = len(df)
    df_with_answers = df[df["contestant_answer"].notna()]
    total_answered = len(df_with_answers)

    for choice in ["A", "B", "C", "D"]:
        correct_count = len(df[df["correct_answer"] == choice])
        chosen_count = len(
            df_with_answers[df_with_answers["contestant_answer"] == choice]
        )

        correct_percentage = float((correct_count / total_questions) * 100)
        chosen_percentage = (
            float((chosen_count / total_answered) * 100) if total_answered > 0 else 0
        )

        analysis["overall_bias"][choice] = {
            "correct_percentage": correct_percentage,
            "chosen_percentage": chosen_percentage,
            "bias_score": float(chosen_percentage - correct_percentage),
            "correct_count": int(correct_count),
            "chosen_count": int(chosen_count),
            "total_questions": int(total_questions),
            "answered_questions": int(total_answered),
        }  # Level-specific bias analysis
    for level in sorted(df["level"].unique()):
        level_data = df[df["level"] == level]

        # Filter out rows with missing contestant answers for percentage calculations
        level_data_with_answers = level_data[level_data["contestant_answer"].notna()]
        level_total = len(level_data)
        level_answered_total = len(level_data_with_answers)

        level_analysis = {}
        for choice in ["A", "B", "C", "D"]:
            correct_at_level = len(level_data[level_data["correct_answer"] == choice])
            chosen_at_level = len(
                level_data_with_answers[
                    level_data_with_answers["contestant_answer"] == choice
                ]
            )

            # Calculate percentages based on answered questions only
            correct_percentage = (
                float((correct_at_level / level_total) * 100) if level_total > 0 else 0
            )
            chosen_percentage = (
                float((chosen_at_level / level_answered_total) * 100)
                if level_answered_total > 0
                else 0
            )

            level_analysis[choice] = {
                "correct_percentage": correct_percentage,
                "chosen_percentage": chosen_percentage,
                "bias_score": float(chosen_percentage - correct_percentage),
                "correct_count": int(correct_at_level),
                "chosen_count": int(chosen_at_level),
                "total_questions": int(level_total),
                "answered_questions": int(level_answered_total),
            }

        analysis["level_bias"][
            f"level_{level}"
        ] = level_analysis  # Category-specific bias analysis
    for category in df["category"].unique():
        cat_data = df[df["category"] == category]

        # Filter out rows with missing contestant answers for percentage calculations
        cat_data_with_answers = cat_data[cat_data["contestant_answer"].notna()]
        cat_total = len(cat_data)
        cat_answered_total = len(cat_data_with_answers)

        category_analysis = {}
        for choice in ["A", "B", "C", "D"]:
            correct_in_cat = len(cat_data[cat_data["correct_answer"] == choice])
            chosen_in_cat = len(
                cat_data_with_answers[
                    cat_data_with_answers["contestant_answer"] == choice
                ]
            )

            # Calculate percentages based on answered questions only
            correct_percentage = (
                float((correct_in_cat / cat_total) * 100) if cat_total > 0 else 0
            )
            chosen_percentage = (
                float((chosen_in_cat / cat_answered_total) * 100)
                if cat_answered_total > 0
                else 0
            )

            category_analysis[choice] = {
                "correct_percentage": correct_percentage,
                "chosen_percentage": chosen_percentage,
                "bias_score": float(chosen_percentage - correct_percentage),
                "correct_count": int(correct_in_cat),
                "chosen_count": int(chosen_in_cat),
                "total_questions": int(cat_total),
                "answered_questions": int(cat_answered_total),
            }

        analysis["category_bias"][category] = category_analysis

    # Difficulty-based bias (by accuracy rate)
    easy_questions = df[df["is_correct"] == True]
    hard_questions = df[df["is_correct"] == False]

    for difficulty, data in [("easy", easy_questions), ("hard", hard_questions)]:
        diff_total = len(data)
        diff_analysis = {}

        for choice in ["A", "B", "C", "D"]:
            correct_in_diff = len(data[data["correct_answer"] == choice])
            chosen_in_diff = len(data[data["contestant_answer"] == choice])

            diff_analysis[choice] = {
                "correct_percentage": (
                    float((correct_in_diff / diff_total) * 100) if diff_total > 0 else 0
                ),
                "chosen_percentage": (
                    float((chosen_in_diff / diff_total) * 100) if diff_total > 0 else 0
                ),
                "bias_score": (
                    float((chosen_in_diff - correct_in_diff) / diff_total * 100)
                    if diff_total > 0
                    else 0
                ),
                "correct_count": int(correct_in_diff),
                "chosen_count": int(chosen_in_diff),
            }

        analysis["difficulty_bias"][
            difficulty
        ] = diff_analysis  # Before vs After Level 7 analysis
    before_7 = df[df["level"] < 7]
    after_7 = df[df["level"] >= 7]

    for period, data in [("before_level_7", before_7), ("level_7_and_after", after_7)]:
        # Filter out rows with missing contestant answers for percentage calculations
        data_with_answers = data[data["contestant_answer"].notna()]
        period_total = len(data)
        period_answered_total = len(data_with_answers)

        period_analysis = {}
        for choice in ["A", "B", "C", "D"]:
            correct_in_period = len(data[data["correct_answer"] == choice])
            chosen_in_period = len(
                data_with_answers[data_with_answers["contestant_answer"] == choice]
            )

            # Calculate percentages based on answered questions only
            correct_percentage = (
                float((correct_in_period / period_total) * 100)
                if period_total > 0
                else 0
            )
            chosen_percentage = (
                float((chosen_in_period / period_answered_total) * 100)
                if period_answered_total > 0
                else 0
            )

            period_analysis[choice] = {
                "correct_percentage": correct_percentage,
                "chosen_percentage": chosen_percentage,
                "bias_score": float(chosen_percentage - correct_percentage),
                "correct_count": int(correct_in_period),
                "chosen_count": int(chosen_in_period),
                "total_questions": int(period_total),
                "answered_questions": int(period_answered_total),
            }

        analysis["before_after_level_7"][period] = period_analysis

    # Elimination pattern bias
    eliminated_questions = df[df["eliminated"] == True]
    safe_questions = df[df["eliminated"] == False]

    for situation, data in [
        ("eliminated", eliminated_questions),
        ("safe", safe_questions),
    ]:
        sit_total = len(data)
        sit_analysis = {}

        for choice in ["A", "B", "C", "D"]:
            correct_in_sit = len(data[data["correct_answer"] == choice])
            chosen_in_sit = len(data[data["contestant_answer"] == choice])

            sit_analysis[choice] = {
                "correct_percentage": (
                    float((correct_in_sit / sit_total) * 100) if sit_total > 0 else 0
                ),
                "chosen_percentage": (
                    float((chosen_in_sit / sit_total) * 100) if sit_total > 0 else 0
                ),
                "bias_score": (
                    float((chosen_in_sit - correct_in_sit) / sit_total * 100)
                    if sit_total > 0
                    else 0
                ),
                "correct_count": int(correct_in_sit),
                "chosen_count": int(chosen_in_sit),
            }

        analysis["elimination_pattern_bias"][situation] = sit_analysis

    # Correct vs Chosen detailed analysis
    choice_performance = {}
    for choice in ["A", "B", "C", "D"]:
        # When this choice is correct, how often is it chosen?
        correct_choice_data = df[df["correct_answer"] == choice]
        chosen_when_correct = len(
            correct_choice_data[correct_choice_data["contestant_answer"] == choice]
        )

        # When this choice is chosen, how often is it correct?
        chosen_choice_data = df[df["contestant_answer"] == choice]
        correct_when_chosen = len(
            chosen_choice_data[chosen_choice_data["is_correct"] == True]
        )

        choice_performance[choice] = {
            "recognition_rate": (
                float((chosen_when_correct / len(correct_choice_data)) * 100)
                if len(correct_choice_data) > 0
                else 0
            ),
            "accuracy_when_chosen": (
                float((correct_when_chosen / len(chosen_choice_data)) * 100)
                if len(chosen_choice_data) > 0
                else 0
            ),
            "overconfidence": (
                float((len(chosen_choice_data) / len(correct_choice_data)) * 100)
                if len(correct_choice_data) > 0
                else 0
            ),
            "total_correct": int(len(correct_choice_data)),
            "total_chosen": int(len(chosen_choice_data)),
            "correctly_identified": int(chosen_when_correct),
            "wrongly_chosen": int(len(chosen_choice_data) - correct_when_chosen),
        }

    analysis["correct_vs_chosen_analysis"] = choice_performance

    # Summary insights
    most_biased_choice = max(
        analysis["overall_bias"].items(), key=lambda x: abs(x[1]["bias_score"])
    )
    most_accurate_choice = max(
        analysis["correct_vs_chosen_analysis"].items(),
        key=lambda x: x[1]["accuracy_when_chosen"],
    )
    most_overconfident_choice = max(
        analysis["correct_vs_chosen_analysis"].items(),
        key=lambda x: x[1]["overconfidence"],
    )

    analysis["insights"] = {
        "most_biased_choice": {
            "choice": most_biased_choice[0],
            "bias_score": float(most_biased_choice[1]["bias_score"]),
        },
        "most_accurate_choice": {
            "choice": most_accurate_choice[0],
            "accuracy": float(most_accurate_choice[1]["accuracy_when_chosen"]),
        },
        "most_overconfident_choice": {
            "choice": most_overconfident_choice[0],
            "overconfidence": float(most_overconfident_choice[1]["overconfidence"]),
        },
        "strategic_recommendations": {
            "avoid_bias_toward": (
                most_biased_choice[0]
                if most_biased_choice[1]["bias_score"] > 0
                else None
            ),
            "trust_when_seeing": most_accurate_choice[0],
            "be_cautious_with": (
                most_overconfident_choice[0]
                if most_overconfident_choice[1]["overconfidence"] > 100
                else None
            ),
        },
    }

    return jsonify(analysis)


@app.route("/api/pattern_analysis")
def get_pattern_analysis():
    # Import and run the pattern analysis
    from pattern_analysis import ContestantPatternAnalyzer

    analyzer = ContestantPatternAnalyzer("csv/milyoner_data_final.csv")
    report = analyzer.generate_comprehensive_report()

    # Convert complex data structures for JSON serialization
    def convert_counters(obj):
        if isinstance(obj, Counter):
            return dict(obj)
        elif isinstance(obj, defaultdict):
            return dict(obj)
        elif isinstance(obj, dict):
            return {k: convert_counters(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_counters(item) for item in obj]
        return obj

    # Clean the report for JSON serialization
    clean_report = convert_counters(report)

    return jsonify(clean_report)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
