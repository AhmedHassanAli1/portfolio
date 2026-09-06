from django.shortcuts import render
#from authuser.auth_backends import authenticate
from django.contrib.auth import login ,authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
import time
# Create your views here.


def login_view(request):
    if request.method == "POST":
        
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            autenticate_user = authenticate(request, 
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password'])
            
            if autenticate_user :
                login(request, autenticate_user)
                request.session['login_time'] = time.time()
                if autenticate_user.role == 3:
                    return redirect('/')
                   
                return redirect('/staffuser')
                
        else :
            messages.error(request, 'Username or password is incorrect')
    else:
        form = AuthenticationForm()
            
            



    return render(request, 'login/login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/login/')

