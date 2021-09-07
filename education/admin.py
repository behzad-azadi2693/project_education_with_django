from django.contrib import admin
from .models import Book, Order,Teacher ,Comment, CourseVideo, Contact, Course, Category, Newsletter_email, EmailSending
# Register your models here.


admin.site.register(Book)
admin.site.register(Newsletter_email)
admin.site.register(EmailSending)
admin.site.register(Comment)
admin.site.register(Order)
admin.site.register(Course)
admin.site.register(CourseVideo)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(Teacher)