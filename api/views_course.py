from api.serializer import EmailSerializer
from django.core.checks import messages
from education.models import Course, Newsletter_email
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .serializer_course import (
                CourseCreate, CourseAll, CourseVideo,
                CourseSingle, CommentCourse, NewsLetterEmail,
                Emailsending, CourseVideoTeacher,Coursevideo,
            )
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail
from django.core.cache import cache


@api_view(['GET', 'POST'])
def course_create(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('api:index')

    if request.method == 'POST':
        form = CourseCreate(data=request.data)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.teacher = request.user.teache
            obj.save()
            return Response(form.data, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        form = CourseCreate().data
        return Response(form, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def course_edit(request, slug):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('api:index')

    course = get_object_or_404(Course, slug=slug, teacher=request.user.teacher)

    if request.method == 'POST':
        form = CourseCreate(course, data=request.data)
        if form.is_valid():
            form.save()
            return Response(form.data, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = CourseCreate(instance=course).data
        return Response(form, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def course_create_video(request, slug):
    course = get_object_or_404(Course, slug=slug)
    course_post = Coursevideo(course=course)
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    if request.user == course.teacher.user:
        if request.method == 'POST':
            form = Coursevideo(course_post, data=request.data)
            if form.is_valid():
                form.save()
                return Response(form.data, status=status.HTTP_201_CREATED)
            else:
                form_new = Coursevideo(course_post,).data
                return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
        else:
            form = Coursevideo(course_post,).data
            return Response(form, status=status.HTTP_200_OK)
    else:
        return redirect('api:index')


@api_view(['GET',])
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    if request.user == course.teacher.user:
        course.delete()
        return redirect('api:index')
    return redirect('api:index')


@api_view(['GET','POST'])
def course_video_edit(request, pk):
    course_video = get_object_or_404(CourseVideo, pk=pk)
    
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    if request.user == course_video.course.teacher.user:
        if request.method == 'POST':
            form = Coursevideo(course_video, request.data)
            if form.is_valid():
                form.save()
                return Response(form.data, status=status.HTTP_201_CREATED)
            else:
                form_new = Coursevideo(course_video, request.data).data
                return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
        else:
            form = Coursevideo(course_video).data
            return Response(form, status=status.HTTP_200_OK)
    else:
        return redirect('api:index')


@api_view(['GET',])
def course_video_delete(request, pk):
    course_video = get_object_or_404(CourseVideo, pk=pk)
    path = reverse('api:course_single', args=[course_video.course.slug])
    if not request.user.is_authenticated:
        return redirect('api:signin')
    
    if request.user == course_video.course.teacher.user:
        course_video.delete()
        return redirect(path)
    else:
        return redirect('api:index')


@api_view(['GET','POST'])
def course_all(request):
    course_all = cache.get('course_all')
    if not course_all:
        course_all = Course.objects.all()
        if course_all:
            cache.set('course_all', course_all, 60*60)

    paginator = PageNumberPagination()
    paginator.page_size = 10

    result_page = paginator.paginate_queryset(course_all, request)

    srz = CourseAll(result_page, many=True).data

    return paginator.get_paginated_response(srz)


@api_view(['GET',])
def teacher_course(request,slug):
    course_all = cache.get('course_all')
    if not course_all:
        course_all = Course.objects.all()
        if course_all:
            cache.set('course_all', course_all, 60*60)

    courses = course_all.filter(teacher__slug = slug)
    srz = CourseAll(courses, many=True).data
    return Response(srz, status=status.HTTP_200_OK)


@api_view(['GET','POST'])
def course_single(request, slug):
    course_data = cache.get(f'course_{slug}')
    if not course_data:
        course_data = get_object_or_404(Course, slug=slug)
        if course_data:
            cache.set(f'course_{slug}', course_data, 3600)


    course_all = cache.get('course_all')
    if not course_all:
        course_all = Course.objects.all()
        if course_all:
            cache.set('course_all', course_all, 60*60)

    courses_video = course_data.relcourse.all()
    course_comment = course_data.commentcourse.all()
    user_course = course_data.courses.filter(user = request.user, is_paid  =True)
    instance_course = course_all.filter(category=course_data.category).exclude(slug=slug)[:4]
    
    course = CourseSingle(course_data).data
    comment = CommentCourse(course_comment, many=True).data
    course_instance = CourseAll(instance_course, many=True).data

    email_data = {'course':course_data,'email':None, 'subject':None,'message':None}
    form ={
        'form_email': NewsLetterEmail(email_data).data
    }

    link={}
    if course_data.teacher.user == request.user:
        courses = CourseVideoTeacher(courses_video, many=True).data
        link.update({
            'course_edit':reverse('api:course_edit', args=[course_data.slug]),
            'course_delete':reverse('api:course_delete', args=[course_data.slug]),
            'create_course_video':reverse('api:course_create_video', args=[course_data.slug])
        })
        form.update({
            'form_email_teacher':Emailsending(email_data).data
        })

    elif course_data.is_free or user_course:
        courses = CourseVideo(courses_video, many=True).data
    else:
         courses = None

    if request.user.is_authenticated and not user_course and not course_data.is_free:
        link.update({
            'add_to_basket':reverse('api:add_to_basket', args={'course', course_data.pk})
        })

    srz = (course,course_instance, courses, comment, link, form)

    return Response(srz, status=status.HTTP_200_OK)


@api_view(['POST',])
def email_save(request):
    if request.method == 'POST':
        form = NewsLetterEmail(data=request.data)
        if form.is_valid():
            obj = form.save()
            if obj.slug:
                return redirect('api:course_single', obj.slug)
            else:
                message = {
                    'message':'your email submited with successfully'
                }
                return Response(messages, status=status.HTTP_201_CREATED)
        else:
            form_new = NewsLetterEmail().data
            return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = NewsLetterEmail().data
        return Response(form, status=status.HTTP_200_OK)



@api_view(['POST'])
def email_sending(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    if not (request.user.is_teacer and request.user.is_admin):
        return redirect('api:index')

    if request.method == 'POST':
        form = Emailsending(data=request.data)
        if form.is_valid():
            subject = form.subject
            message = form.message 
            course = form.course or None
            if course is not None:
                emilses = Newsletter_email.objects.filter(course = course )
            else:
                emilses = Newsletter_email.objects.all()
            email_list = [email.email for email in emilses]
            try:
                send_mail(
                    subject,
                    message,
                    'Education Site',
                    email_list,
                    fail_silently=False,
                )
                obj = form.save(commit = False)
                obj.user = request.user
                obj.save()
                return Response(form.data, status=status.HTTP_200_OK)
            except:
                message = {
                    'message':'emial don`t sending please try egain',
                }
                return Response(message)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        message = {
                    'message':'emial don`t sending please try egain',
                }
        form_new = EmailSerializer(data=request.data).data
        return Response(message, form_new)