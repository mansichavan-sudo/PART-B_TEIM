# ===============================================================
# 📊 evaluate_models.py — Compare Accuracy of All Recommender Models
# ===============================================================

import numpy as np
import pandas as pd
from recommender.recommender_engine import (
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_upsell_recommendations,
    get_crosssell_recommendations,
    get_user_based_recommendations,
)
from crmapp.models import Product as Item  # ✅ Corrected import
from recommender.models import PestRecommendation


# ===============================================================
# 🔹 Utility: Evaluation Metrics (Precision, Recall, F1)
# ===============================================================
def precision_recall_f1(actual_items, predicted_items, k=5):
    """Compute Precision@K, Recall@K, and F1@K."""
    if not predicted_items:
        return 0, 0, 0

    predicted_k = predicted_items[:k]
    hits = len(set(actual_items) & set(predicted_k))

    precision = hits / k
    recall = hits / len(actual_items) if actual_items else 0
    f1 = (2 * precision * recall) / (precision + recall + 1e-8)
    return precision, recall, f1


# ===============================================================
# 🔹 Core Evaluator for Any Model
# ===============================================================
def evaluate_model(model_name, test_data, recommender_func, top_k=5):
    """Evaluate a given recommender function."""
    precisions, recalls, f1s = [], [], []

    for user_id, true_items in test_data.items():
        try:
            recs = recommender_func(user_id, top_k)

            # --- Normalize predictions ---
            if recs is None:
                recs = []

            # Case 1: QuerySet → extract 'product_name'
            if hasattr(recs, "values_list"):
                recs = list(recs.values_list("product_name", flat=True))

            # Case 2: List of dicts → extract name/id
            elif isinstance(recs, list) and recs and isinstance(recs[0], dict):
                recs = [
                    r.get("product_name")
                    or Item.objects.filter(product_id=r.get("id"))
                    .values_list("product_name", flat=True)
                    .first()
                    for r in recs
                    if r
                ]

            # Case 3: List of IDs → convert to product names
            elif isinstance(recs, list) and all(isinstance(x, (int, np.integer)) for x in recs):
                recs = list(Item.objects.filter(product_id__in=recs).values_list("product_name", flat=True))

            # Remove Nones and duplicates
            recs = [r for r in recs if r]
            recs = list(dict.fromkeys(recs))  # preserve order, remove duplicates

            # --- Compute metrics ---
            precision, recall, f1 = precision_recall_f1(true_items, recs, k=top_k)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        except Exception as e:
            print(f"⚠️ Error evaluating {model_name} for user {user_id}: {e}")

    precision_mean = np.mean(precisions)
    recall_mean = np.mean(recalls)
    f1_mean = np.mean(f1s)

    print(
        f"📈 {model_name}: Precision@{top_k}={precision_mean:.3f}, "
        f"Recall@{top_k}={recall_mean:.3f}, F1={f1_mean:.3f}"
    )

    return {
        "model": model_name,
        "precision": precision_mean,
        "recall": recall_mean,
        "f1": f1_mean,
    }


# ===============================================================
# 🔹 Load or Fabricate Test Data
# ===============================================================
def load_test_data():
    """
    Load actual customer → product mapping from PestRecommendation table.
    Falls back to fabricated demo data if empty.
    """
    data = {}
    records = PestRecommendation.objects.all().values("customer_id", "recommended_product_id")

    if records.exists():
        df = pd.DataFrame(records)
        for uid, group in df.groupby("customer_id"):
            product_names = (
                Item.objects.filter(product_id__in=group["recommended_product_id"].tolist())
                .values_list("product_name", flat=True)
            )
            data[int(uid)] = list(product_names)
    else:
        print("⚠️ No test data found in DB — using fabricated test set.")
        data = {
            1: ["Cockroach Control", "Termite Treatment"],
            2: ["Rodent Control"],
            3: ["Mosquito Fogging", "Bed Bug Treatment"],
        }

    return data


# ===============================================================
# 🔹 Evaluate All Models Together
# ===============================================================
def run_all_model_evaluations(top_k=5):
    """Run evaluations for all recommender models and print a comparison table."""
    test_data = load_test_data()

    results = []
    results.append(
        evaluate_model(
            "Content-Based",
            test_data,
            lambda u, k: get_content_based_recommendations("Cockroach"),
            top_k,
        )
    )
    results.append(evaluate_model("Collaborative", test_data, get_collaborative_recommendations, top_k))
    results.append(evaluate_model("Upsell", test_data, lambda u, k: get_upsell_recommendations(1), top_k))
    results.append(evaluate_model("Cross-Sell", test_data, get_crosssell_recommendations, top_k))
    results.append(evaluate_model("User-Based", test_data, get_user_based_recommendations, top_k))

    # Convert to DataFrame for clean view
    df = pd.DataFrame(results)
    print("\n============================")
    print("📊 MODEL PERFORMANCE SUMMARY")
    print("============================")
    print(df.to_string(index=False))

    return df


# ===============================================================
# 🔹 Main Execution
# ===============================================================
if __name__ == "__main__":
    print("🚀 Running Recommender System Evaluation...\n")
    summary_df = run_all_model_evaluations(top_k=5)
    print("\n✅ Evaluation Complete!")
