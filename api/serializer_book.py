from django.contrib.contenttypes import fields
from django.contrib.sessions import models
from rest_framework import serializers
from education.models import Course, CourseVideo, Comment, Newsletter_email, EmailSending,BookComment
from rest_framework.serializers import ModelSerializer,SerializerMethodField
from django.urls import reverse
from education.models import Book


class BookSerializer(ModelSerializer):
    single_url = SerializerMethodField()

    class Meta:
        model = Book
        fields = ('name', 'image', 'single_url')

    def get_single_url(self, obj):
        result = '{}'.format(reverse('api:book_single', args=[obj.slug]),)
        return result


class BookSingleSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class SingleSerializer(ModelSerializer):
    class Meta:
        model = Book
        exclude = ('id', 'file')

class BookCommentSerializer(ModelSerializer):
    class Meta:
        model = BookComment
        fields = ('name', 'message')


class CommentSerializer(ModelSerializer):
    book_url = SerializerMethodField()

    class Meta:
        model = BookComment
        exclude = ('id',)
        extra_kwargs = {
            'book': {'read_only': True},
        }
    
    def get_book_url(self, obj):
        result = '{}'.format(reverse('api:book_comment'))