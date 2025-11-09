import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from .models import Item, Rating, SavedModel

MODEL_DIR = os.path.join(settings.BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

### -----------------------
### Content-based (TF-IDF)
### -----------------------
def train_content_model(save=True):
    items = Item.objects.all().values('id', 'title', 'description', 'category', 'tags')
    df = pd.DataFrame(list(items))
    if df.empty:
        return None

    df['text'] = df[['title', 'description', 'category', 'tags']].fillna('').agg(' '.join, axis=1)

    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['text'])

    model_path = os.path.join(MODEL_DIR, 'content_tfidf.joblib')
    if save:
        joblib.dump({'tfidf': tfidf, 'matrix': tfidf_matrix, 'ids': df['id'].tolist()}, model_path)
        SavedModel.objects.update_or_create(name='content_tfidf', defaults={'file_path': model_path})
    return {'tfidf': tfidf, 'matrix': tfidf_matrix, 'ids': df['id'].tolist()}

def load_content_model():
    try:
        sm = SavedModel.objects.get(name='content_tfidf')
        data = joblib.load(sm.file_path)
        return data
    except SavedModel.DoesNotExist:
        return None

def recommended_items_content(item_id, top_k=10):
    data = load_content_model()
    if not data:
        data = train_content_model()
        if not data:
            return []

    ids = data['ids']
    if item_id not in ids:
        return []

    idx = ids.index(item_id)
    matrix = data['matrix']
    # compute cosine similarity between item and all items
    sim = cosine_similarity(matrix[idx], matrix).flatten()
    # get top indices excluding self
    top_idx = np.argsort(-sim)
    top_idx = [i for i in top_idx if ids[i] != item_id][:top_k]
    top_ids = [ids[i] for i in top_idx]
    # return Item queryset in same order
    id_to_order = {id_: i for i, id_ in enumerate(top_ids)}
    items = list(Item.objects.filter(id__in=top_ids))
    items.sort(key=lambda x: id_to_order[x.id])
    return items

### --------------------------------
### Collaborative Filtering (SVD)
### --------------------------------
def train_cf_svd(n_components=50, save=True):
    # Build user-item matrix
    ratings = Rating.objects.all().values('user_id', 'item_id', 'rating')
    df = pd.DataFrame(list(ratings))
    if df.empty:
        return None

    user_ids = df['user_id'].unique().tolist()
    item_ids = df['item_id'].unique().tolist()
    user_map = {u: i for i, u in enumerate(user_ids)}
    item_map = {it: i for i, it in enumerate(item_ids)}

    R = np.zeros((len(user_ids), len(item_ids)))
    for row in df.itertuples():
        R[user_map[row.user_id], item_map[row.item_id]] = row.rating

    # Use TruncatedSVD to get latent factors (simple MF-ish)
    svd = TruncatedSVD(n_components=min(n_components, min(R.shape)-1))
    user_factors = svd.fit_transform(R)  # (n_users, k)
    item_factors = svd.components_.T     # (n_items, k)  (note: in sklearn SVD components_ shape is (k, n_items))

    model_path = os.path.join(MODEL_DIR, 'cf_svd.joblib')
    payload = {
        'svd': svd,
        'user_map': user_map,
        'item_map': item_map,
        'user_ids': user_ids,
        'item_ids': item_ids,
        'user_factors': user_factors,
        'item_factors': item_factors
    }
    if save:
        joblib.dump(payload, model_path)
        SavedModel.objects.update_or_create(name='cf_svd', defaults={'file_path': model_path})
    return payload

def load_cf_svd():
    try:
        sm = SavedModel.objects.get(name='cf_svd')
        data = joblib.load(sm.file_path)
        return data
    except SavedModel.DoesNotExist:
        return None

def recommended_items_cf(user_id, top_k=10):
    data = load_cf_svd()
    if not data:
        data = train_cf_svd()
        if not data:
            return []

    user_map = data['user_map']
    item_map = data['item_map']
    user_ids = data['user_ids']
    item_ids = data['item_ids']
    user_factors = data['user_factors']
    item_factors = data['item_factors']

    if user_id not in user_map:
        # Cold start: fallback to popular items (highest avg rating)
        popular = Rating.objects.values('item_id').annotate(avg=models.Avg('rating')).order_by('-avg')[:top_k]
        return [Item.objects.get(pk=p['item_id']) for p in popular]

    uidx = user_map[user_id]
    user_vector = user_factors[uidx]  # (k,)
    scores = item_factors.dot(user_vector)  # (n_items,)
    top_idx = np.argsort(-scores)[:top_k]
    top_item_ids = [item_ids[i] for i in top_idx]

    # return Items in order
    id_to_order = {id_: i for i, id_ in enumerate(top_item_ids)}
    items = list(Item.objects.filter(id__in=top_item_ids))
    items.sort(key=lambda x: id_to_order[x.id])
    return items
