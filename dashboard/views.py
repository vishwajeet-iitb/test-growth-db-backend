from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect

from dashboard.models import Proposal
from .forms import CheckProposal

# Create your views here.
def index(response):
    return render(response,"dashboard/dash.html",{'message':'Welcome'})

def check(response):
    if response.user.is_authenticated:
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
    else:
        return redirect('/login')