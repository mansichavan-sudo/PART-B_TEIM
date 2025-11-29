# from django.contrib.auth import get_user_model
# from celery import shared_task
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from crm import settings
# from crmapp.models import lead_management

# @shared_task(bind=True)
# def send_hot_lead_emails(self):
#     send_lead_emails(lead_type="Hot")

# @shared_task(bind=True)
# def send_warm_lead_emails(self):
#     send_lead_emails(lead_type="Warm")

# @shared_task(bind=True)
# def send_cold_lead_emails(self):
#     send_lead_emails(lead_type="Cold")

# @shared_task(bind=True)
# def send_immediate_email(self, lead_id):
#     try:
#         lead = lead_management.objects.get(id=lead_id)
        
#         if lead.typeoflead == "NotInterested":
#             mail_subject = "Feedback Form"
#             template_name = "emails/thank_you.html"  
#         elif lead.typeoflead == "LossOfOrder":
#             mail_subject = "Thank You for Considering Us"
#             template_name = "emails/feedback_request.html"
#         else:
#             return "Invalid lead type"

#         message = render_to_string(template_name, {'lead': lead})  
        
        
#         email = EmailMultiAlternatives(
#             subject=mail_subject,
#             body=message,
#             from_email=settings.EMAIL_HOST_USER,
#             to=[lead.customeremail],  
#         )
#         email.attach_alternative(message, "text/html") 
#         email.send(fail_silently=False)

#         return "Email sent to customer"
    
#     except lead_management.DoesNotExist:
#         return "Lead not found"
#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# def send_lead_emails(lead_type):
#     leads = lead_management.objects.filter(typeoflead=lead_type)  
    
#     for lead in leads:
#         mail_subject = f"Follow-up for {lead_type.capitalize()} Lead"
#         template_name = f"emails/{lead_type}.html" 
#         message = render_to_string(template_name, {'lead': lead})  
        
#         email = EmailMultiAlternatives(
#             subject=mail_subject,
#             body=message,
#             from_email=settings.EMAIL_HOST_USER,
#             to=[lead.customeremail],  
#         )
#         email.attach_alternative(message, "text/html")
#         email.send(fail_silently=False)

#     return "Done"
