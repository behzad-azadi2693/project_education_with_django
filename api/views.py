from django.core.checks import messages
from django.core.paginator import Paginator
from django.db.models import manager
from rest_framework import permissions
from accounts.models import SessionUser
from education.models import Course, NewsBlog, Order,EmailSending
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.cache import cache
from .serializer import (
    CategorySerializer, CoursesSerializer, EmailTeacherSerializer, NewsBlogSerializer,
    NewsBlogSerializerall,EmailAdminSerializer, SessionSerializer,EmailSerializer,
    OrderSerializer,UserSerializer, EmailTeacherSerializer
)


@api_view(['GET',])
def profile(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    user = get_user_model().objects.get(email = request.user.email)
    buy = Order.objects.filter(user = request.user, is_paid = True)
    device = SessionUser.objects.filter(user=request.user)
    srz = ()

    if request.user.is_teacher:
        course_all = cache.get('course_all')
        if not course_all:
            course_all = Course.objects.all()
            if course_all:
                cache.set('course_all', course_all, 60*60)

        courses = course_all.filter(teacher__user = request.user)
        courses_srz = CoursesSerializer(courses, many=True).data
        emails = EmailSending.objects.filter(course__in = courses)
        email_srz = EmailTeacherSerializer(emails, many=True).data

    else:
        courses_srz = None
        email_srz = None

    user_srz = UserSerializer(user).data
    buy_srz = OrderSerializer(buy, many=True).data
    device_srz = SessionSerializer(device, many=True).data

    srz = (user_srz,buy_srz, device_srz,courses_srz, email_srz)
    return Response(srz, status=status.HTTP_200_OK)


@api_view(['DELETE',])
def session_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    obj = get_object_or_404(SessionUser, pk=pk, user=request.user)
    session = get_object_or_404(Session, Session_key = obj.session_key.Session_key)
    session.delete()
    return redirect('api:profile')


@api_view(['GET',])
def admin_panel(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    if request.user.is_authenticated and request.user.is_admin:
        link={
            'create_course': reverse('api:course_create'),
            'create_book' : reverse('api:book_create'),
            'create_category': reverse('api:create_category')
        }
        form = {
            'email':EmailSerializer().data,
            'email_url': reverse('api:email_sending'),
        }
        email = EmailSending.objects.filter(user__is_admin = True)
        email_srz = EmailAdminSerializer(email, many=True).data

        srz = (link, form, email_srz)

        return Response(srz, status.HTTP_200_OK)
    else:
        return redirect('api:profile')
        

@api_view(['GET', 'POST'])
def news_blog_create(request):
    if not (request.user.is_authenticated or request.user.is_admin):
        return redirect('api:signin')

    if request.method == 'POST':
        form = NewsBlogSerializer(data=request.data)
        if form.is_valid():
            form.save()
            return redirect('api:admin_panel')
        else:
            form_new = NewsBlogSerializer(data=request.data).data
            return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = NewsBlogSerializer().data
        return Response(form, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
def news_blog_edit(request, pk):
    if not (request.user.is_authenticated or request.user.is_admin):
        return redirect('api:signin')
    
    news = get_object_or_404(NewsBlog, pk=pk)

    if request.method == 'PUT':
        form = NewsBlogSerializer(news, data=request.data)
        if form.is_valid():
            form.save()
            return redirect('api:admin_panel')
        else:
            form_new = NewsBlogSerializer(news, data=request.data).data
            return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = NewsBlogSerializer(news).data
        return Response(form, status=status.HTTP_200_OK)


@api_view(['GET',])
def news_blog(request):
    news = NewsBlog.objects.all()

    srz = NewsBlogSerializerall(news, many=True).data

    return Response(srz, status=status.HTTP_200_OK)

@api_view(['DELETE',])
def news_blog_delete(request,pk):
    news = get_object_or_404(NewsBlog, pk=pk)

    if not (request.user.is_authenticated or request.user.is_admin):
        return redirect('api:signin')

    else:
        news.delete()
        return redirect('api:news_blog')


@api_view(['GET',])
def news_blog_single(request,pk):
    news = get_object_or_404(NewsBlog, pk=pk)

    form = NewsBlogSerializer(news).data
    link = {}

    if request.user.is_authenticated and request.user.is_admin:
        link = {
            'news_delete':reverse('api:news_blog_delete', args = [news.pk]),
            'news_edit':reverse('api:news_blog_edit', args=[news.pk])
        }

    srz = (form, link)
    return Response(srz, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def category(request):
    if request.method == 'POST':
        form = CategorySerializer(data=request.data)
        if form.is_valid():
            form.save()
            return redirect('api:admin_panel')
        else:
            form_new = CategorySerializer(data=request.data).data
            return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = CategorySerializer().data
        return Response(form, status=status.HTTP_200_OK)
