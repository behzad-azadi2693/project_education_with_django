from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from .serializer_user import UserRegisterSerializer, UserLoginSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .token import send_token, account_activation_token
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse


@api_view(['GET'])
def signout(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')
    else:
        logout(request)
        return redirect('api:signin')

@api_view(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('api:index')

    if request.method == 'POST':
        form = UserRegisterSerializer(data=request.data)
        if form.is_valid():
            email = request.data.get('email')
            password = request.data.get('password')
            user = get_user_model().objects.filter(email=email).first()
            if not user:
                user = get_user_model().objects.create_user(email=email, password=password)
                user.is_active = False
                user.save()
                send_token(user, request)
                context = {
                    'messages': 'please check email and click onthe link for activation email',
                    'signin_url': reverse('api:signin',)
                }
                return Response(context, status.HTTP_201_CREATED)
            if not user.email_check:
                user.set_password(password)
                user.is_active=False
                user.save()
                send_token(user, request)
                context = {
                    'messages': 'please check email and click onthe link for activation email',
                    'signin_url': reverse('api:signin',)
                }
                return Response(context, status.HTTP_201_CREATED)
        else:
            form_new = UserRegisterSerializer().data
            srz = (form.errors, form_new)
            return Response(srz, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = UserRegisterSerializer().data
        return Response(form, status=status.HTTP_200_OK)


@api_view(['GET','POST'])
def signin(request):
    if request.user.is_authenticated:
        return redirect('api:index')
        
    if request.method == 'POST':
        form = UserLoginSerializer(data=request.data)
        if form.is_valid():
            email = request.data.get('email')
            password = request.data.get('password')
            user = get_user_model().objects.filter(email=email).first()
            if user is not None:
                if user.email_check:
                    user_is =  authenticate(request, email = email, password=password)
                    if user_is:
                        login(request, user_is)
                        return redirect('api:index')
                    else:
                        context = {
                            'messages': 'please check email or password field',
                            'form': UserLoginSerializer().data
                        }
                        return Response(context, status=status.HTTP_400_BAD_REQUEST)
                else:
                    send_token(user, request)
                    context = {
                        'messages': 'please check email and click on the link for activation email',
                        'form': UserLoginSerializer().data
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
            else:
                context = {
                    'messages': 'please first register in site',
                    'signup_url':reverse('api:signup',)
                }
                return Response(context, status=status.HTTP_404_NOT_FOUND)
        else:
            form_new = UserLoginSerializer().data
            srz = (form.errors, form_new)
            return Response(srz, status=status.HTTP_400_BAD_REQUEST)

    else:
        form = UserLoginSerializer().data
        return Response(form, status=status.HTTP_200_OK)
    
    
@api_view(['GET', ])    
def rest_activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_check = True
        user.save()
        context ={
            'messages': _('Your email account activate please login with email and password'),
            'signin_url': reverse('api:signin',)
        }
        return Response(context, status=status.HTTP_200_OK)

    else:
        context = {
            'messages': _('The confirmation link was invalid, possibly because it has already been used.'),
            'signin_url': reverse('api:signin',)
        }
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
def index(request):
    context = {
        'msg':'ok'
    }
    return Response(context)