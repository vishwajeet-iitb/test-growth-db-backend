from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth import login,authenticate
from .forms import RegisterForm

# Create your views here.
def register(response):
    form = RegisterForm(response.POST or None)
    if response.method == 'POST':
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(response, user)
            return HttpResponseRedirect("/home")
        else:
            form = RegisterForm()

    return render(response,'userlogin/register.html',{"form":form})
        
