import numpy as np
import pandas as pd
import pickle
from recommender.models import Rating, Item, SavedModel, PestRecommendation
from crmapp.models import customer_details, Product

def generate_recommendations_for_user(customer_id, top_n=5, return_scores=False):
    ratings_qs = Rating.objects.all().values("customer_id", "product_id", "rating")
    df = pd.DataFrame(list(ratings_qs))

    # Fallback: no ratings
    if df.empty:
        popular_items = Item.objects.all()[:top_n]
        rec_list = []
        for i in popular_items:
            if i.product:
                PestRecommendation.objects.create(
                    customer_id=customer_id,
                    base_product_id=None,
                    recommended_product_id=i.product.product_id,
                    recommendation_type="collaborative",
                    confidence_score=0
                )
            if return_scores:
                rec_list.append({
                    "product_id": i.product.product_id if i.product else None,
                    "title": i.title,
                    "category": i.category,
                    "score": 0
                })
        return rec_list if return_scores else popular_items

    pivot_table = df.pivot_table(index="customer_id", columns="product_id", values="rating").fillna(0)

    if customer_id not in pivot_table.index:
        top_products = df.groupby("product_id")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
        items = Item.objects.filter(product_id__in=top_products)
        rec_list = []
        for i in items:
            if i.product:
                PestRecommendation.objects.create(
                    customer_id=customer_id,
                    base_product_id=None,
                    recommended_product_id=i.product.product_id,
                    recommendation_type="collaborative",
                    confidence_score=0
                )
            if return_scores:
                rec_list.append({
                    "product_id": i.product.product_id if i.product else None,
                    "title": i.title,
                    "category": i.category,
                    "score": 0
                })
        return rec_list if return_scores else items

    # Load similarity matrix
    try:
        saved_model = SavedModel.objects.filter(name="recommender_similarity").latest("created_at")
        with open(saved_model.file_path, "rb") as f:
            similarity_matrix = pickle.load(f)
    except Exception:
        similarity_matrix = None

    if similarity_matrix is None:
        top_products = df.groupby("product_id")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
        items = Item.objects.filter(product_id__in=top_products)
        rec_list = []
        for i in items:
            if i.product:
                PestRecommendation.objects.create(
                    customer_id=customer_id,
                    base_product_id=None,
                    recommended_product_id=i.product.product_id,
                    recommendation_type="collaborative",
                    confidence_score=0
                )
            if return_scores:
                rec_list.append({
                    "product_id": i.product.product_id if i.product else None,
                    "title": i.title,
                    "category": i.category,
                    "score": 0
                })
        return rec_list if return_scores else items

    # Predict scores
    user_vector = pivot_table.loc[customer_id].values.reshape(1, -1)
    scores = np.dot(similarity_matrix, user_vector.T).flatten()

    rated_items = pivot_table.loc[customer_id][pivot_table.loc[customer_id] > 0].index
    all_items = pivot_table.columns
    unrated_items = [i for i in all_items if i not in rated_items]

    predictions = pd.DataFrame({"product_id": all_items, "predicted_score": scores})
    recommendations = predictions[predictions["product_id"].isin(unrated_items)].sort_values("predicted_score", ascending=False).head(top_n)

    items_qs = Item.objects.filter(product_id__in=recommendations["product_id"].tolist())
    rec_list = []

    for i in items_qs:
        score = 0
        if i.product:
            score = predictions.loc[predictions["product_id"] == i.product.product_id, "predicted_score"].values[0]
            PestRecommendation.objects.create(
                customer_id=customer_id,
                base_product_id=None,
                recommended_product_id=i.product.product_id,
                recommendation_type="collaborative",
                confidence_score=score
            )
        if return_scores:
            rec_list.append({
                "product_id": i.product.product_id if i.product else None,
                "title": i.title,
                "category": i.category,
                "score": float(score)
            })

    return rec_list if return_scores else items_qs
