from django import forms
from .models import VisitingCard

class VisitingCardForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = VisitingCard
        fields = ['file']
