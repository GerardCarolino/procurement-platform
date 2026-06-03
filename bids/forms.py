from django import forms
from .models import Bid


class BidSubmissionForm(forms.ModelForm):
    # Honeypot — hidden from real users, bots fill it in
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex':     '-1',
        })
    )

    class Meta:
        model  = Bid
        fields = ('bid_amount', 'technical_proposal', 'supporting_document')
        widgets = {
            'technical_proposal': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        self.procurement = kwargs.pop('procurement', None)
        self.user        = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_website(self):
        """Honeypot check — real users leave this blank. Bots fill it in."""
        value = self.cleaned_data.get('website', '')
        if value:
            raise forms.ValidationError('Bot detected.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        if self.procurement and self.user:
            if Bid.objects.filter(
                procurement=self.procurement,
                submitted_by=self.user
            ).exists():
                raise forms.ValidationError(
                    'You have already submitted a bid for this procurement.'
                )
        return cleaned_data


# ── NEW ──────────────────────────────────────────────────────────────────────
class BidEditForm(forms.ModelForm):
    """Allows vendors to update bid amount, proposal, and document before opening."""

    class Meta:
        model  = Bid
        fields = ('bid_amount', 'technical_proposal', 'supporting_document')
        widgets = {
            'technical_proposal': forms.Textarea(attrs={'rows': 6}),
        }