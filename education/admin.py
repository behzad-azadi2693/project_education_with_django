from django.http.response import FileResponse
from education.views import search
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import Book, Order ,Comment, CourseVideo, Contact, Course, Category, Newsletter_email, EmailSending
# Register your models here.
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _


@admin.register(Book)
class AdminBook(admin.ModelAdmin):
    date_hierarchy = 'date'

    prepopulated_fields = {'slug': ('title','name' )}
    list_filter = ('name','title', 'price','date')
    list_display = ('name', 'author', 'price', 'awatar', 'is_free')
    search_fields= ('name','title', 'description')
    fieldsets = (
        (_('INFORMATION'), {"fields": ('name','title','slug','page','language', 'image','author','date','description'),}),
        (_('INFORMATION PAID'), {"fields": ('price','discount','is_free'),}),
    )
    
    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.image.url,))

@admin.register(Newsletter_email)
class AdminNewsletter_email(admin.ModelAdmin):
    list_display = ('email','title','awatar')
    list_filte = ('email',)
    search_fields = ('email',)

    fieldsets = (
        (_('INFORMATION'), {"fields": ('email','course'),}),)
    
    def title(self, obj):
        return obj.course.title

    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.course.image.url,))

@admin.register(EmailSending)
class AdminEmailSending(admin.ModelAdmin):
    list_display = ('subject','date','username','awatar')
    list_filter = ('subject', 'date','user', 'course')
    search_fields = ('subject',)

    fieldsets = (
        (_('INFORMATION EMAIL'), {"fields": ('subject','message','date'),}),
        (_('INFORMATION SENDER'), {"fields": ('user','course'),}),
    )
    def username(self, obj):
        return obj.user.email

    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.course.image.url,))



@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name','email','date','awatar')
    list_filter = ('date','name','email')
    search_fields = ('name', 'email')
    fieldsets = (
        (_('INFORMATION EMAIL'), {"fields": ('name', 'email', 'message'),}),
        (_('INFORMATION reply'), {"fields": ('course','date'),}),
        )

    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.course.image.url,))




@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name','title','full_name', 'awatar', 'is_free')
    list_filter = ('name','title','teacher', 'is_free','price','date','discount','time')
    search_fields = ('name','title','description')
    prepopulated_fields = {'slug': ('title','name' )}

    fieldsets = (
        (_('INFORMATION'), {"fields": ('name','title','teacher','course','image','translate','view','time','date','description'),}),
        (_('INFORMATION PAID'), {"fields": ('price','discount','is_free'),}),
    )
    
    def full_name(self, obj):
        return obj.teacher.user.full_name

    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.image.url,))



@admin.register(CourseVideo)
class AdminCourseVideo(admin.ModelAdmin):
    list_display = ('number','title','awatar')
    list_filter = ('number', 'title', 'course')
    search_fields = ('number', 'title')
    fieldsets = (
        (_('INFORMATION'), {"fields": ('number', 'title', 'course', 'file'),}),
    )
    
    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.image.url,))


@admin.register(Contact)
class AdminContact(admin.ModelAdmin):
    list_display = ('name','email','subject')
    list_filter = ('name', 'email', )
    search_fields = ('email', 'subject','email')
    fieldsets = (
        (_('INFORMATION'), {"fields": ('name', 'email', 'subject', 'message'),}),
    )

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ('category','sub_category')
    list_filter = ('category', 'sub_category')
    search_fields = ('category', 'sub_category')
    fieldsets = (
        (_('INFORMATION'), {"fields": ('category', 'sub_category'),}),
    )


@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ('user', 'is_paid', 'is_book','code_payment', 'awatar')
    list_filter = ('is_paid', 'price_paide')
    fieldsets = (
        (_('INFORMATION'), {"fields": ('user','price_paide','is_paid'),}),
        (_('INFORMATION GENERIC'), {"fields": ('content_type','object_id','is_book'),}),

    )
    
    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.content_object.image.url,))