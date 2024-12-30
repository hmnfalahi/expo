from django import forms
from django.contrib.auth.models import User
from ..models import Session
from ..services.balance_calculator import calculate_balances

class SessionForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        help_text="Enter a name for your session"
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Enter a description for your session"
    )
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select members to add to this session"
    )

    class Meta:
        model = Session
        fields = ['name', 'description', 'members']

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        user = kwargs.pop('user', None)
        super(SessionForm, self).__init__(*args, **kwargs)
        if group:
            self.fields['members'].queryset = group.members.all()
        if user:
            self.fields['members'].initial = [user]

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk and self.instance.ended:
            raise forms.ValidationError("Cannot update an ended session.")
        return cleaned_data

    def clean_members(self):
        members = self.cleaned_data.get('members')
        session = self.instance
        if session.pk:
            balances = calculate_balances(session)
            for member in session.members.all():
                if member not in members and balances.get(member, 0) != 0:
                    raise forms.ValidationError(f"Cannot remove member {member.username} with non-zero balance.")
        return members
