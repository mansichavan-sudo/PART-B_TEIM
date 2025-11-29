# ============================================================
# File: train_model_from_csv.py
# Description: Train a Collaborative Filtering (SVD) model
# using your prepared dataset (train.csv, val.csv, test.csv)
# ============================================================

import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
import pickle
import os

# ------------------------------------------------------------
# 1️⃣ Load datasets
# ------------------------------------------------------------
print("📥 Loading datasets...")
train_path = "train.csv"
val_path = "val.csv"
test_path = "test.csv"

train_df = pd.read_csv(train_path)
val_df = pd.read_csv(val_path)
test_df = pd.read_csv(test_path)

print(f"✅ Loaded: {len(train_df)} train, {len(val_df)} val, {len(test_df)} test records")

# ------------------------------------------------------------
# 2️⃣ Combine train + val for full training (optional)
# ------------------------------------------------------------
full_train_df = pd.concat([train_df, val_df], ignore_index=True)

# Surprise needs: user, item, rating
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(full_train_df[['user_idx', 'item_idx', 'rating']], reader)

# ------------------------------------------------------------
# 3️⃣ Split data for quick evaluation
# ------------------------------------------------------------
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# ------------------------------------------------------------
# 4️⃣ Train SVD (Matrix Factorization)
# ------------------------------------------------------------
print("🚀 Training SVD model...")
algo = SVD(n_factors=50, n_epochs=25, lr_all=0.005, reg_all=0.02)
algo.fit(trainset)

# ------------------------------------------------------------
# 5️⃣ Evaluate model performance
# ------------------------------------------------------------
predictions = algo.test(testset)
rmse = accuracy.rmse(predictions)
print(f"📊 RMSE: {rmse:.4f}")

# ------------------------------------------------------------
# 6️⃣ Save trained model
# ------------------------------------------------------------
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "recommender_model.pkl")

with open(model_path, "wb") as f:
    pickle.dump(algo, f)

print(f"✅ Model saved to {model_path}")

# ------------------------------------------------------------
# 7️⃣ Quick sanity test (recommendations)
# ------------------------------------------------------------
def recommend_for_user(algo, user_id, all_items, top_n=5):
    """Generate top-N recommendations for a user."""
    user_items = []
    for iid in all_items:
        est = algo.predict(user_id, iid).est
        user_items.append((iid, est))
    ranked = sorted(user_items, key=lambda x: x[1], reverse=True)[:top_n]
    return ranked

# test recommend for first user
unique_items = train_df['item_idx'].unique().tolist()
sample_user = int(train_df['user_idx'].iloc[0])
top_recs = recommend_for_user(algo, sample_user, unique_items)

print(f"\n🎯 Top Recommendations for user {sample_user}:")
for iid, score in top_recs:
    print(f"  Item {iid} → predicted rating {score:.2f}")
