# recommender/recommender_engine.py
import os
import pickle
import numpy as np
import pandas as pd
from django.db import models


from django.db import connection
from sklearn.metrics.pairwise import cosine_similarity

from recommender.models import Rating, Item, SavedModel, PestRecommendation
from crmapp.models import Product, customer_details


# ------------------------
# Paths
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINED_MODELS_DIR = os.path.join(BASE_DIR, "..", "trained_models")
os.makedirs(TRAINED_MODELS_DIR, exist_ok=True)

USER_ITEM_MATRIX = os.path.join(TRAINED_MODELS_DIR, "user_item_matrix.csv")
ITEM_SIM_MODEL = os.path.join(TRAINED_MODELS_DIR, "item_similarity_model.pkl")
USER_TOP5 = os.path.join(TRAINED_MODELS_DIR, "user_top5_recommendations.csv")


# ------------------------
# Fabricated helpers
# ------------------------
def load_fabricated_models():
    """Load fabricated CSVs if present (optional helper)."""
    try:
        user_item_df = pd.read_csv(USER_ITEM_MATRIX, index_col=0) if os.path.exists(USER_ITEM_MATRIX) else None
        item_sim_df = pd.read_csv(ITEM_SIM_MODEL, index_col=0) if os.path.exists(ITEM_SIM_MODEL) else None
        rec_df = pd.read_csv(USER_TOP5, index_col=0) if os.path.exists(USER_TOP5) else None
        return user_item_df, item_sim_df, rec_df
    except Exception as e:
        print("⚠️ Error loading fabricated models:", e)
        return None, None, None


def get_fabricated_recommendations(user_id, top_n=5):
    """Return fabricated top-n if available (index may be str or int)."""
    _, _, rec_df = load_fabricated_models()
    if rec_df is None:
        return []

    # ensure consistent index type
    idx = str(user_id)
    if idx in rec_df.index:
        items = rec_df.loc[idx].dropna().tolist()
        return items[:top_n]
    # try integer index
    if user_id in rec_df.index:
        items = rec_df.loc[user_id].dropna().tolist()
        return items[:top_n]

    # fallback: most frequent recommendations across users
    try:
        melted = rec_df.melt(value_name="product").dropna(subset=["product"])
        top = melted["product"].value_counts().head(top_n).index.tolist()
        return top
    except Exception:
        return []


# ------------------------
# Trained model loader
# ------------------------
def load_trained_model(model_name="recommender_similarity"):
    """
    Loads a saved similarity matrix (pickled DataFrame or numpy array).
    The SavedModel table (recommender.SavedModel) stores file_path.
    """
    try:
        saved_model = SavedModel.objects.filter(name=model_name).latest("created_at")
        model_path = saved_model.file_path
        with open(model_path, "rb") as f:
            model_obj = pickle.load(f)
        # Accept pandas.DataFrame or numpy array.
        if isinstance(model_obj, pd.DataFrame):
            return model_obj
        else:
            # if numpy array, convert to DataFrame with no index (caller must know mapping)
            return pd.DataFrame(model_obj)
    except SavedModel.DoesNotExist:
        print("⚠️ No trained model saved (SavedModel row missing).")
        return None
    except Exception as e:
        print("⚠️ Error loading saved model:", e)
        return None


