# crmapp/management/commands/clean_data.py

from django.core.management.base import BaseCommand
from crmapp.models import lead_management   # correct model import

class Command(BaseCommand):
    help = 'Clean and standardize CRM data'

    def handle(self, *args, **options):

        # 1. Update null customer_type for Residential
        lead_management.objects.filter(
            customer_type__isnull=True,
            customersegment='Residential'
        ).update(customer_type='Individual')

        # 2. Update null customer_type for Industrial / Commercial
        lead_management.objects.filter(
            customer_type__isnull=True,
            customersegment='Industrial / Commercial'
        ).update(customer_type='Organization')

        # Example: Fill missing secondary contact if required
        # lead_management.objects.filter(secondarycontact__isnull=True).update(secondarycontact='N/A')

        self.stdout.write(self.style.SUCCESS('Data cleaning completed.'))
