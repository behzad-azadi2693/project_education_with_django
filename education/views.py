from accounts.models import SessionUser
from os import error, linesep
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.urls import reverse
from .models import Book, BookComment, Category, Contact, CourseVideo, NewsBlog, Order, Course, Comment, Newsletter_email, EmailSending
# Create your views here.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
from .forms import (
        CourseForm,CourseVideoForm,CategoryForm, BookForm, CommentCourseForm,
        BookCommentForm
)
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail


def index(request):
    courses = Course.objects.order_by('-date')[:4]
    news = NewsBlog.objects.order_by('-date') [:3]
    context = {
        'courses':courses,
        'students':get_user_model().objects.all().count(),
        'course': Course.objects.all().count(),
        'book':Book.objects.all().count(),
        'news':news  
    }

    return render(request, 'index.html', context)


@login_required
def send_email(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('education:index')

    if request.method == 'POST':
        cd = request.POST
        course = None
        if cd['slug'] != 'none':
            course = Course.objects.get(slug=cd['slug'])
            users = Newsletter_email.objects.filter(course = course)

        else:
            users = Newsletter_email.objects.all()

        email_list = []
        for user in users:
            email_list.append(user.email)
        
        path = cd['path']
        subject = cd['subject']
        message = cd['message']

        try:
            send_mail(
                subject,
                message,
                'Education Site',
                email_list,
                fail_silently=False,
            )
            EmailSending.objects.create(course = course, subject=cd['subject'], message=cd['message'], user=request.user)
            messages.success(request,_('email sendig successfully'), 'succsess')
            return redirect(path)
        except:
                messages.warning(request,_('email not sendig successfully'),'error')
                return redirect(path)
    
    return redirect('education:index')
        

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        msg = request.POST['message']
        if name == '' or email == '' or subject == '' or msg == '':
            messages.error(request, 'لطفا تمامی فیلدها را پر کنید','warning')
        else:
            query = Contact.objects.create(name=name, email=email, subject=subject, message=msg)
            query.save()

    return render(request, 'page-contact.html')



def courses(request):
    course_list = Course.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(course_list, 12)

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    context = {
        'courses':courses,
        'boo':course_list.count

    }

    return render(request, 'courses.html', context)


def teachercourse(request, slug):
    course_list = Course.objects.filter(teacher__slug = slug)
    page = request.GET.get('page', 1)

    paginator = Paginator(course_list, 12)

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    context = {
        'courses':courses,
        'boo':course_list.count

    }

    return render(request, 'courses.html', context)


def tag_search(request, name):
    tag_list = Course.objects.filter(category__name = name)
    page = request.GET.get('page', 1)

    paginator = Paginator(tag_list, 12)

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    context = {
        'courses':courses,
        'boo':tag_list.count

    }

    return render(request, 'courses.html', context)



def course_single(request, slug):
    course = get_object_or_404(Course, slug=slug)
    courses = Course.objects.filter(category__category=course.category, category__sub_category=course.category.sub_category).exclude(slug=slug)[:4]
    order = course.courses.filter(user=request.user).filter(is_paid=True)
    tags = Category.objects.order_by('?')[:6]

    context = {
        'course':course,
        'courses':courses,
        'order':order,
        'tags':tags,
        'form': CommentCourseForm()
    }

    if request.method == 'POST':
        form = CommentCourseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.save()
            return redirect('education:coursesingle', course.slug)
        else:
            context.update({'errors':form.errors})
            return render(request, 'course_single.html', context)

    return render(request, 'course_single.html', context)



def book_store(request):
    book_list = Book.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(book_list, 12)

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    context = {
        'books':books,
        'boo':book_list.count
    }

    return render(request, 'bookstore.html', context)



def book_single(request, slug):
    book = get_object_or_404(Book, slug=slug)
    books = Book.objects.filter(name__contains = book.name).exclude(slug=slug)[:4]
    is_buy = book.books.filter(user = request.user, is_paid = True)

    context = {
        'book':book,
        'books':books,
        'is_buy':is_buy,
        'form':BookCommentForm()
    } 

    if request.method == 'POST':
        form = BookCommentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.book = book
            obj.save()
            return redirect('education:book_single', book.slug)
        else:
            context.update({'errors':form.errors})
            return render(request, 'shop-single.html', context)

    return render(request, 'shop-single.html', context)


#this change
@login_required
def myorder(request):
    orders = Order.objects.filter(user = request.user, is_paid = True)
    context = {
        'orders':orders,
    }

    return render(request, 'cart.html', context)


@login_required
def cartview(request):
    orders = Order.objects.filter(user = request.user, is_paid = False)

    paid = 0

    for order in orders:
        paid = paid + int(order.content_object.price - (order.content_object.price * order.content_object.discount ))

    context = {
        'orders':orders,
        'paid':paid
    }

    return render(request, 'cart.html', context)


@login_required
def cart(request, name, pk):
    if name == 'book':
        course = get_object_or_404(Book, pk=pk)
        order = course.books.filter(user = request.user)
        if order:
            return redirect('education:cartview')
        else:
            basket = Order(content_object = course, user = request.user, is_book = True)
            basket.save()

    if name == 'education':
        course = get_object_or_404(Course, pk=pk)
        order = course.courses.filter(user = request.user)
        if order:
            return redirect('education:cartview')
        else:
            price_end = course.price * (course.price * course.discount)
            basket = Order(content_object = course, user = request.user)
            basket.save()

    if name == 'delete':
        order = Order.objects.get(pk=pk, user = request.user, is_paid = False).delete()
               
    return redirect('education:cartview')


@login_required
def panel(request):
    context = {
        'emails':EmailSending.objects.filter(course = None)
    }
    return render(request, 'panel.html', context)


@login_required
def newsletters(request):
    if request.method == 'POST':
        cd = request.POST
        path_name = cd['path']
        if cd['email'] == '':
            messages.error(request, _('please insert email field'),'warning')
            return redirect(path_name)
        else:
            course = Course.objects.filter(slug = cd['slug']).first() or None
            comment = Newsletter_email.objects.create(email=request.POST['email'],course = course)
            comment.save()
            messages.success(request, _('email successful submit'),'success')
            return redirect(path_name)

    return redirect('education:index')


def search(request):
    query = request.GET.get('q')

    courses = Course.objects.filter(
        Q(name__contains=query) | Q(date__contains=query) |
        Q(description__contains=query) | Q(title__contains=query)
    )
    
    books = Book.objects.filter(
        Q(name__contains=query) | Q(date__contains=query) |
        Q(description__contains=query)
    
    )

    context = {
        'orders' : list(chain(courses , books)),
    }

    return render(request, 'search.html', context)


@login_required
def create_category(request):
    if not request.user.is_admin:
        return redirect('education:index')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('education:index')
        else:
            form = CategoryForm(request.POST)
            context = {
                'form':form,
                'name':_('Create Category')
            }
            return render(request, 'create.html',context)
    else:
        form = CategoryForm()
        context = {
            'form':form,
            'name':_('Create Category')

        }
        return render(request, 'create.html',context)


@login_required
def create_course(request):
    if not (request.user.is_admin or request.user.is_teacher):
        return redirect('education:index')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.teacher = request.user.teacher
            obj.save()
            return redirect('education:coursesingle', obj.slug)
        else:
            form = CourseForm(request.POST, request.FILES)
            context = {
                'form':form,
                'name':_('Create Course')
            }
            return render(request, 'create.html',context)
    else:
        form = CourseForm()
        context = {
            'form':form,
            'name':_('Create Course')

        }
        return render(request, 'create.html',context)


@login_required
def create_coursevideo(request, pk):
    file = get_object_or_404(CourseVideo, pk=pk)

    teacher_access = False
    if file.teacher == request.user.teacher:
        teacher_access = True

    if not (request.user.is_admin or teacher_access):
        return redirect('education:index')

    if request.method == 'POST':
        form = CourseVideoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = file
            obj.save()
            return redirect('education:coursesingle', obj.course.slug)
        else:
            form = CourseVideoForm(request.POST, request.FILES)
            context = {
                'form':form,
                'name':_('Create Course Video')
            }
            return render(request, 'create.html',context)
    else:
        form = CourseVideoForm()
        context = {
            'form':form,
            'name':_('Create Course')

        }
        return render(request, 'create.html',context)


@login_required
def create_book(request):
    if not request.user.is_admin:
        return redirect('education:index')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('education:book_singel', form.slug)
        else:
            form = BookForm(request.POST, request.FILES)
            context = {
                'form':form,
                'name':_('Create Book')
            }
            return render(request, 'create.html',context)
    else:
        form = BookForm()
        context = {
            'form':form,
            'name':_('Create Book')
        }
        return render(request, 'create.html',context)


@login_required
def edit_course(request, pk):
    file = get_object_or_404(Course, pk=pk)
    
    teacher_access = False
    if file.teacher == request.user.teacher:
        teacher_access = True

    if not (request.user.is_admin or teacher_access):
        return redirect('education:index')


    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance = file)
        if form.is_valid():
            obj = form.save()
            return redirect('education:coursesingle', obj.slug)
        else:
            form = CourseForm(request.POST, request.FILES, instance=file)
            context = {
                'form':form,
                'name':_('Edit Category')
            }
            return render(request, 'create.html',context)
    else:
        form = CourseForm(instance=file)
        context = {
            'form':form,
            'name':_('Edit Course')

        }
        return render(request, 'create.html',context)


