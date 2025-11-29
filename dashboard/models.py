from django.db import models

class Lead(models.Model):
    STATUS_CHOICES = [
        ('hot', 'Hot'),
        ('cold', 'Cold'),
        ('warm', 'Warm'),
        ('lost', 'Lost (FIO Order)'),
        ('not_interested', 'Not Interested')
    ]
    
    platform = models.CharField(max_length=50)
    source_of_lead = models.CharField(max_length=255)
    campaign_name = models.CharField(max_length=255)
    lead_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    contact_no = models.CharField(max_length=20)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    date_of_lead = models.DateField()
    visitors_name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.visitors_name} - {self.lead_status}'
