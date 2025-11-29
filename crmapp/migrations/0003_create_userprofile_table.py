from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('crmapp', '0002_remove_userprofile_address_alter_userprofile_phone_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=20, choices=[
                    ('admin', 'Admin'),
                    ('sales', 'Sales'),
                    ('technician', 'Technician'),
                    ('customer', 'Customer'),
                ])),
                ('phone', models.CharField(max_length=15, blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
