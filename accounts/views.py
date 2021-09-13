from accounts.forms import UserRegister, UserLogin, EmailForm, PasswordForm
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from .models import User, SessionUser
from .token import send_token, account_activation_token, send_email
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.sessions.models import Session
from datetime import date
from education.models import Course, Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def email_form(request):
    #if request.user.is_authenticated:
    #    return redirect('education:index')
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid:
            cd = request.POST
            user = get_user_model().objects.get(email=cd['email'])
            send_email(user, request)
            messages.success(request, _('please check your email'),'success')
            return redirect('accounts:email_form')
        else:
            form_email = EmailForm(request.POST)
            return render(request, 'login.html', {'form_email':form_email})
    else:
        form_email = EmailForm()
        return render(request, 'login.html', {'form_email':form_email})


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
                return redirect('accounts:signin')

            elif not user.email_check:
                password = cd['password']
                user.set_password(password)
                user.is_active= False
                user.save()
                send_token(user, request)
                messages.success(request,_('user register please check email and click your link for activation email'),'success')
                return redirect('accounts:signin')

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


def signin(request):
    #if request.user.is_authenticated:
    #    return redirect('education:index')

    if request.method == 'POST':
        form = UserLogin(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = get_user_model().objects.filter(email=cd['email']).first()
            if user:
                if user.email_check:
                    user_is =  authenticate(request, email = cd['email'], password=cd['password'])
                    if user_is:
                        login(request, user_is)
                        SessionUser.objects.get_or_create(
                                            user = user,
                                            session_key =Session.objects.get(session_key = request.session.session_key),
                                            device = f'{request.user_agent.browser.family}-{request.user_agent.browser.version_string}',
                                            os = f'{request.user_agent.os.family}-{request.user_agent.os.version_string}',
                                            date_joiin = date.today(),
                                            ip_device =request.META['REMOTE_ADDR'] ,
                                        )

                        return redirect('education:index')
                    else:
                        messages.success(request, _('email or password email not True'),'success')
                        return redirect('accounts:signin')
                else:
                    send_token(user, request)
                    messages.success(request, _('please check email and click your link for activation email'),'success')
                    return redirect('accounts:signin')

            else:
                messages.success(request, _('please first register in site'),'success')
                return redirect('accounts:signup')
        else:
            context = {
                'form_login': UserLogin(request.POST),
            }
            messages.error(request, 'email or password email not True', 'warning')
            return render(request, 'login.html', context)
    else:
        context = {
            'form_login': UserLogin(),
        }
        return render(request, 'login.html', context)


@login_required
def logoutg(request):
    logout(request)
    messages.success(request, _('you are logout of site'), 'success')
    return redirect('accounts:signin')


def password_confirm_down(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if user is not None and account_activation_token.check_token(user, token):
                password = cd['new_password']
                print('rrrrrrrrrrrrrrrrrrrrrrr',password)
                user = User.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, _('reset password complete'),'success')
                return redirect('accounts:signin')
            else:
                messages.warning(request, _("please triing ea\gain"))
                return redirect('accounts:email_form')
        else:
            form_password = PasswordForm(request.POST)
            return render(request, 'login.html',{'form_password':form_password} )
    else:
        form_password = PasswordForm()
        return render(request, 'login.html',{'form_password':form_password,'user':user.email} )

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
        return redirect('accounts:signin')
    else:
        messages.warning(request, _('The confirmation link was invalid, possibly because it has already been used.'),'error')
        return redirect('accounts:signin')


@login_required
def remove_session(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        try:
            sessn = SessionUser.objects.get(user = request.user, session_key__session_key=key)
            if sessn:
                session = Session.objects.get(session_key = key)
                session.delete()
                return redirect('accounts:profile')
            return redirect('accounts:profile')
        except:
            return redirect('accounts:profile')
    else:           
        return redirect('accounts:profile')



@login_required
def profile(request):
    context = {
        'courses' : Course.objects.filter(teacher = request.user.teacher),
        'sessions' : SessionUser.objects.filter(user=request.user),
        'orders': Order.objects.filter(user=request.user, is_paid = True)
    }
    if request.user.is_teacher:
        paids = []
        orders = Order.objects.filter(is_paid = True)
        for order in orders:
            if not order.is_book: 
                if order.content_object.teacher == request.user.teacher:
                    paids.append(order)

        context.update({'paids':paids})
    return render(request, 'profile.html', context)

