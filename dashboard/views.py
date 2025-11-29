# from django.shortcuts import render

# # Create your views here.
# # dashboard/views.py

# from django.shortcuts import render
# from crmapp.models import lead_management
# from django.db.models import Count

# def dashboard_view(request):
#     # Query all leads and count each type
#     lead_counts = lead_management.objects.values('typeoflead').annotate(count=Count('typeoflead'))

#     # Prepare data for pie chart
#     labels = [entry['typeoflead'] for entry in lead_counts]
#     data = [entry['count'] for entry in lead_counts]

#     # Key metrics
#     total_leads = lead_management.objects.count()
#     hot_leads = lead_management.objects.filter(typeoflead='Hot').count()
#     warm_leads = lead_management.objects.filter(typeoflead='Warm').count()
#     cold_leads = lead_management.objects.filter(typeoflead='Cold').count()
#     not_interested = lead_management.objects.filter(typeoflead='Not Interested').count()
#     loss_of_order = lead_management.objects.filter(typeoflead='Loss of Order').count()

#     context = {
#         'labels': labels,
#         'data': data,
#         'total_leads': total_leads,
#         'hot_leads': hot_leads,
#         'warm_leads': warm_leads,
#         'cold_leads': cold_leads,
#         'not_interested': not_interested,
#         'loss_of_order': loss_of_order,
#     }

#     return render(request, 'dashboard/dashboard.html', context)



# dashboard/views.py
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from crmapp.models import lead_management

def dashboard_view(request):
    # Fetch lead counts by type
    total_leads = lead_management.objects.count()
    hot_leads = lead_management.objects.filter(typeoflead='Hot').count()
    warm_leads = lead_management.objects.filter(typeoflead='Warm').count()
    cold_leads = lead_management.objects.filter(typeoflead='Cold').count()
    not_interested = lead_management.objects.filter(typeoflead='NotInterested').count()
    loss_of_order = lead_management.objects.filter(typeoflead='LossOfOrder').count()

    # Prepare data for the pie chart
    lead_data = [hot_leads, warm_leads, cold_leads, not_interested, loss_of_order]
    labels = ["Hot Leads", "Warm Leads", "Cold Leads", "Not Interested", "Loss of Order"]

    # Create the pie chart using matplotlib
    fig, ax = plt.subplots()
    ax.pie(lead_data, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the figure to a BytesIO object to convert it into an image for the web
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert the image to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Prepare context
    context = {
        'total_leads': total_leads,
        'hot_leads': hot_leads,
        'warm_leads': warm_leads,
        'cold_leads': cold_leads,
        'not_interested': not_interested,
        'loss_of_order': loss_of_order,
        'chart': image_base64  # Send the chart as a base64 string to the template
    }

    return render(request, 'dashboard/dashboard.html', context)


# for displaying calender 

# from django.shortcuts import render
# from django.http import JsonResponse
# from schedule_meetings.models import Meeting

# def calendar_view(request):
#     return render(request, 'dashboard/calender.html')

# def get_meetings(request):
#     meetings = Meeting.objects.all()
#     print("meetings", meetings)
#     events = [
#         {
#             "title": meeting.title,
#             "start": meeting.start_time.isoformat(),
#             "end": meeting.end_time.isoformat(),
#             "description": meeting.objective,
#         }
#         for meeting in meetings
#     ]
#     return JsonResponse(events, safe=False)




#  calendar try 

# dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from schedule_meetings.models import Meeting

# def calendar_view(request):
#     return render(request, 'dashboard/dashboard.html')

def meeting_data(request):
    # Fetch all meetings
    print("heloooooooooooooooooooooooooo")
    meetings = Meeting.objects.all()
    events = []
    for meeting in meetings:
        # Calculate end time as 1 hour after start time
        start_datetime = datetime.datetime.combine(meeting.meeting_date, meeting.meeting_time)
        end_datetime = start_datetime + datetime.timedelta(hours=1)
        print("stratdate", start_datetime)
        print("enddatetiem", end_datetime)
        events.append({
            'title': f"{meeting.meeting_agenda}",
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'description': f"Agenda: {meeting.meeting_agenda}, Participants: {meeting.participants}"
        })
    return JsonResponse(events, safe=False)
