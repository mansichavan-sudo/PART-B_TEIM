from django.shortcuts import render
from crmapp.models import lead_management
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User

# Helper function to send emails
def send_email(subject, recipient, template_name, context):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()

# Automated lead email sending
def automate_lead_emails(request):
    leads = lead_management.objects.all()
    
    for lead in leads:
        try:
            user = User.objects.get(email=lead.customeremail)
            last_login = user.last_login  
            
            lead.update_next_email_date(last_login)
            
            if lead.next_email_date and lead.next_email_date <= timezone.now():
                if lead.typeoflead == 'Hot':
                    send_immediate_follow_up(lead)
                elif lead.typeoflead == 'Warm':
                    send_regular_follow_up(lead)
                elif lead.typeoflead == 'Cold':
                    send_occasional_follow_up(lead)
                elif lead.typeoflead == 'NotInterested':
                    send_thank_you(lead)
                elif lead.typeoflead == 'LossOfOrder':
                    send_feedback_request(lead)
        
        except User.DoesNotExist:
            # Handle the case where the user associated with the lead does not exist
            print(f"User with email {lead.customeremail} does not exist in auth_user.")
    
    return render(request, 'lead_automation/automate_leads.html', {'leads': leads})

def send_immediate_follow_up(lead):
    lead.follow_up_date = timezone.now() + timezone.timedelta(days=1)
    lead.save()
    context = {
        "lead": lead,
        "message": "We are following up with you as you're identified as a hot lead."
    }
    send_email("Immediate Follow-Up", lead.customeremail, "emails/immediate_follow_up.html", context)

def send_regular_follow_up(lead):
    lead.follow_up_date = timezone.now() + timezone.timedelta(days=3)
    lead.save()
    context = {
        "lead": lead,
        "message": "We are following up with you as you're identified as a warm lead."
    }
    send_email("Regular Follow-Up", lead.customeremail, "emails/regular_follow_up.html", context)

def send_occasional_follow_up(lead):
    lead.follow_up_date = timezone.now() + timezone.timedelta(days=7)
    lead.save()
    context = {
        "lead": lead,
        "message": "We are following up with you as you're identified as a cold lead."
    }
    send_email("Occasional Follow-Up", lead.customeremail, "emails/occasional_follow_up.html", context)

def send_feedback_request(lead):
    context = {
        "lead": lead,
        "message": "We noticed that your recent order was not completed. Please provide feedback."
    }
    send_email("We Value Your Feedback", lead.customeremail, "emails/feedback_request.html", context)

def send_thank_you(lead):
    context = {
        "lead": lead,
        "message": "Thank you for your interest. Let us know if you change your mind!"
    }
    send_email("Thank You", lead.customeremail, "emails/thank_you.html", context)

