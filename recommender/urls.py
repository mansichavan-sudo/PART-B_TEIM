from django.urls import path
from . import views , api_views 

urlpatterns = [
    # UI Pages
    path('recommendations/ui/', views.recommendation_ui, name='recommendation_ui'),
    path('recommendations/dashboard/', views.recommendation_dashboard, name='recommendation_dashboard'),

    # APIs
    path('api/recommendations/', views.recommendations_view, name='api_recommendations'),
    path('api/collaborative/<int:customer_id>/', views.collaborative_view, name='api_collaborative'),
    path('api/upsell/<int:product_id>/', views.upsell_view, name='api_upsell'),
    path('api/crosssell/<int:customer_id>/', views.crosssell_view, name='api_crosssell'),
    path('api/products/', views.get_all_products, name='api_products'),
    path('api/ai-personalized/', views.api_ai_personalized, name='ai_personalized'),  # ✅ fixed

    path('send-message/', views.send_message_to_customer, name='send_message_to_customer'),

    path('api/send-message/<int:customer_id>/<int:product_id>/', views.generate_personalized_message, name='send_message'),

    path("api/message-templates/", views.get_message_templates, name="get_message_templates"),

    path("api/generate-message/", api_views.generate_message_view, name="generate_message"),
    path("api/send-message/", api_views.send_message_view, name="send_message"),



]

