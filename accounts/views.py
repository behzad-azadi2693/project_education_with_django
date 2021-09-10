from accounts.forms import UserRegister, UserLogin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your views here.
from .models import User
from .token import send_token, account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode


def signup(request):
    #if request.user.is_authenticated:
    #    return redirect('education:index')

    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(email=cd['email']).first()

            if not user:
                user = User.objects.create_user(email=cd['email'],password=cd['password'])
                user.is_active = False
                user.save()
                send_token(user, request)
                messages.success(request, 'user registred please check email and click your link for activation email','success')
                return redirect('accounts:login')

            elif not user.email_check:
                user.password = cd['password']
                user.is_active= False
                user.save()
                send_token(user, request)
                messages.success(request,_('user register please check email and click your link for activation email'),'success')
                return redirect('accounts:login')

            else:
                messages.success(request, 'email or password is wrong ','success')
                return redirect('accounts:signup')


        else:
            context = {
                'form_register': UserRegister(request.POST),
            }
            return render(request, 'login.html', context)

    else:
        context = {
            'form_register': UserRegister(),
        }
        return render(request, 'login.html', context)


def logining(request):
    #if request.user.is_authenticated:
    #    return redirect('education:index')

    if request.method == 'POST':
        form = UserLogin(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = get_user_model().objects.get(email=cd['email'])
                if user.email_check:
                    user_is =  authenticate(request, email = cd['email'], password=cd['password'])
                    login(request, user)

                    return redirect('education:index')

                else:
                    send_token(user, request)
                    messages.success(request, _('please check email and click your link for activation email'),'success')
                    return redirect('accounts:login')

            except get_user_model().DoesNotExist:
                messages.success(request, _('please first register in site'),'success')
                return redirect('accounts:signup')
        else:
            context = {
                'form_login': UserLogin(request.POST),
            }
            messages.error(request, 'email or password confirm email not True', 'warning')
            return render(request, 'login.html', context)
    else:
        context = {
            'form_login': UserLogin(),
        }
        return render(request, 'login.html', context)


@login_required
def logoutg(request):
    logout(request)
    messages.success(request, 'شما از سایت خارج شدید', 'success')
    return redirect('education:login')


def activate_account(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_check = True
        user.save()
        messages.success(request, _('Your email account activate please login with email and password'), 'success')
        return redirect('accounts:login')
    else:
        messages.warning(request, _('The confirmation link was invalid, possibly because it has already been used.'),'error')
        return redirect('home')