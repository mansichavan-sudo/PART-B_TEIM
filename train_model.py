import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# ===================================
# 📥 Load fabricated or database data
# ===================================
ratings = pd.read_csv("data/user_item_ratings.csv")  # must have columns: user_id, item_id, rating

# Pivot the data into user-item matrix
pivot = ratings.pivot_table(index="user_id", columns="item_id", values="rating").fillna(0)

# ===================================
# 🧠 Compute similarity-based model
# ===================================
user_similarity = cosine_similarity(pivot)
user_similarity_df = pd.DataFrame(user_similarity, index=pivot.index, columns=pivot.index)

print("✅ User similarity matrix shape:", user_similarity_df.shape)

# ===================================
# 💾 Save model artifacts
# ===================================
model_data = {
    "pivot": pivot,
    "user_similarity": user_similarity_df
}

with open("recommender_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("✅ Model trained and saved successfully (simple CF model).")
