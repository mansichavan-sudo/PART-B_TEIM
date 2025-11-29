import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from math import sqrt

from django.db import connection
from recommender.models import Rating


# ======================================
# 📦 1️⃣ Load Rating Data
# ======================================
def load_data():
    """Load user-item ratings from the database."""
    df = pd.DataFrame(list(Rating.objects.all().values('user_id', 'item_id', 'rating')))
    if df.empty:
        print("⚠️ No ratings found in database.")
    else:
        print(f"✅ Loaded {len(df)} ratings from database.")
    return df


# ======================================
# 🧠 2️⃣ Build User-Item Matrix
# ======================================
def build_matrix(df):
    """Convert user-item ratings into a pivot table (matrix)."""
    pivot = df.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    return pivot


# ======================================
# 🔍 3️⃣ Predict using Collaborative Filtering
# ======================================
def predict_ratings(user_item_matrix):
    """Compute predicted ratings using user-user collaborative filtering."""
    similarity = cosine_similarity(user_item_matrix)
    np.fill_diagonal(similarity, 0)
    sim_matrix = pd.DataFrame(similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    # Avoid division by zero
    denom = np.array([np.abs(sim_matrix).sum(axis=1)]).T
    denom[denom == 0] = 1e-9  # prevent divide by zero

    pred_ratings = np.dot(sim_matrix, user_item_matrix) / denom
    return pd.DataFrame(pred_ratings, index=user_item_matrix.index, columns=user_item_matrix.columns)


# ======================================
# 🎯 4️⃣ Ranking Metrics (Precision@K, Recall@K)
# ======================================
def precision_recall_at_k(actual, predicted, k=5):
    precisions, recalls = [], []

    for user, true_items in actual.items():
        if user not in predicted:
            continue

        pred_items = predicted[user][:k]
        hits = len(set(pred_items) & set(true_items))
        precisions.append(hits / k if k else 0)
        recalls.append(hits / len(true_items) if len(true_items) else 0)

    if not precisions:
        return 0.0, 0.0, 0.0

    precision = np.mean(precisions)
    recall = np.mean(recalls)
    f1 = (2 * precision * recall) / (precision + recall + 1e-9)
    return precision, recall, f1


# ======================================
# 🧪 5️⃣ Main Evaluation Function
# ======================================
def evaluate():
    print("📥 Loading data...")
    df = load_data()
    if df.empty:
        return

    # ✅ Ensure multiple ratings per user before splitting
    valid_users = df['user_id'].value_counts()
    df = df[df['user_id'].isin(valid_users[valid_users > 1].index)]

    if df.empty:
        print("⚠️ Not enough overlapping user data for evaluation.")
        return

    # ✅ Split so that each user appears in both train & test
    train_df = df.groupby('user_id', group_keys=False).apply(
        lambda x: x.sample(frac=0.8, random_state=42)
    )
    test_df = df.drop(train_df.index)

    print(f"🧩 Train: {len(train_df)} | Test: {len(test_df)}")

    train_matrix = build_matrix(train_df)
    pred_matrix = predict_ratings(train_matrix)

    # Evaluate on test set
    y_true, y_pred = [], []
    for _, row in test_df.iterrows():
        user, item, true_rating = row['user_id'], row['item_id'], row['rating']
        if user in pred_matrix.index and item in pred_matrix.columns:
            pred_rating = pred_matrix.loc[user, item]
            if not np.isnan(pred_rating):
                y_true.append(true_rating)
                y_pred.append(pred_rating)

    print(f"📊 Matched samples for evaluation: {len(y_true)}")

    if len(y_true) == 0:
        print("⚠️ No overlapping samples found between train/test. Try adding more ratings.")
        return

    # Compute numeric metrics
    rmse = sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    print(f"📈 RMSE: {rmse:.4f} | MAE: {mae:.4f}")

    # Ranking metrics
    actual_items = test_df.groupby('user_id')['item_id'].apply(list).to_dict()
    predicted_items = {
        user: list(pred_matrix.loc[user].sort_values(ascending=False).index)
        for user in pred_matrix.index
    }

    precision, recall, f1 = precision_recall_at_k(actual_items, predicted_items, k=5)
    print(f"🎯 Precision@5: {precision:.4f} | Recall@5: {recall:.4f} | F1: {f1:.4f}")


# ======================================
# ▶️ Run directly
# ======================================
if __name__ == "__main__":
    evaluate()
