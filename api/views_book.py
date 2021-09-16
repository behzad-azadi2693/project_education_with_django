from django.core.checks import messages
from django.core.paginator import Paginator
from django.db.models import manager
from rest_framework import permissions
from education.models import Book, BookComment, Comment, Course, Newsletter_email, Order
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.cache import cache
from .serializer_book import (
                BookSerializer, BookSingleSerializer, BookCommentSerializer, CommentSerializer,
                SingleSerializer
            )
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail


@api_view(['GET',])
def book_all(request):
    books = cache.get('book_all')
    if not books:
        books = Book.objects.all()
        if books:
            cache.set('book_all', books, 60 * 60)

    paginator = PageNumberPagination()
    paginator.page_size = 10

    books = Book.objects.all()
    result_page = paginator.paginate_queryset(books, request)

    srz = BookSerializer(result_page, many=True).data

    return paginator.get_paginated_response(srz)


@api_view(['GET',])
def book_single(request, slug):
    book = cache.get(f'book_{slug}')
    if not book:
        book = get_object_or_404(Book, slug=slug)
        if book:
            cache.set(f'book_{slug}',book, 3600)
    
    book_comment = book.relbook.all()
    paid = book.books.filter(user = request.user, is_paid=True)
    bookcomment_srz = BookCommentSerializer(book_comment, many=True).data

    form_data = BookComment(book = book)
    form = CommentSerializer(form_data)

    link = {}
    if paid or book.is_free:
        book_srz = BookSingleSerializer(book).data
    else:
        book_srz = SingleSerializer(book).data

        link.update({
            'add_to_basket':reverse('api:add_to_basket', args=['book', book.pk])
        })

    if request.user.is_authenticated and request.user.is_admin:

        link.update({
            'book_edit': reverse('api:book_edit', args=[book.slug]),
            'book_delete': reverse('api:book_delete', args=[book.slug])
        })

    srz = (bookcomment_srz, book_srz, link, form.data)
    return Response(srz, status=status.HTTP_200_OK)

@api_view(['GET','POST'])
def book_edit(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if not request.user.is_authenticated:
        return redirect('api:signin')

    if request.user.is_admin:
        if request.method == 'POST':
            form = BookSingleSerializer(book, data=request.data)
            if form.is_valid():
                obj = form.save()
                return redirect('api:book_single', obj.slug)
            else:
                form_new = BookSingleSerializer(book).data
                return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
        else:
            form = BookSingleSerializer(book)
            return Response(form.data,status=status.HTTP_200_OK)
    else:
        return redirect('api:index')

@api_view(['GET','POST'])
def book_create(request):
    if not request.user.is_authenticated:
        return redirect('api:signin')

    if request.user.is_admin:
        if request.method == 'POST':
            form = BookSingleSerializer(data=request.data)
            if form.is_valid():
                obj = form.save()
                return redirect('api:book_single', obj.slug)
            else:
                form_new = BookSingleSerializer()
                return Response(form.errors, form_new, status=status.HTTP_400_BAD_REQUEST)
        else:
            form = BookSingleSerializer()
            return Response(form.data,status=status.HTTP_200_OK)
    else:
        return redirect('api:index')


@api_view(['GET',])
def book_delete(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if not request.user.is_authenticated:
        return redirect('api:signin')

    if request.user.is_admin:
        book.delete()
        return redirect('api:book_all')

@api_view(['POST',])
def book_comment(request):
    if request.method == 'POST':
        form = CommentSerializer(data=request.data)
        if form.is_valid():
            form.save()
        
        else:
            pass
