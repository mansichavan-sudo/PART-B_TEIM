# signals.py
import requests
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver, Signal
from django.db import transaction
from django.contrib.auth.models import User
from django.apps import apps

# ✅ Safe model access (prevents "model already registered" warning)
UserProfile = apps.get_model('crmapp', 'UserProfile')
TechWorkList = apps.get_model('crmapp', 'TechWorkList')
TechnicianProfile = apps.get_model('crmapp', 'TechnicianProfile')
service_management = apps.get_model('crmapp', 'service_management')
WorkAllocation = apps.get_model('crmapp', 'WorkAllocation')
MessageTemplates = apps.get_model('crmapp', 'MessageTemplates')

from crmapp.tasks import send_email_task, send_whatsapp_task


# ------------------- User Profile Creation -------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ------------------- TechWorkList Notification -------------------
@receiver(post_save, sender=TechWorkList)
def mark_new_work_as_notification(sender, instance, created, **kwargs):
    if created:
        instance.is_notified = True
        instance.save(update_fields=['is_notified'])


# ------------------- Custom Signal -------------------
service_scheduled = Signal()


# ------------------- Work Allocation Post-Save -------------------
@receiver(post_save, sender=WorkAllocation)
def notify_customer_on_workallocation(sender, instance, created, **kwargs):
    """Trigger notification only when a WorkAllocation is created."""
    if not created:
        return
    print(f"WorkAllocation {instance.id} created. Waiting for technicians...")


# ------------------- Technician Assignment (M2M) -------------------
@receiver(m2m_changed, sender=WorkAllocation.technician.through)
def workallocation_technicians_changed(sender, instance, action, pk_set, **kwargs):
    """Trigger notification after technicians are assigned."""
    if action != "post_add" or not pk_set:
        return

    service = instance.service
    if not service or not service.customer_id:
        return

    print(f"Technicians assigned to WorkAllocation {instance.id}: {pk_set}")

    transaction.on_commit(lambda: service_scheduled.send(
        sender=WorkAllocation,
        service_id=service.id,
        created=True
    ))


# ------------------- Notification Handler -------------------
@receiver(service_scheduled)
def send_service_scheduled_email(sender, service_id, created, **kwargs):
    """Send Email + WhatsApp notifications to the customer."""
    service = service_management.objects.get(id=service_id)
    customer = getattr(service, "customer", None)
    if not customer:
        return

    # ------------------- Technician Info -------------------
    work = WorkAllocation.objects.filter(service=service_id).order_by("-id").first()
    if work and work.technician.exists():
        tech_list = [
            f"{t.first_name} {t.last_name} - {t.contact_number}"
            for t in work.technician.all()
        ]
        tech_details = ", ".join(tech_list)
    else:
        tech_details = "Not Assigned"

    placeholders = {
        "customer_name": customer.fullname,
        "service_date": service.service_date.strftime("%d-%m-%Y"),
        "delivery_time": service.delivery_time.strftime("%I:%M %p"),
        "selected_service": service.service_subject,
        "tech_details": tech_details,
    }

    # ------------------- Email -------------------
    if customer.primaryemail:
        email_template = MessageTemplates.objects.filter(
            message_type="email", category="service"
        ).first()
        if email_template:
            email_body = email_template.body
            for key, value in placeholders.items():
                email_body = email_body.replace(f"{{{key}}}", str(value))

            subject = (
                "Service Appointment Confirmation – Seva Facility Services"
                if created else
                "Service Appointment Updated – Seva Facility Services"
            )

            send_email_task.delay(
                subject,
                email_body,
                recipient=customer.primaryemail,
                attachment_path=None,
                attachment_name=None,
            )
            print("📧 Email queued for:", customer.primaryemail)

    # ------------------- WhatsApp -------------------
    if customer.primarycontact:
        whatsapp_template = MessageTemplates.objects.filter(
            message_type="whatsapp", category="service"
        ).first()
        if whatsapp_template:
            whatsapp_body = whatsapp_template.body
            for key, value in placeholders.items():
                whatsapp_body = whatsapp_body.replace(f"{{{key}}}", str(value))

            mobile = f"91{customer.primarycontact}"
            send_whatsapp_task.delay(mobile, whatsapp_body)
            print("📲 WhatsApp queued for:", mobile)
