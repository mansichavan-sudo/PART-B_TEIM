from django.contrib import admin
from .models import Item, Rating, SavedModel

admin.site.register(Item)
admin.site.register(Rating)
admin.site.register(SavedModel)
