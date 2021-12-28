from django import forms
from dashboard.models import Image

class CheckProposal(forms.Form):
    proposal_num = forms.CharField(label="Proposal",max_length=255)

class ImageQuery(forms.Form):
    tar_ra = forms.FloatField(label="Target RA", required=False)
    tar_dec = forms.FloatField(label="Target Dec", required=False)
    tar_name = forms.CharField(label="Target",max_length=20,required=False)
    filter_used = forms.CharField(label="Filter Used",max_length=20,required=False) 
    proposal_no = forms.CharField(label="Proposal Number",max_length=20,required=False)
    start_date = forms.DateField(label="From (inclusive)",required=False)
    end_date = forms.DateField(label="To (inclusive)",required=False)
    