@login_required
def edit_coursevideo(request, pk):

    file = get_object_or_404(CourseVideo, pk=pk)
    
    teacher_access = False
    if file.course.teacher == request.user.teacher:
        teacher_access = True

    if not (request.user.is_admin or teacher_access):
        return redirect('education:index')


    if request.method == 'POST':
        form = CourseVideoForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save()
            return redirect('education:index')
        else:
            form = CourseVideoForm(request.POST, request.FILES, instance=file)
            context = {
                'form':form,
                'name':_('Edit Course Video')
            }
            return render(request, 'create.html',context)
    else:
        form = CourseVideoForm(instance = file)
        context = {
            'form':form,
            'name':_('Edit Course Video')

        }
        return render(request, 'create.html',context)


@login_required
def edit_book(request, pk):
    if not (request.user.is_admin):
        return redirect('education:index')

    file = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save()
            return redirect('education:index')
        else:
            form = BookForm(request.POST, request.FILES, instance = file)
            context = {
                'form':form,
                'name':_('Edit Book')
            }
            return render(request, 'create.html',context)
    else:
        form = BookForm(instance = file)
        context = {
            'form':form,
            'name':_('Edit Book')

        }
        return render(request, 'create.html',context)


@login_required
def delete_course(request, pk): 
    file = get_object_or_404(Course, pk=pk)
    
    teacher_access = False
    if file.teacher == request.user.teacher:
        teacher_access = True

    if not (request.user.is_admin or teacher_access):
        return redirect('education:index')

    file.delete()
    return redirect('education:teachercourse', request.user.teacher.slug)

@login_required
def delete_coursevideo(request, pk):
    file = get_object_or_404(CourseVideo, pk=pk)
    slug = file.course.slug

    teacher_access = False
    if file.teacher == request.user.teacher:
        teacher_access = True

    if not (request.user.is_admin or teacher_access):
        return redirect('education:index')

    file.delete()
    return redirect('education:coursesingle', slug)


@login_required
def delete_book(request, pk):
    if not (request.user.is_admin):
        return redirect('education:index')

    file = get_object_or_404(Book, pk=pk)

    file.delete()
    return redirect('education:book_store')
