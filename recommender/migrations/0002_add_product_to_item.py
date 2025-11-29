from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='product',
            field=models.OneToOneField(
                to='crmapp.Product',
                on_delete=models.CASCADE,
                null=True,
                blank=True,
                related_name='item'
            ),
        ),
    ]