# ------------------------
# Generate recommendations for a single user
# ------------------------ 
def generate_recommendations_for_user(customer_id, top_n=5):  # Renamed from user_id
    """
    Return top-N Item queryset for given customer_id (customer id).
    Priorities:
      1) fabricated (CSV)
      2) collaborative model (saved similarity)
      3) popular fallback
    """
    try:
        # 1) fabricated
        fabricated = get_fabricated_recommendations(customer_id, top_n)  # Updated
        if fabricated:
            pids = [int(x) for x in fabricated[:top_n] if str(x).isdigit()]
            items = Item.objects.filter(product_id__in=pids)
            # Attach dummy score for consistency
            for item in items:
                item.score = None  # Or compute if possible
            return items

        # 2) build rating pivot
        qs = Rating.objects.all().values("customer_id", "product_id", "rating")
        df = pd.DataFrame(list(qs))
        if df.empty:
            # fallback: return first top items by popularity (empty if none)
            top_products = Rating.objects.all().values("product_id").annotate(avg=models.Avg("rating")).order_by("-avg")[:top_n]
            top_pids = [r["product_id"] for r in top_products]
            items = Item.objects.filter(product_id__in=top_pids)[:top_n]
            for item in items:
                item.score = None
            return items

        # pivot: index = customer_id, columns = product_id
        pivot = df.pivot_table(index="customer_id", columns="product_id", values="rating", aggfunc="mean").fillna(0)

        if customer_id not in pivot.index:  # Updated
            # user has no ratings -> return top-rated products
            top_products = df.groupby("product_id")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
            items = Item.objects.filter(product_id__in=top_products)
            for item in items:
                item.score = None
            return items

        # load saved item-item similarity
        similarity_df = load_trained_model()
        if similarity_df is None:
            # fallback: compute simple item similarity from current data
            matrix = pivot.values
            if matrix.size == 0:
                return Item.objects.none()  # Empty queryset
            try:
                computed = cosine_similarity(matrix.T)
                similarity_df = pd.DataFrame(computed, index=pivot.columns, columns=pivot.columns)
            except Exception as e:
                print(f"⚠️ Error computing similarity: {e}")
                # fallback to popularity
                top_products = df.groupby("product_id")["rating"].mean().sort_values(ascending=False).head(top_n).index.tolist()
                items = Item.objects.filter(product_id__in=top_products)
                for item in items:
                    item.score = None
                return items

        # align matrix columns (similarity_df index must be product ids)
        if isinstance(similarity_df, pd.DataFrame):
            sim_index = list(map(int, similarity_df.index))
        else:
            sim_index = list(pivot.columns)  # best-effort

        # create user vector aligned to sim_index
        user_vector = pivot.loc[customer_id].reindex(index=sim_index, fill_value=0).values.reshape(1, -1)  # Updated

        # if similarity is df, convert to numpy with same order
        if isinstance(similarity_df, pd.DataFrame):
            sim_mat = similarity_df.reindex(index=sim_index, columns=sim_index).fillna(0).values
        else:
            sim_mat = np.array(similarity_df)

        # score = sim * user_vector
        try:
            scores = np.dot(sim_mat, user_vector.T).flatten()
        except Exception as e:
            print(f"⚠️ Error computing scores: {e}")
            scores = np.zeros(len(sim_index))

        # build predictions DataFrame
        preds = pd.DataFrame({"product_id": sim_index, "score": scores})
        # exclude items already rated by user
        rated = pivot.loc[customer_id][pivot.loc[customer_id] > 0].index.tolist()  # Updated
        preds = preds[~preds["product_id"].isin(rated)]
        preds = preds.sort_values("score", ascending=False).head(top_n)

        items = Item.objects.filter(product_id__in=preds["product_id"].astype(int).tolist())
        # Attach scores to items
        score_dict = dict(zip(preds["product_id"], preds["score"]))
        for item in items:
            item.score = score_dict.get(item.product_id, None)
        return items

    except Exception as e:
        print(f"⚠️ Unexpected error in generate_recommendations_for_user for customer {customer_id}: {e}")  # Updated
        return Item.objects.none()  # Return empty queryset on any error

# ------------------------
# SQL/ORM-based content & collaborative helpers
# ------------------------
def get_content_based_recommendations(product_name, top_n=5):
    """
    Return recommended product names for a base product_name using PestRecommendation table (ORM).
    """
    qs = (
        PestRecommendation.objects
        .filter(base_product__product_name__icontains=product_name)
        .order_by("-confidence_score")
        .values_list("recommended_product__product_name", flat=True)
        .distinct()[:top_n]
    )
    return list(qs)


def get_collaborative_recommendations(customer_id, top_k=5):
    """
    Find other customers who share recommended products (from PestRecommendation).
    Returns list of dicts: {customer_id, common_count}
    """
    rows = (
        PestRecommendation.objects
        .filter(customer_id=customer_id)
        .values_list("recommended_product_id", flat=True)
    )
    if not rows:
        return []

    recommended_ids = list(rows)
    # Count other customers who have the same recommended products
    qs = (
        PestRecommendation.objects
        .filter(recommended_product_id__in=recommended_ids)
        .exclude(customer_id=customer_id)
        .values("customer_id")
        .annotate(common_count=models.Count("recommended_product_id"))
        .order_by("-common_count")[:top_k]
    )
    return [{"customer_id": r["customer_id"], "common_count": r["common_count"]} for r in qs]


def get_upsell_recommendations(product_id, top_n=5):
    """
    Return product names recommended as upsell for a base product_id.
    """
    qs = (
        PestRecommendation.objects
        .filter(base_product_id=product_id, recommendation_type__iexact="upsell")
        .order_by("-confidence_score")
        .values_list("recommended_product__product_name", flat=True)
        .distinct()[:top_n]
    )
    return list(qs)


def get_crosssell_recommendations(user, top_n=5):
    """
    Recommend items for a user (customer) excluding already rated/purchased.
    Returns Item objects.
    """
    user_id = user.id if hasattr(user, "id") else int(user)
    purchased_pids = Rating.objects.filter(customer_id=user_id).values_list("product_id", flat=True).distinct()
    crosssell = Item.objects.exclude(product_id__in=list(purchased_pids)).order_by("?")[:top_n]
    return list(crosssell)


