from django.db import models
from crmapp.models import customer_details
from django.utils import timezone  # Import timezone for default date
    

class Meeting(models.Model):
    customer = models.ForeignKey(customer_details, on_delete=models.CASCADE, null=True, blank=True)
    meeting_date = models.DateField(default=timezone.now)  # Automatically sets today's date
    meeting_time = models.TimeField(default=timezone.now)
    minutes_of_meeting = models.TextField(default="No minutes recorded")
    participants = models.TextField(default="No participants")
    meeting_agenda = models.TextField(default="No agenda provided")

    def __str__(self):
        return f"Meeting with {self.customer.firstname} {self.customer.lastname} on {self.meeting_date} at {self.meeting_time}"

    