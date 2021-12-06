from django import forms


class CheckProposal(forms.Form):
    proposal_num = forms.CharField(label="Proposal",max_length=255)

class ImageQuery(forms.Form):
    ra = forms.FloatField(label="Target RA")
    dec = forms.FloatField(label="Target Dec")
    date = forms.DateField(label="Date of Observation")
    filter_used = forms.CharField(label="Filter Used",max_length=20) 
