from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.sessions.models import Session

# Create your models here.

class  MyUserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError(_("please insert email"))
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_admin=True
        user.save(using=self._db)
        return user
 
class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=250, unique=True,verbose_name=_('your email'))
    email_check = models.BooleanField(default=False, verbose_name=_('user check email'))

    is_teacher = models.BooleanField(default=False, verbose_name=_('user is teacher'))
    is_active = models.BooleanField(default=True, verbose_name=_("user is active"))
    is_admin = models.BooleanField(default=False, verbose_name=_("user is admin"))
    
    full_name = models.CharField(max_length=300, default='None', verbose_name=_('name for user'))

    objects=MyUserManager()
    USERNAME_FIELD = 'email'
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
        
    @property
    def is_staff(self):
        return self.is_admin

    def save(self, *args, **kwargs):
        """saving to DB disabled"""
        super(User, self).save(*args, **kwargs)
    
    def price_amount(self):
        amount = 0
        for order in self.user.filter(is_paid=False):
            pass


def path_save_teacher(instance, filename):
    name = '{0}/{1}'.format(instance.user.email, filename)
    return 'teacher/'+name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, verbose_name=_('user teacher'))
    slug = models.SlugField(unique=True, max_length=150, default=uuid4)
    description = models.TextField(verbose_name=_('bio description teacher'))
    facebook = models.URLField(null=True, blank=True, verbose_name=_('facebook'))
    image = models.ImageField(upload_to=path_save_teacher, verbose_name=_('awatar'))
    twitter = models.URLField(null=True, blank=True, verbose_name=_('twitter'))
    google_plus = models.URLField(null=True, blank=True, verbose_name=_('google'))
    group = models.URLField(null=True, blank=True, verbose_name=_('group'))
    gmail = models.URLField(null=True, blank=True, verbose_name=_('gmail'))

    class Meta:
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.user.email

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args,**kwargs)

    def save(self, *args, **kwargs):
        try:
            this = Teacher.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except: 
            pass
        
        super(Teacher, self).save(*args, **kwargs)


class SessionUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('user name'))
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name=_('session key'))
    device = models.CharField(max_length=300, verbose_name=_('device name'))
    os = models.CharField(max_length=300, verbose_name=_('os name'))
    date_joiin = models.DateField(verbose_name=_('date join device'))
    ip_device = models.GenericIPAddressField(verbose_name=_('ip address device'))


    class Meta:
        verbose_name = _('session user device')        
        verbose_name_plural = _("ssessions user devices")
        ordering = ('-id',)
        app_label = 'accounts'