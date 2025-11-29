import random
from django.utils import timezone

# Try to import models safely from crmapp or recommender
try:
    from crmapp.models import UserProfile as Customer, Product
except ImportError:
    from recommender.models import Customer, Product

# Import Rating model (some projects have it under recommender)
try:
    from crmapp.models import Rating
except ImportError:
    from recommender.models import Rating


def run(num_ratings=50):
    """
    Generate random customer-product ratings for testing recommendation models.
    Avoids duplicates and checks if data exists first.
    """
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    if not customers or not products:
        print("❌ No customers or products found in database.")
        return

    created = 0
    for _ in range(num_ratings):
        customer = random.choice(customers)
        product = random.choice(products)
        rating_value = random.randint(1, 5)

        # Avoid duplicate ratings
        if not Rating.objects.filter(customer=customer, product=product).exists():
            Rating.objects.create(
                customer=customer,
                product=product,
                rating=rating_value,
                timestamp=timezone.now()
            )
            created += 1

    print(f"✅ {created} random ratings created successfully.")
