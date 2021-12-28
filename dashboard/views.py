from datetime import date
import datetime
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, request
from django.contrib.auth.decorators import login_required
from numpy import string_

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
            keys = ['tar_ra','tar_dec','tar_name','filter_used','proposal_no']
            
            kwargs = {}
            for key in keys:
                if form.cleaned_data[key] != '' and form.cleaned_data[key] != None :
                    kwargs[key] = form.cleaned_data[key]

            queriedImages = Image.objects.filter(**kwargs).values()
            print(form.cleaned_data['end_date'])
            if form.cleaned_data['start_date'] !=None and form.cleaned_data['end_date']!=None:
                start_date = datetime.datetime.combine(form.cleaned_data['start_date'],datetime.time(8,0))
                end_date = datetime.datetime.combine(form.cleaned_data['end_date'],datetime.time(8,0))
                queriedImages = queriedImages.filter(date_observed__gte=start_date,
                                                    date_observed__lte=end_date)
            print(len(queriedImages))
            i = 0
            result = []
            for image in queriedImages:
                allowAccess = Proposal.objects.filter(user=response.user,heading=image['proposal_no'])
                if allowAccess or response.user.is_superuser:
                    i=i+1
                    result.append(image)
                    
            
            msg = "Found %s & displaying %s"%(len(queriedImages),i)
            showcols = response.POST.getlist('checks[]')
            showcols = [i[1:] for i in showcols]

            return render(response,"dashboard/result.html",{'data':result,"txt":msg, 
            'colmn':list(Image.headers.keys()),'showcols':showcols})
                
        else:
            return HttpResponseRedirect("/query")
    else:
        form = ImageQuery()
    return render(response,'dashboard/nightly.html',{"form":form,'colmn':list(Image.headers.keys())})
