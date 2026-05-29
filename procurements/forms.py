from django import forms
from .models import Procurement, Agency


class ProcurementForm(forms.ModelForm):
    class Meta:
        model = Procurement
        fields = [
            'reference_number', 'title', 'description',
            'agency', 'category', 'status',
            'approved_budget', 'bid_open_date',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'bid_open_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'approved_budget': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.bid_open_date:
            self.initial['bid_open_date'] = (
                self.instance.bid_open_date.strftime('%Y-%m-%dT%H:%M')
            )
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['agency'].widget.attrs['class'] = 'form-select'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['status'].widget.attrs['class'] = 'form-select'


class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ['name', 'department', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')