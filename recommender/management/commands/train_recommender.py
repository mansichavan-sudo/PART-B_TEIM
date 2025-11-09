from django.core.management.base import BaseCommand
from recommender.models import Rating, SavedModel
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class Command(BaseCommand):
    help = "Train the recommender system using existing ratings"

    def handle(self, *args, **options):
        # Load ratings data
        ratings = Rating.objects.all().values('user', 'item', 'rating')
        if not ratings:
            self.stdout.write(self.style.WARNING("⚠️ No ratings data found. Please import interactions first."))
            return

        # Convert to DataFrame
        df = pd.DataFrame(ratings)
        pivot_table = df.pivot_table(index='user', columns='item', values='rating').fillna(0)

        # Compute cosine similarity between items
        similarity_matrix = cosine_similarity(pivot_table.T)

        # Save model to file
        model_dir = "trained_models"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "recommender_similarity.pkl")

        with open(model_path, "wb") as f:
            pickle.dump(similarity_matrix, f)

        # Update or create SavedModel record
        SavedModel.objects.update_or_create(
            name="recommender_similarity",
            defaults={"file_path": model_path}
        )

        self.stdout.write(self.style.SUCCESS("✅ Recommender model trained and saved successfully!"))
