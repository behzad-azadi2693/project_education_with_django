from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.




def signup(request):
    pass


def logining(request):
   pass

@login_required
def logoutg(request):
    logout(request)
    messages.success(request, 'شما از سایت خارج شدید', 'success')
    return redirect('education:login')
