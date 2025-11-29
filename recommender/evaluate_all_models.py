import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from recommender.models import Rating, Item
from .recommender_engine import (
    train_and_save_model,
    generate_recommendations_for_user,   # ✅ Added missing import
    get_user_based_recommendations,      # ✅ Added missing import
    get_collaborative_recommendations,
    get_content_based_recommendations,
    get_crosssell_recommendations,
    get_upsell_recommendations,
)

# ---------------------------------------------------
# 🔹 Helper: Precision@K, Recall@K, F1
# ---------------------------------------------------
def precision_recall_f1(actual, predicted, k=5):
    actual_set = set(actual)
    pred_set = set(predicted[:k])
    hits = len(actual_set & pred_set)
    precision = hits / k if k else 0
    recall = hits / len(actual_set) if actual_set else 0
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)
    return precision, recall, f1


# ---------------------------------------------------
# 🔹 Evaluate a single recommender function
# ---------------------------------------------------
def evaluate_model(model_name, test_data, recommender_func, top_k=5):
    precisions, recalls, f1s = [], [], []
    for user_id, actual_items in test_data.items():
        try:
            recs = recommender_func(user_id, top_k)
            rec_names = [r if isinstance(r, str) else getattr(r, "title", str(r)) for r in recs]
            precision, recall, f1 = precision_recall_f1(actual_items, rec_names, k=top_k)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)
        except Exception as e:
            print(f"⚠️ Error evaluating {model_name} for user {user_id}: {e}")
            continue

    results = {
        "Model": model_name,
        "Precision@K": np.mean(precisions),
        "Recall@K": np.mean(recalls),
        "F1@K": np.mean(f1s),
    }
    print(f"📊 {model_name}: P={results['Precision@K']:.3f}, R={results['Recall@K']:.3f}, F1={results['F1@K']:.3f}")
    return results


# ---------------------------------------------------
# 🔹 Step 1: Build test dataset
# ---------------------------------------------------
def build_test_data():
    ratings = list(Rating.objects.values("user_id", "item_id", "rating"))
    if not ratings:
        print("⚠️ No ratings found. Please add data first.")
        return {}

    df = pd.DataFrame(ratings)
    # Only consider positive interactions (e.g. rating >= 3)
    test_data = {}
    for user, group in df.groupby("user_id"):
        liked_items = group[group["rating"] >= 3]["item_id"].tolist()
        item_names = list(Item.objects.filter(id__in=liked_items).values_list("title", flat=True))
        test_data[user] = item_names
    return test_data


# ---------------------------------------------------
# 🔹 Step 2: Evaluate all models together
# ---------------------------------------------------
def evaluate_all_models():
    test_data = build_test_data()
    if not test_data:
        return

    results = []

    # Collaborative (AI-based cosine similarity)
    results.append(evaluate_model("Collaborative", test_data, generate_recommendations_for_user))

    # User-Based
    results.append(evaluate_model("User-Based", test_data, get_user_based_recommendations))

    # Content-Based (via product name match)
    sample_product = next(iter(Item.objects.values_list("title", flat=True)), None)
    if sample_product:
        def content_recommender_wrapper(_user_id, top_k=5):
            return get_content_based_recommendations(sample_product)
        results.append(evaluate_model("Content-Based", test_data, content_recommender_wrapper))

    # Upsell
    sample_item_id = next(iter(Item.objects.values_list("id", flat=True)), None)
    if sample_item_id:
        def upsell_wrapper(_user_id, top_k=5):
            return get_upsell_recommendations(sample_item_id)
        results.append(evaluate_model("Upsell", test_data, upsell_wrapper))

    # Cross-Sell
    results.append(evaluate_model("Cross-Sell", test_data, get_crosssell_recommendations))

    print("\n✅ Final Model Comparison Table:")
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    return df


# ---------------------------------------------------
# 🔹 Run directly
# ---------------------------------------------------
if __name__ == "__main__":
    evaluate_all_models()
