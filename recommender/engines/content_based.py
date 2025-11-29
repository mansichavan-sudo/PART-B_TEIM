from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from recommender.models import Item, Rating
import numpy as np

def get_content_recommendations(user, top_k=5):
    """
    Simple content-based recommender using TF-IDF similarity.
    """
    items = list(Item.objects.all())
    if not items:
        return []

    item_texts = [i.content_blob() for i in items]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(item_texts)

    rated_items = Rating.objects.filter(user=user).select_related('item')
    if not rated_items.exists():
        return []

    liked_indices = [items.index(r.item) for r in rated_items if r.rating >= 4]
    if not liked_indices:
        return []

    liked_vectors = tfidf_matrix[liked_indices]
    scores = cosine_similarity(liked_vectors, tfidf_matrix).mean(axis=0)

    ranked_indices = np.argsort(scores)[::-1]
    recommended = []
    for idx in ranked_indices:
        if items[idx].id not in [r.item.id for r in rated_items]:
            recommended.append(items[idx])
        if len(recommended) >= top_k:
            break

    return recommended
