from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from dashboard.models import Image, Proposal
from .forms import CheckProposal, ImageQuery

# Create your views here.
def index(response):
    return render(response,"dashboard/dash.html",{'message':'Welcome'})

@login_required(login_url='/login')
def check(response):
    if response.method =="POST":
        form = CheckProposal(response.POST)
        if form.is_valid():
            h = form.cleaned_data["proposal_num"]
            ProposalList = Proposal.objects.filter(user=response.user,heading=h)
            if not ProposalList:
                return render(response,"dashboard/dash.html",{'message':'you don\'t have access'})
            else:
                return render(response,"dashboard/dash.html",{'message':'you have access'})
        else:
            return HttpResponseRedirect("/check")

    else:
        form = CheckProposal()
    return render(response,'dashboard/nightly.html',{"form":form})

@login_required(login_url='/login')
def query(response):
    if response.method =="POST":
        form = ImageQuery(response.POST)
        if form.is_valid():
            ra = form.cleaned_data["ra"]
            dec = form.cleaned_data["dec"]
            date = form.cleaned_data["date"]
            filterUsed = form.cleaned_data["filter_used"]
            queriedImages = Image.objects.filter(tar_ra=ra,
                                                tar_dec=dec,
                                                filter_used=filterUsed,
                                                date_observed__year=date,
                                                date_observed__month=date,
                                                date_observed__day=date)
            
            for image in queriedImages:
                allowAccess = Proposal.objects.filter(user=response.user,heading=image.proposal_no)
                if allowAccess:
                    #show photo
                    pass
                
        else:
            return HttpResponseRedirect("/query")
    else:
        form = ImageQuery()
    return render(response,'dashboard/nightly.html',{"form":form})