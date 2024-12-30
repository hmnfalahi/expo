from django import forms
from django.contrib.auth.models import User
from ..models import Group


class GroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        help_text="Enter a name for your group"
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Enter a description for your group"
    )

    class Meta:
        model = Group
        fields = ['name', 'description']
