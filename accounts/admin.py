from .models import User, Teacher, SessionUser
from django.contrib import admin
from .forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from education.models import EmailSending
from django.contrib.sessions.models import Session


class TeacherInline(admin.TabularInline):
    model = Teacher
    fields  = ('user','slug','description','image','gmail','group','twitter','facebook','google_plus')
    

class EmailInline(admin.TabularInline):
    model = EmailSending
    fields  = ('subject', 'user', 'message')


@admin.register(User)
class AdminUser(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'is_admin','teacher', 'is_active','email_check')
    list_filter = ('is_admin', 'is_teacher', 'full_name' )
    fieldsets = ( #this is for form
        (_('Information'),{'fields':('email','full_name','email_check','password')}),
        (_('personal info'),{'fields':('is_active','is_admin','is_teacher')}),
        (_('permission'),{'fields':('groups', 'user_permissions')}),
    )
    add_fieldsets = (#this is for add_form 
        (_('Information'),{'fields':('email', 'password','password_confierm')}),
        (_('otp information'),{'fields':('email_check',)}),
        (_('Access'),{'fields':('is_active','is_admin', 'groups', 'user_permissions')})
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    inlines = [TeacherInline,EmailInline]

    actions = ('make_admin',)

    def make_admin(self, request, queryset):
        queryset.update(is_admin=True)



@admin.register(Teacher)
class AdminTeacher(admin.ModelAdmin):
    list_display = ('full_name','awatar')
    
    fieldsets = (
        (_('INFORMATION'), {"fields": ('user','slug','description','image'),}),
        (_('INFORMATION SOCIAL'), {"fields": ('gmail','group','twitter','facebook','google_plus'),}),
    )
    
    def full_name(self, obj):
        return obj.user.full_name

    def awatar(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(url=obj.image.url,))

admin.site.register(Session)

@admin.register(SessionUser)
class AdminSessionUser(admin.ModelAdmin):
    list_filter = ('user','id', 'date_joiin')
    list_display = ('user','session_key', 'date_joiin')
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False    
