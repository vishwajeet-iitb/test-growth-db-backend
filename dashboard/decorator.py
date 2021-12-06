from django.http import HttpResponse
from django.shortcuts import redirect

def require_authentication(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return view_func(request,*args,**kwargs)
        else:
            return redirect('/login')
    return wrapper_func


