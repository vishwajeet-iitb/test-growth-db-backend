from django import forms


class CheckProposal(forms.Form):
    proposal_num = forms.CharField(label="Proposal",max_length=255)