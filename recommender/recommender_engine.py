# recommender/recommender_engine.py

import pickle
import os
import numpy as np
import pandas as pd
from django.db import connection
from sklearn.metrics.pairwise import cosine_similarity
from recommender.models import Rating, Item, SavedModel


# =========================================
# 🔹 1️⃣ AI-Based Collaborative Recommender
# =========================================

def load_trained_model(model_name="recommender_similarity"):
    """Load the saved cosine similarity matrix from database file path"""
    try:
        saved_model = SavedModel.objects.filter(name=model_name).latest("created_at")
        model_path = saved_model.file_path
        with open(model_path, "rb") as f:
            similarity_matrix = pickle.load(f)
        return similarity_matrix
    except SavedModel.DoesNotExist:
        print("⚠️ No trained model found. Run `python manage.py train_recommender` first.")
        return None


def generate_recommendations_for_user(user_id, top_n=5):
    """Generate top-N personalized recommendations for a given user"""
    ratings = Rating.objects.all().values("user", "item", "rating")
    df = pd.DataFrame(list(ratings))

    # 🧩 If no ratings at all — fallback to top-rated items
    if df.empty:
        print("⚠️ No rating data found — returning top popular products.")
        return Item.objects.all()[:top_n]

    pivot_table = df.pivot_table(index="user", columns="item", values="rating").fillna(0)

    # 🧍 If user never rated anything — fallback
    if user_id not in pivot_table.index:
        print("⚠️ No ratings found for this user — returning popular items.")
        top_items = (
            df.groupby("item")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
        )
        return Item.objects.filter(id__in=top_items)

    similarity_matrix = load_trained_model()
    if similarity_matrix is None:
        print("⚠️ No trained model found — returning top-rated items.")
        top_items = (
            df.groupby("item")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
        )
        return Item.objects.filter(id__in=top_items)

    # Predict scores
    user_vector = pivot_table.loc[user_id].values.reshape(1, -1)
    scores = np.dot(similarity_matrix, user_vector.T).flatten()

    user_rated_items = pivot_table.loc[user_id][pivot_table.loc[user_id] > 0].index
    all_items = pivot_table.columns
    unrated_items = [item for item in all_items if item not in user_rated_items]

    predictions = pd.DataFrame({
        "item": all_items,
        "predicted_score": scores
    })

    recommendations = (
        predictions[predictions["item"].isin(unrated_items)]
        .sort_values(by="predicted_score", ascending=False)
        .head(top_n)
    )

    # ⚡ Fallback if empty
    if recommendations.empty:
        print("⚠️ Model returned empty — showing fallback items.")
        top_items = (
            df.groupby("item")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
        )
        return Item.objects.filter(id__in=top_items)

    return Item.objects.filter(id__in=recommendations["item"].tolist())


# =========================================
# 🔹 2️⃣ SQL-Based Content & Collaborative
# =========================================

def get_content_based_recommendations(product_name):
    """Content-based: Get recommended products similar to the given product"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p2.product_name
            FROM pest_recommendations pr
            JOIN product_details p1 ON pr.base_product_id = p1.id
            JOIN product_details p2 ON pr.recommended_product_id = p2.id
            WHERE p1.product_name LIKE %s
            ORDER BY pr.confidence_score DESC
            LIMIT 5;
        """, [f"%{product_name}%"])
        rows = cursor.fetchall()
    return [r[0] for r in rows] if rows else []


def get_collaborative_recommendations(customer_id):
    """Collaborative filtering: Find similar customers and common products"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pr2.customer_id, COUNT(*) as common_count
            FROM pest_recommendations pr1
            JOIN pest_recommendations pr2 
              ON pr1.recommended_product_id = pr2.recommended_product_id
            WHERE pr1.customer_id = %s 
              AND pr2.customer_id != pr1.customer_id
            GROUP BY pr2.customer_id
            ORDER BY common_count DESC
            LIMIT 5;
        """, [customer_id])
        rows = cursor.fetchall()
    return [{"customer_id": r[0], "common_count": r[1]} for r in rows]


def get_upsell_recommendations(product_id):
    """Upsell: Suggest higher-end products similar to given one"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT rp.product_name
            FROM pest_recommendations pr
            JOIN product_details bp ON pr.base_product_id = bp.id
            JOIN product_details rp ON pr.recommended_product_id = rp.id
            WHERE pr.recommendation_type = 'Upsell'
              AND bp.id = %s
            ORDER BY pr.confidence_score DESC
            LIMIT 5;
        """, [product_id])
        rows = cursor.fetchall()
    return [r[0] for r in rows]


def get_crosssell_recommendations(customer_id):
    """Cross-sell: Recommend additional complementary products"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pd.product_name, COUNT(*) as count
            FROM pest_recommendations pr
            JOIN product_details pd ON pr.recommended_product_id = pd.id
            WHERE pr.customer_id = %s
              AND pr.recommendation_type = 'Cross-Sell'
            GROUP BY pd.product_name
            ORDER BY count DESC
            LIMIT 5;
        """, [customer_id])
        rows = cursor.fetchall()
    return [{"product_name": r[0], "count": r[1]} for r in rows]