# ------------------------
# User-based recommender (file-backed)
# ------------------------
def get_user_based_recommendations(user_id, top_n=5):
    """
    Uses precomputed CSVs user_item_matrix and user_similarity_matrix
    to recommend items for a user.
    """
    base_dir = os.getcwd()
    user_item_path = os.path.join(base_dir, "trained_models", "user_item_matrix.csv")
    similarity_path = os.path.join(base_dir, "trained_models", "user_similarity_matrix.csv")

    if not os.path.exists(user_item_path) or not os.path.exists(similarity_path):
        print("⚠️ Precomputed files missing.")
        return []

    user_item = pd.read_csv(user_item_path, index_col=0)
    similarity = pd.read_csv(similarity_path, index_col=0)

    # ensure integer indices
    try:
        user_item.index = user_item.index.astype(int)
        similarity.index = similarity.index.astype(int)
        similarity.columns = similarity.columns.astype(int)
    except Exception:
        pass

    if user_id not in user_item.index:
        print(f"⚠️ User {user_id} not found in matrix.")
        return []

    sim_scores = similarity.loc[user_id]
    sim_scores = sim_scores[sim_scores > 0]

    if sim_scores.empty:
        print("⚠️ No similar users found.")
        return []

    user_ratings = user_item.loc[user_id]
    unrated_items = user_ratings[user_ratings == 0].index

    weighted_scores = {}
    for item in unrated_items:
        total_sim, weighted_sum = 0.0, 0.0
        for other_user, score in sim_scores.items():
            if user_item.loc[other_user, item] > 0:
                weighted_sum += score * user_item.loc[other_user, item]
                total_sim += score
        if total_sim > 0:
            weighted_scores[item] = weighted_sum / total_sim

    if not weighted_scores:
        item_means = user_item.replace(0, np.nan).mean(axis=0).sort_values(ascending=False)
        return item_means.head(top_n).index.tolist()

    ranked = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
    top_items = [int(item) for item, _ in ranked[:top_n]]
    items = Item.objects.filter(product_id__in=top_items).values_list("product_id", "title", "category")
    return [f"{i[1]} (Category: {i[2]})" for i in items]


# ------------------------
# Train and save collaborative (item-item) model
# ------------------------
def train_and_save_model():
    """
    Train item-item similarity (cosine) from Rating table and save with SavedModel.
    """
    qs = Rating.objects.all().values("customer_id", "product_id", "rating")
    df = pd.DataFrame(list(qs))

    if df.empty:
        print("❌ No ratings found in DB.")
        return None

    # pivot table: rows=customers, cols=products
    matrix = df.pivot_table(index="customer_id", columns="product_id", values="rating", aggfunc="mean").fillna(0)

    # compute item-item similarity
    sim = cosine_similarity(matrix.T)
    sim_df = pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns)

    # save to disk
    model_path = os.path.join(TRAINED_MODELS_DIR, "recommender_similarity.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(sim_df, f)

    # save path to SavedModel table
    SavedModel.objects.update_or_create(
        name="recommender_similarity",
        defaults={"file_path": model_path},
    )

    print(f"✅ Model trained (items={len(sim_df)}) and saved → {model_path}")
    return sim_df



def recommendations_with_scores(user_id, top_n=5):
    """Return top-N recommendations with predicted scores."""
    from recommender.models import Rating, Item
    import pandas as pd

    # Get recommended items
    items = generate_recommendations_for_user(user_id, top_n=top_n)

    # Load collaborative similarity matrix
    similarity_matrix = load_trained_model()
    if similarity_matrix is None:
        return [
            {"product_id": r.product_id, "title": r.title, "category": r.category, "score": None}
            for r in items
        ]

    # Create user-item pivot table
    ratings_df = pd.DataFrame(list(Rating.objects.all().values("customer_id", "product_id", "rating")))
    if ratings_df.empty:
        return [
            {"product_id": r.product_id, "title": r.title, "category": r.category, "score": None}
            for r in items
        ]

    pivot_table = ratings_df.pivot_table(index="customer_id", columns="product_id", values="rating").fillna(0)

    if user_id not in pivot_table.index:
        return [
            {"product_id": r.product_id, "title": r.title, "category": r.category, "score": None}
            for r in items
        ]

    user_vector = pivot_table.loc[user_id].values.reshape(1, -1)
    scores = (similarity_matrix.values @ user_vector.T).flatten()

    scored_items = []
    for r in items:
        if r.product_id in pivot_table.columns:
            score = scores[pivot_table.columns.get_loc(r.product_id)]
        else:
            score = None
        scored_items.append({
            "product_id": r.product_id,
            "title": r.title,
            "category": r.category,
            "score": float(score) if score is not None else None
        })

    return scored_items


from recommender.models import Item, Rating
from crmapp.models import customer_details

def recommender_for_customer(customer_id, top_n=5):
    """
    Simple example: returns top N items for a given customer.
    Replace this with your real recommendation logic.
    """
    # Placeholder: top-rated items (just as example)
    top_items = Item.objects.all()[:top_n]
    return top_items
