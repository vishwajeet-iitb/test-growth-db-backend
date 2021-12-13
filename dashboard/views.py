from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from numpy import string_

from dashboard.models import Image, Proposal
from .forms import CheckProposal, ImageQuery

import os
import astropy.io.fits
import astropy.stats
from matplotlib import pyplot as plt
import io
import urllib, base64
import math

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
            keys = ['tar_ra','tar_dec','tar_name','filter_used']
            
            kwargs = {}
            for key in keys:
                if form.cleaned_data[key] != '' and form.cleaned_data[key] != None :
                    kwargs[key] = form.cleaned_data[key]

            print(kwargs)
            queriedImages = Image.objects.filter(**kwargs)
            print(len(queriedImages))
            
            fig = plt.figure(figsize=(7, 7))
            col = 2
            row = math.ceil(len(queriedImages)/2)
            i = 1;
            plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.7, 
                    hspace=0.4)
            for image in queriedImages:
                allowAccess = Proposal.objects.filter(user=response.user,heading=image.proposal_no)
                if allowAccess or response.user.is_superuser:
                    fits = astropy.io.fits.open(os.path.join(image.filepath))
                    mean, median, std = astropy.stats.sigma_clipped_stats(fits[0].data)
                    fig.add_subplot(row,col,i)
                    plt.imshow(fits[0].data, vmin=mean-std, vmax=mean+3*std, cmap='binary')
                    plt.title(os.path.basename(image.filepath))
                    i+=1
            
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf,format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read())
            uri = urllib.parse.quote(string)
            return render(response,"dashboard/result.html",{'data':uri})
                
        else:
            return HttpResponseRedirect("/query")
    else:
        form = ImageQuery()
    return render(response,'dashboard/nightly.html',{"form":form})