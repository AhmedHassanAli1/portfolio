from Publication.models import Publication_Event, Publication_News
from django import forms

class ApprovalNewsForm(forms.ModelForm):
    CHOICES = [(True, 'Approve'), (False, 'Reject')]
    is_approved = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label='Approval Status')
    reject_text = forms.CharField(required=False,widget=forms.Textarea(attrs={'placeholder': 'Reason for rejection', 'disabled': 'true'}))
    class Meta:
        model = Publication_News
        fields = ['is_approved']

class ApprovalEventForm(forms.ModelForm):
    CHOICES = [(True, 'Approve'), (False, 'Reject')]
    is_approved = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label='Approval Status')
    reject_text = forms.CharField(required=False,widget=forms.Textarea(attrs={'placeholder': 'Reason for rejection', 'disabled': 'true'}))
    class Meta:
        model = Publication_Event
        fields = ['is_approved']