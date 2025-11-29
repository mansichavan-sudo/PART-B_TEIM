# pest_recommender_train.py
import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity

# Paths
input_path = os.path.join(os.getcwd(), "trained_models", "recsys_interactions_cleaned.csv")
matrix_path = os.path.join(os.getcwd(), "trained_models", "user_item_matrix.csv")
model_path = os.path.join(os.getcwd(), "trained_models", "user_similarity_matrix.csv")

print("📂 Loading cleaned dataset from:", input_path)
df = pd.read_csv(input_path)

# Step 1️⃣ — Create user-item matrix (ratings)
pivot_df = df.pivot_table(index="user_id", columns="item_id", values="rating", fill_value=0)
print("\n✅ User–Item Matrix (sample):")
print(pivot_df.head())

# Step 2️⃣ — Calculate cosine similarity between users
similarity_matrix = cosine_similarity(pivot_df)
similarity_df = pd.DataFrame(similarity_matrix, index=pivot_df.index, columns=pivot_df.index)

print("\n✅ User Similarity Matrix (sample):")
print(similarity_df.head())

# Step 3️⃣ — Save outputs
pivot_df.to_csv(matrix_path)
similarity_df.to_csv(model_path)

print(f"\n💾 Saved matrices:")
print(f"User–Item Matrix → {matrix_path}")
print(f"User Similarity Matrix → {model_path}")
print("\n✅ Training completed successfully!")
