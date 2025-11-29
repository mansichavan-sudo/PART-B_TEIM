# crmapp/management/commands/load_message_templates.py
from django.core.management.base import BaseCommand
from crmapp.models import MessageTemplate  # Adjust app name if needed
import json
import os

class Command(BaseCommand):
    help = 'Load or update message templates from JSON fixture'

    def handle(self, *args, **options):
        fixture_path = os.path.join(os.path.dirname(__file__), '../../fixtures/templates_recommendation.json')
        
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR('Fixture file not found at: %s' % fixture_path))
            return
        
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        updated_count = 0
        for item in data:
            fields = item['fields']
            template, created = MessageTemplate.objects.update_or_create(
                name=fields['name'],
                defaults={
                    'message_type': fields['message_type'],
                    'category': fields['category'],
                    'lead_status': fields['lead_status'],
                    'subject': fields['subject'],
                    'body': fields['body'],
                    'attachment': fields['attachment'],
                    'is_active': fields['is_active'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created: %s' % fields['name']))
            else:
                self.stdout.write(self.style.WARNING('Updated: %s' % fields['name']))
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS('Successfully processed %d templates' % updated_count))