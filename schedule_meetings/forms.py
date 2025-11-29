# from django import forms
# from .models import Meeting
# import requests
# from crm import settings
# from crmapp.models import customer_details
# from django.forms.widgets import SelectDateWidget, TimeInput  # Import widgets for date and time

# class ScheduleMeetingForm(forms.ModelForm):

#     event_type = forms.ChoiceField(choices=[], label='Select Event Type')  # Dropdown for event types

#     class Meta:
#         model = Meeting
#         fields = ['customer', 'scheduled_date', 'scheduled_time','event_type']

#     # Customize fields with separate date and time widgets
#     scheduled_date = forms.DateField(widget=SelectDateWidget(), label='Meeting Date')
#     scheduled_time = forms.TimeField(widget=TimeInput(format='%H:%M'), label='Meeting Time')

#     customer = forms.ModelChoiceField(
#         queryset=customer_details.objects.all(),
#         widget=forms.Select,
#         label='Customer',
#         required=True
#     )

#     def __init__(self, *args, **kwargs):
#         super(ScheduleMeetingForm, self).__init__(*args, **kwargs)
#         self.fields['event_type'].choices = self.get_calendly_event_choices()

#     def get_calendly_event_choices(self):
#         import http.client

#         conn = http.client.HTTPSConnection("api.calendly.com")

#         headers = {
#             'Authorization': f'Bearer {settings.CALENDLY_API_TOKEN}',
#             'Content-Type': 'application/json'
#         }
#         response = requests.get('https://api.calendly.com/event_types/uuid', headers=headers)
        
#         choices = []
#         if response.status_code == 200:
#             event_types = response.json()
#             choices = [(event['uri'], event['name']) for event in event_types['collection']]
        
#         return choices if choices else [('','No events available')]


# from django import forms
# from .models import Meeting
# import requests
# import http.client
# from crm import settings
# from crmapp.models import customer_details
# from django.forms.widgets import SelectDateWidget, TimeInput  # Import widgets for date and time
# import logging  # For logging the API response
# import json  # For parsing JSON data
# import requests  # For making API requests

# # Set up logging
# logger = logging.getLogger(__name__)

# class ScheduleMeetingForm(forms.ModelForm):

#     event_type = forms.ChoiceField(choices=[], label='Select Event Type')  # Dropdown for event types

#     class Meta:
#         model = Meeting
#         fields = ['customer', 'scheduled_date', 'scheduled_time', 'event_type']

#     # Customize fields with separate date and time widgets
#     scheduled_date = forms.DateField(widget=SelectDateWidget(), label='Meeting Date')
#     scheduled_time = forms.TimeField(widget=TimeInput(format='%H:%M'), label='Meeting Time')

#     customer = forms.ModelChoiceField(
#         queryset=customer_details.objects.all(),
#         widget=forms.Select,
#         label='Customer',
#         required=True
#     )

#     def __init__(self, *args, **kwargs):
#         super(ScheduleMeetingForm, self).__init__(*args, **kwargs)
#         self.fields['event_type'].choices = self.get_calendly_event_choices()

#     def get_calendly_event_choices(self):
#         user_id = settings.CALENDLY_USER_ID

#         headers = {
#             'Authorization': f'Bearer {settings.CALENDLY_API_TOKEN}',
#             'Content-Type': 'application/json'
#         }
#         response = requests.get('https://api.calendly.com/event_types?user={user_id}', headers=headers)
        
#         choices = []
#         if response.status_code == 200:
#             event_types = response.json()

#             # Log or print the response to see if the data is correct
#             logger.debug(f"Calendly API Response: {event_types}")
            
#             if 'collection' in event_types:
#                 choices = [(event['uri'], event['name']) for event in event_types['collection']]
#             else:
#                 logger.error(f"No 'collection' found in the Calendly API response: {event_types}")
        
#         else:
#             logger.error(f"Failed to fetch Calendly events. Status Code: {response.status_code}. Response: {response.text}")
        
