from datetime import datetime
from django import forms
from .models import Publication_Event, Publication_News, RecurringEvent
from django.contrib.postgres.forms import SimpleArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from array import array

class MultiWidgetBasic(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices),
            forms.Select(choices=RecurringEvent.Byday.choices)
            ]
        super(MultiWidgetBasic, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        else:
            return ['', '']

class MultiExampleField(forms.fields.MultiValueField):
    widget = MultiWidgetBasic

    def __init__(self, *args, **kwargs):
        list_fields = [
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices),
            forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices)
            ]
        super(MultiExampleField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        ## compress list to single object                                               
        ## eg. date() >> u'31/12/2012'                                                  
        return values

class BydayForm(forms.Form):
    BYDAY_OPTIONS = (
        ("0", "-"),
        ("1","Monday"),
        ("2","Tuesday"),
        ("3","Wednesday"),
        ("4","Thursday"),
        ("5","Friday"),
        ("6","Saturday"),
        ("7", "Sunday")
    )
    byday = forms.fields.ChoiceField(choices=RecurringEvent.Byday.choices,required=False)
    day = forms.ChoiceField(choices=BYDAY_OPTIONS,required=False)

class RecurringEventForm(forms.Form):
    freq = forms.ChoiceField(choices=RecurringEvent.Freq.choices,required=False)
    interval = forms.IntegerField(initial=1,validators=[MinValueValidator(1)],required=False)
    bymonth = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=RecurringEvent.Month.choices,
        required=False
    )
    month_select = (
        ("1","Each"),
        ("2","On the...")
    )
    month_select = forms.ChoiceField(choices=month_select,required=False)
    bymonthday = SimpleArrayField(forms.IntegerField(
        validators=[MaxValueValidator(31),MinValueValidator(-30)],

        ),required=False)
    byyearday = SimpleArrayField(forms.IntegerField(
        validators=[MaxValueValidator(365),MinValueValidator(-30)]
    ),required=False)
    year_select = (
        ("1","Yeardays"),
        ("2","Months")
    )
    year_select = forms.ChoiceField(choices=year_select,required=False)
    year_month_usebyday = forms.BooleanField(widget=forms.CheckboxInput,required=False)
    byweekno = SimpleArrayField(forms.IntegerField(
        validators=[MaxValueValidator(53),MinValueValidator(-52)]
        
    ),required=False)
    byweekday = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=RecurringEvent.Weekday.choices,
        required=False
    )
    #weekday_byday = MultiExampleField()

    END_RECURRENCE_CHOICES = (
        ("1", "Never"),
        ("2", "After x events"),
        ("3", "Until date")
    )
    end_recurrence = forms.ChoiceField(choices=END_RECURRENCE_CHOICES,required=False)
    count = forms.IntegerField(required=False)
    until = forms.DateField(widget=forms.SelectDateWidget,required=False)
    
    """
    class Meta:
        model = RecurringEvent
        fields = [
            'freq',
            'interval',
            'count',
            'until',
            'bymonth',
            'bymonthday',
            'byyearday',
            'byweekno',
            #'byweekday',
        ]
        """