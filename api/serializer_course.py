from education.models import Course, CourseVideo, Comment, Newsletter_email, EmailSending
from rest_framework.serializers import ModelSerializer,SerializerMethodField
from django.urls import reverse
from accounts.models import Teacher

class CourseCreate(ModelSerializer):
    class Meta:
        model = Course
        exclude = ('slug','id','teacher')

class CourseAll(ModelSerializer):
    single_url = SerializerMethodField()

    class Meta:
        model = Course
        fields = ('name', 'image', 'single_url')

    def get_single_url(self, obj):
        result = '{}'.format(reverse('api:course_single', args=[obj.slug],),)
        return result

class CommentCourse(ModelSerializer):
    class Meta:
        modeel = Comment
        fields = '__all__'


class Teacher(ModelSerializer):
    teacher_url = SerializerMethodField()
    class Meta:
        model = Teacher
        exclude = ('id','slug')
    def get_teacher_url(seelf, obj):
        result = '{}'.format(reverse('api:teacher_course',args=[obj.slug]))
        return result


class CourseSingle(ModelSerializer):
    teacher = Teacher()

    class Meta:
        model = Course
        exclude = ('id','slug')


class Coursevideo(ModelSerializer):
    class Meta:
        model = CourseVideo
        fields = '__all__'


class CourseVideoTeacher(ModelSerializer):
    video_edit = SerializerMethodField()
    video_delete = SerializerMethodField()

    class Meta:
        model = CourseVideo
        exclude = ('id',)
    
    def get_video_edit(self, obj):
        result = '{}'.format(reverse('api:course_video_edit', args=[obj.pk]),)
        return result
    
    def get_video_delete(self, obj):
        result = '{}'.format(reverse('api:course_video_delete', args=[obj.pk]),)
        return result

class NewsLetterEmail(ModelSerializer):
    email_save = SerializerMethodField()

    class Meta:
        model = Newsletter_email
        fields = ('email','course', 'email_save')
        extra_kwargs = {
            'course': {'read_only': True},
        }
    def get_email_save(self, obj):
        result = '{}'.format(reverse('api:email_save',))
        return result

class Emailsending(ModelSerializer):
    email_sending = SerializerMethodField()

    class Meta:
        model = EmailSending
        fields = ('subject', 'message', 'course', 'email_sending')
        
        extra_kwargs = {
            'course': {'read_only': True},
        }

    def get_email_sending(self, obj):
        result = '{}'.format(reverse('api:email_sending',))
        return result