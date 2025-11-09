from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('crmapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead_management',
            name='branch',
            field=models.CharField(max_length=20, choices=[
                ('Bhiwandi', 'Bhiwandi'),
                ('Indore', 'Indore'),
                ('Hyderabad', 'Hyderabad'),
                ('Nagpur', 'Nagpur'),
                ('Amravti', 'Amravti'),
                ('Aurangabad', 'Aurangabad'),
                ('Baramati', 'Baramati'),
                ('Pune', 'Pune'),
            ], default='NA'),
        ),
    ]

