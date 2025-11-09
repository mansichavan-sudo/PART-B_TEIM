from django.db import models
from django.conf import settings

class Item(models.Model):
    # Example content fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=128, blank=True)
    tags = models.CharField(max_length=512, blank=True)  # comma separated tags
    created_at = models.DateTimeField(auto_now_add=True)

    def content_blob(self):
        # The combined text used by content-based recommender
        parts = [self.title or '', self.description or '', self.category or '', self.tags or '']
        return ' '.join(parts)

    def __str__(self):
        return self.title

class Rating(models.Model):
    # Users rate items (for CF)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.FloatField()  # e.g., 1-5
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')

class SavedModel(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., 'content_tfidf', 'cf_svd'
    file_path = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)


 

class MessageTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('upsell', 'Upsell'),
        ('crosssell', 'Cross-sell'),
        ('general', 'General'),
    ]

    template_name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    content = models.TextField()

     

    def __str__(self):
        return self.template_name
    

class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('purchase', 'Purchase'),
        ('call', 'Call'),
        ('recommend', 'Recommendation Shown'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Optional extra info

    class Meta:
        unique_together = ('user', 'item', 'interaction_type')
        db_table = 'recommender_interaction'

    def __str__(self):
        return f"{self.user.username} - {self.item.title} ({self.interaction_type})"




class PestRecommendation(models.Model):
    customer_id = models.IntegerField()
    base_product_id = models.IntegerField()
    recommended_product_id = models.IntegerField()
    recommendation_type = models.CharField(max_length=20)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pest_recommendations'

    def __str__(self):
        return f"{self.recommendation_type} (Customer {self.customer_id})"