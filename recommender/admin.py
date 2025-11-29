from django.contrib import admin

# Lazy imports inside function to avoid circular import
def register_recommender_models():
    from .models import Item, Rating, SavedModel, Interaction, PestRecommendation, SentMessageLog
    from crmapp.models import MessageTemplates

    admin.site.register(Item)
    admin.site.register(Rating)
    admin.site.register(SavedModel)
    admin.site.register(Interaction)
    admin.site.register(PestRecommendation)
    admin.site.register(SentMessageLog)

    # admin.site.register(MessageTemplates)  # optional

register_recommender_models()
