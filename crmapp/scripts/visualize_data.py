import os
import sys
import django
import pandas as pd
import matplotlib.pyplot as plt

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

django.setup()

from django.db import connection

def visualize_lead_sources():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sourceoflead, COUNT(*)
            FROM crmapp_lead_management
            GROUP BY sourceoflead;
        """)
        data = cursor.fetchall()

    df = pd.DataFrame(data, columns=['Source', 'Count'])

    plt.figure(figsize=(10,5))
    plt.bar(df['Source'], df['Count'])
    plt.title('Leads by Source')
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_lead_sources()
