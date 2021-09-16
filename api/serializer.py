from django.contrib.contenttypes import fields
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from education.models import Category, NewsBlog,EmailSending
from django.contrib.auth import get_user_model
from education.models import Order,Course
from accounts.models import SessionUser

class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', )

class SessionSerializer(ModelSerializer):
    session_url = SerializerMethodField()

    class Meta:
        model = SessionUser
        fields = ('device','os','date_joiin')

    def get_session_url(self, obj):
        result = '{}'.format(reverse('api:session_delte', args=[obj.pk]))
        return result

class EmailSerializer(ModelSerializer):
    class Meta:
        model = EmailSending
        fields = ('subject', 'message')


class EmailTeacherSerializer(ModelSerializer):
    course = SerializerMethodField()

    class Meta:
        model = EmailSending
        fields = ('subject', 'message', 'date','course')

    def get_course(self, obj):
        return obj.course.name

class EmailAdminSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = EmailSending
        fields = ('subject','message','date','user')

    def get_user(self, obj):
        return obj.user.email

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id')

class NewsBlogSerializer(ModelSerializer):
    class Meta:
        model = NewsBlog
        exclude = ('id',)

class NewsBlogSerializerall(ModelSerializer):
    news_url = SerializerMethodField()
    class Meta:
        model = NewsBlog
        fields = ('title', 'image', 'date', 'news_url')

    def get_news_url(self, obj):
        result = '{}'.format(reverse('api:news_blog_single', args=[obj.pk]))
        return result

class CoursesSerializer(ModelSerializer):
    course_link = SerializerMethodField()

    class Meta:
        model = Course
        fields = ('name', 'image', 'price_end', 'course_link')

    def get_course_link(self, obj):
        result = '{}'.format(reverse('api:course_single', args=[obj.slug]))
        return result


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('name', 'image', 'price_end')

class OrderSerializer(ModelSerializer):
    content_object = CourseSerializer()
    order_link = SerializerMethodField()
    
    
    class Meta:
        model = Order
        fields = ('content_object','order_link')
    
    def get_order_link(self ,obj):
        if obj.is_book:
            result = '{}'.format(reverse('api:book_single', args=[obj.content_object.slug]),)
            return result
        else:
            result = '{}'.format(reverse('api:course_single', args=[obj.content_object.slug]),)
            return result
