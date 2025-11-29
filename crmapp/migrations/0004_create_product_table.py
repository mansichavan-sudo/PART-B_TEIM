from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmapp', '0003_create_userprofile_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('category', models.CharField(
                    max_length=50,
                    choices=[
                        ('Pest Control', 'Pest Control'),
                        ('Fumigation', 'Fumigation'),
                        ('Product Sale', 'Product Sale'),
                    ],
                    default="NULL"
                )),
            ],
        ),
    ]
