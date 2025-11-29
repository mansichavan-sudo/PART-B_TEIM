from crmapp.models import UserProfile, Product
from recommender.models import PestRecommendation
from django.utils import timezone
from decimal import Decimal

def populate_recommendations():
    PestRecommendation.objects.all().delete()
    for cust in UserProfile.objects.all()[:5]:
        product_ids = list(Product.objects.values_list('product_id', flat=True)[:2])
        if not product_ids:
            print("⚠️ No Product records found in Product table!")
            break
        for pid in product_ids:
            PestRecommendation.objects.create(
                customer_id=cust.id,
                base_product_id=product_ids[0],
                recommended_product_id=pid,
                recommendation_type="cross-sell",
                confidence_score=Decimal("0.85"),
                created_at=timezone.now()
            )
    print("✅ Sample PestRecommendation records created:", PestRecommendation.objects.count())

populate_recommendations()
