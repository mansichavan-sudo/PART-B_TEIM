from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crmapp.models import lead_management as Lead
from recommender.models import Item, Rating

User = get_user_model()

class Command(BaseCommand):
    help = "Import interactions (like ratings) from CRM leads"

    def handle(self, *args, **options):
        default_user = User.objects.first()  # fallback user (e.g., admin)
        leads = Lead.objects.all()

        for lead in leads:
            if lead.maincategory:  # or product_name, depending on your model
                item, _ = Item.objects.get_or_create(title=lead.maincategory)
                Rating.objects.update_or_create(
                    user=default_user,
                    item=item,
                    defaults={'rating': 5.0}
                )

        self.stdout.write(self.style.SUCCESS("✅ Imported interactions successfully."))
