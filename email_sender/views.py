# # from .models import lead_management
# # from django.utils import timezone
# # from .tasks import send_hot_lead_email, send_warm_lead_email, send_cold_lead_email, send_not_interested_email, send_loss_of_order_email

# # def schedule_emails_for_leads():
# #     leads = lead_management.objects.all()
# #     current_time = timezone.now()

# #     for lead in leads:
# #         if lead.next_email_date and lead.next_email_date <= current_time:
# #             if lead.typeoflead == 'Hot':
# #                 send_hot_lead_email.delay(lead.id)
# #             elif lead.typeoflead == 'Warm':
# #                 send_warm_lead_email.delay(lead.id)
# #             elif lead.typeoflead == 'Cold':
# #                 send_cold_lead_email.delay(lead.id)
# #             elif lead.typeoflead == 'Not Interested':
# #                 send_not_interested_email.delay(lead.id)
# #             elif lead.typeoflead == 'Loss of Order':
# #                 send_loss_of_order_email.delay(lead.id)
                
# #             # Update next_email_date for further scheduling
# #             lead.update_next_email_date(current_time)





# # ////
# # from django.shortcuts import render
# # from django.shortcuts import HttpResponse
# # from .tasks import send_mail_func

# # def send_mail_to_all(request):
# #     send_mail_func.delay()
# #     return HttpResponse("Sent")




# # //1st try
# from django.shortcuts import render, HttpResponse
# from .tasks import send_immediate_email
# from crmapp.models import lead_management

# def send_mail_to_all(request):
#     all_leads = lead_management.objects.all()

#     for lead in all_leads:
#         send_immediate_email.delay(lead.id)

#     return HttpResponse("Emails sent for all leads.")
