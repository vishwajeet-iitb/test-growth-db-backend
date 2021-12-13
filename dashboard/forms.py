from django import forms


class CheckProposal(forms.Form):
    proposal_num = forms.CharField(label="Proposal",max_length=255)

class ImageQuery(forms.Form):
    tar_ra = forms.FloatField(label="Target RA", required=False)
    tar_dec = forms.FloatField(label="Target Dec", required=False)
    tar_name = forms.CharField(label="Target",max_length=20,required=False)
    filter_used = forms.CharField(label="Filter Used",max_length=20,required=False) 
