from django.db import models

# Create your models here.

class VisitingCard(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=15)
	company = models.CharField(max_length=255, blank=True)
	address = models.CharField(max_length=255, blank=True)
	card_image = models.ImageField(upload_to='cards/')
	uploaded_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.name

