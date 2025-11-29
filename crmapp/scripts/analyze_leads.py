# crmapp/scripts/analyze_leads.py

import os
import sys
import django

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Load correct Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

django.setup()

from django.db import connection
from crmapp.models import lead_management, main_followup


def analyze_lead_conversion():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT lm.sourceoflead, COUNT(lm.id) AS total_leads, 
                   SUM(CASE WHEN mf.order_status = 'Close Win' THEN 1 ELSE 0 END) AS wins
            FROM crmapp_lead_management lm
            LEFT JOIN crmapp_main_followup mf ON lm.id = mf.lead_id
            GROUP BY lm.sourceoflead
            ORDER BY wins DESC;
        """)
        results = cursor.fetchall()

        for row in results:
            print(f"Source: {row[0]}, Total Leads: {row[1]}, Wins: {row[2]}")


if __name__ == '__main__':
    analyze_lead_conversion()