#         return choices if choices else [('', 'No events available')]

    # def get_calendly_event_choices(self):
    #     conn = http.client.HTTPSConnection("api.calendly.com")

    #     # Retrieve user ID or organization ID from settings or hard-code it if necessary
    #     user_id = settings.CALENDLY_USER_ID  # Set this in your settings.py

    #     headers = {
    #         'Authorization': f'Bearer {settings.CALENDLY_API_TOKEN}',
    #         'Content-Type': 'application/json'
    #     }

    #     # Adjust the endpoint to include the user_id parameter if necessary
    #     conn.request("GET", f"/event_types?user={user_id}", headers=headers)

    #     response = conn.getresponse()

    #     if response.status == 200:  # Using `status` instead of `status_code`
    #         data = response.read()
    #         event_types = json.loads(data)

    #         choices = [(event['uri'], event['name']) for event in event_types.get('collection', [])]
    #     else:
    #         print(f"Failed to fetch Calendly events. Status Code: {response.status}. Response: {response.read().decode()}")
    #         choices = []

    #     return choices if choices else [('', 'No events available')]


import requests
from django import forms
from django.forms.widgets import SelectDateWidget, TimeInput
from .models import Meeting
from crmapp.models import customer_details
from django.conf import settings
from datetime import time
from django.forms.widgets import DateInput

class ScheduleMeetingForm(forms.ModelForm):
    event_type = forms.ChoiceField(choices=[], label='Select Event Type')

    class Meta:
        model = Meeting
        fields = ['customer', 'event_type']

    # Customize fields with separate date and time widgets
    # Customize the scheduled_date with a DateInput (calendar)
    scheduled_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),  # Calendar widget
        label='Meeting Date'
    )

    # Customize the scheduled_time with a dropdown of time slots
    TIME_SLOTS = [
        (time(hour=9, minute=0), '9:00 AM'),
        (time(hour=9, minute=30), '9:30 AM'),
        (time(hour=10, minute=0), '10:00 AM'),
        (time(hour=10, minute=30), '10:30 AM'),
        (time(hour=11, minute=0), '11:00 AM'),
        (time(hour=11, minute=30), '11:30 AM'),
        (time(hour=12, minute=0), '12:00 PM'),
        (time(hour=12, minute=30), '12:30 PM'),
        (time(hour=13, minute=0), '1:00 PM'),
        (time(hour=13, minute=30), '1:30 PM'),
        (time(hour=14, minute=0), '2:00 PM'),
        (time(hour=14, minute=30), '2:30 PM'),
        (time(hour=15, minute=0), '3:00 PM'),
        (time(hour=15, minute=30), '3:30 PM'),
        (time(hour=16, minute=0), '4:00 PM'),
        (time(hour=16, minute=30), '4:30 PM'),
        (time(hour=17, minute=0), '5:00 PM'),
    ]
    
    scheduled_time = forms.ChoiceField(
        choices=TIME_SLOTS,  # Dropdown for time slots
        label='Meeting Time'
    )

    customer = forms.ModelChoiceField(
        queryset=customer_details.objects.all(),
        widget=forms.Select,
        label='Customer',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(ScheduleMeetingForm, self).__init__(*args, **kwargs)
        self.fields['event_type'].choices = self.get_calendly_event_choices()

    def get_user_id(self):
        """Fetch the user ID from Calendly API."""
        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        user_response = requests.get('https://api.calendly.com/users/me', headers=headers)

        if user_response.status_code == 200:
            user_data = user_response.json()
            return user_data['resource']['uri']  # Get the user's Calendly ID (URI)
        else:
            print(f"Failed to fetch Calendly user. Status Code: {user_response.status_code}. Response: {user_response.text}")
            return None

    def get_calendly_event_choices(self):
        """Fetch available event types for the user."""
        user_id = self.get_user_id()

        if not user_id:
            return [('', 'No events available')]

        headers = {
            'Authorization': f'Bearer {settings.CALENDLY_API_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Fetch event types for the user
        response = requests.get(f'https://api.calendly.com/event_types?user={user_id}', headers=headers)

        choices = []
        if response.status_code == 200:
            event_types = response.json()
            # print("uhniun",event_types)
            choices = [(event['uri'], event['name']) for event in event_types['collection']]
        else:
            print(f"Failed to fetch Calendly events. Status Code: {response.status_code}. Response: {response.text}")

        return choices if choices else [('', 'No events available')]



