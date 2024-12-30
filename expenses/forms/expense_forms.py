from django import forms
from django.utils import timezone
from ..models import Expense


class ExpenseForm(forms.ModelForm):
    split_with = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select who to split this expense with"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="When was this expense incurred?",
        initial=timezone.now().date()
    )

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'split_with', 'date']

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if session:
            self.fields['split_with'].queryset = session.members.all()
            # Set all session members as default
            self.fields['split_with'].initial = session.members.all()

    def clean_date(self):
        date = self.cleaned_data['date']
        return date.strftime('%Y-%m-%d') if date else None