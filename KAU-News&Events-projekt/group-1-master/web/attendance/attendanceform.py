from django import forms
from .models import EventAttendance

class EventAttendanceForm(forms.ModelForm):
    class Meta:
        model = EventAttendance
        fields = ['allergies', 'dietary_preferences', 'notes']
        labels = {
            'allergies': 'Allergier',
            'dietary_preferences': 'Kostpreferenser',
            'notes': 'Övrigt / Kommentarer'
        }
        widgets = {'notes': forms.Textarea(attrs={'rows':3})}
