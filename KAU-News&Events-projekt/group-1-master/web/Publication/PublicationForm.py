from datetime import datetime
from django import forms
from .models import Publication_Event, Publication_News
from authuser.models import Department, Tag
from django.utils import timezone

def get_hour_choices():
    TimeChoices = []
    for hour in range(24):
        for minute in range(0,60,15):
            # Format the time as HH
            time = f"{hour:02d}:{minute:02d}"
            # add a tuple (value,lable) to the list
            TimeChoices.append((time,time))
    return TimeChoices


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    required=False

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class PublicationEventForm(forms.ModelForm):
    EventTitle = forms.CharField(label='Title', max_length=200)
    Author = forms.CharField(label='Author', max_length=100)
    Username = forms.CharField(label='Username', max_length=100)
    Organization = forms.CharField(label='Organization', max_length=100)
    Email = forms.EmailField(label='Email')
    EventLocation = forms.CharField(label='Location', max_length=200)
    EventDesc = forms.CharField(label='Description', widget=forms.Textarea)
    EventStartDate = forms.DateField(label='Event Start Date', widget=forms.SelectDateWidget)
    EventStartTime = forms.TimeField(label='Event Start Time', widget=forms.Select(choices=get_hour_choices()))  
    EventEndDate = forms.DateField(label='Event End Date', widget=forms.SelectDateWidget)
    EventEndTime = forms.TimeField(label='Event End Time', widget=forms.Select(choices=get_hour_choices()))  
    Tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)
    Department = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), widget=forms.CheckboxSelectMultiple)
    is_recurring = forms.BooleanField(widget=forms.CheckboxInput,required=False)
    class Meta:
        model = Publication_Event
        fields = [
            'EventTitle', 
            'Author',  
            'Username',
            'Organization', 
            'Email', 
            'EventLocation', 
            'EventDesc', 
            'EventStartDate', 
            'EventStartTime', 
            'EventEndDate', 
            'EventEndTime', 
            'Department', 
            'Tag',
            'is_recurring'
        ]

class MultipleFilesForm(forms.Form):
    files = MultipleFileField(required=False);

class PublicationNewsForm(forms.ModelForm):
    NewsTitle = forms.CharField(label='Title', max_length=200)
    Author = forms.CharField(label='NewsAuthor', max_length=100)
    Organization = forms.CharField(label='Organization', max_length=100)
    Email = forms.EmailField(label='Email')
    NewsDesc = forms.CharField(label='Description', widget=forms.Textarea)
    Tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)
    Department = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Publication_News
        fields = [
            'Author',
            'NewsTitle',  
            'Organization', 
            'Email', 
            'NewsDesc',  
            'Department', 
            'Tag'
        ]
