import pickle
import numpy as np
import pandas as pd

# Load trained model
with open("recommender_model.pkl", "rb") as f:
    model_data = pickle.load(f)

pivot = model_data["pivot"]
user_similarity = model_data["user_similarity"]

# Extract user and item lists
users = pivot.index.tolist()
items = pivot.columns.tolist()

print(f"\n✅ Loaded model with {len(users)} users and {len(items)} items")

# Choose a user for testing (first user)
target_user = users[0]

# Get similar users by user ID (not index!)
similarities = user_similarity.loc[target_user]
top_similar_users = similarities.sort_values(ascending=False).index[1:4]  # skip self

# Get mean item ratings of similar users
recommend_candidates = pivot.loc[top_similar_users].mean().sort_values(ascending=False)

# Filter out already-rated items
user_ratings = pivot.loc[target_user]
unrated_items = user_ratings[user_ratings == 0].index
recommendations = recommend_candidates.loc[unrated_items].head(5)

print(f"\n🎯 Recommendations for user '{target_user}':")
print(recommendations)
