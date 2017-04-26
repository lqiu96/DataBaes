from django import forms

from Crate.models import Discussion
from user_profile.models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report']


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['comment']
