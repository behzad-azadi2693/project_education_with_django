import os
from datetime import date
from django.db import models
from django.urls import reverse
from accounts.models import Teacher
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Category(models.Model):
    category = models.CharField(max_length=250, verbose_name=_('category name'), help_text=_('Area of expertise'))
    sub_category = models.CharField(max_length=250, verbose_name=_('subcategory name'),help_text=_('Sub Area of expertties'))
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        app_label = _('accounts')

    def __str__(self) -> str:
        return f'{self.category}-{self.sub_category}'

def path_save_course(instance, filename):
    name = os.path.join('course',instance.slug, filename)
    return name

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING,related_name='categories', verbose_name=('category'))
    slug = models.SlugField(allow_unicode=True, verbose_name=_("course slug"), unique=True)
    name = models.CharField(max_length=250, verbose_name=_('course name'))
    title = models.CharField(max_length=300, verbose_name=_('course title'))
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_('select teacher'), related_name='teacher')
    description = models.TextField(verbose_name=_('course description'))
    image = models.ImageField(upload_to=path_save_course,verbose_name=_('awatar'))
    price = models.PositiveIntegerField(verbose_name=_('course price'), null=True, blank=True)
    view = models.PositiveIntegerField(default=0, verbose_name=_('Number Of visit'))
    time = models.TimeField(verbose_name=_('course time'))
    date = models.DateTimeField(verbose_name=_('publish date'))
    discount = models.FloatField(verbose_name=_('discount'), default='0.0')
    is_free = models.BooleanField(default=False, verbose_name=_('course free'))
    courses = GenericRelation('Order')
    translate = models.FileField(null=True, blank=True,upload_to= path_save_course, verbose_name=_('file translate'))
    
    def get_absolute_url(self):
        return reverse('education:coursesingle', args=(self.slug,))

    def price_end(self):
        product_price = self.price * (1 - self.discount)
        if 0 <= product_price <= self.price:
            return product_price
        else:
            return self.price

    def delete(self, *args, **kwargs):
        self.image.delete()
        self.translate.delete()
        super(Course, self).delete()

    def save(self, *args, **kwargs):
        slti = self.title.replace(' ','-')
        slna = self.name.replace(' ','-')
        self.slug = f'{slti}-{slna}'
        try:
            this = Course.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
            if this.translate != self.translate:
                this.translate.delete()
        except: 
            pass
        super(Course, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    course = models.ForeignKey(Course, models.CASCADE, verbose_name=_('select_course'), related_name='commentcourse')
    name = models.CharField(max_length=200, verbose_name=_('your name'))
    email = models.EmailField(max_length=200, verbose_name=_('your email'))
    message = models.TextField(verbose_name=_('message'))
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replay', null=True, blank=True)
    is_reply = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.name


def path_save_coursevideo(instance, filename):
    name = os.path.join('course',instance.course.slug, filename)
    return name

class CourseVideo(models.Model):
    number = models.PositiveBigIntegerField(verbose_name=_('number file'))
    title = models.CharField(max_length=300, verbose_name=_('title video'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='relcourse', verbose_name=_('select course'))
    file = models.FileField(upload_to=path_save_coursevideo, verbose_name=_('file video'))

    class Meta:
        verbose_name = _('course video')
        verbose_name_plural = _('courses video')
        app_label = 'accounts'
    
    def delete(self, *args, **kwargs):
        self.file.delete()
        super(CourseVideo, self).delete()

    def save(self, *args, **kwargs):
        try:
            this = NewsBlog.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete()
        except: 
            pass
        super(CourseVideo, self).save(*args,**kwargs)

    def __str__(self) -> str:
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=300, verbose_name=_('your name'))
    email = models.EmailField(verbose_name='email')
    subject = models.CharField(max_length=200, verbose_name='subject')
    message = models.TextField(verbose_name='message')

    class Meta:
        verbose_name = _('message received')
        verbose_name_plural = _('messages received')
        app_label = 'education'

    def __str__(self) -> str:
        return self.name


def path_save_book(instance, filename):
    name = os.path.join('book', instance.name, filename)
    return name

class Book(models.Model):
    name = models.CharField(max_length=250, verbose_name=_('book name'))
    title = models.CharField(max_length=300, verbose_name=_('course title'))
    slug = models.SlugField(allow_unicode=True, verbose_name=_("book slug"), unique=True)
    image = models.ImageField(upload_to = path_save_book, verbose_name=_('awatar'))
    file = models.FileField(upload_to= path_save_book, verbose_name=_('book pdf file'))
    author = models.CharField(max_length=200, verbose_name=_('writer'))
    description = models.TextField(verbose_name=_('description'))
    date = models.DateField(verbose_name=_('public date'))
    language = models.CharField(max_length=20, verbose_name=_('language book'))
    page = models.CharField(max_length=5, verbose_name=_('number of pages'))
    price = models.PositiveIntegerField(verbose_name=_('price'), null=True, blank=True)
    discount = models.FloatField(verbose_name=_('discount'),default='0.0')
    is_free = models.BooleanField(default=False,verbose_name=_('free'))
    books = GenericRelation('Order')

    def price_end(self):
        product_price = self.price * (1 - self.discount)
        if 0 <= product_price <= self.price:
            return product_price
        else:
            return self.price

    
    def get_absolute_url(self):
        return reverse('education:book_single', args=(self.slug,))
    
    def save(self, *args, **kwargs):
        slti = self.title.replace(' ','-')
        slna = self.name.replace(' ','-')
        self.slug = slti+ slna
        try:
            this = NewsBlog.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
            if this.file != self.file:
                this.file.delete()
        except: 
            pass

        super(Book, self).save()


    def delete(self, *args, **kwargs):
        self.image.delete()
        self.file.delete()
        super(Book, self).delete()

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.name

class BookComment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='relbook', verbose_name=_('select book'))
    message = models.TextField(verbose_name=_('MESSAGE'))
    name = models.CharField(max_length=200, verbose_name=_('your name'))
    email = models.EmailField(verbose_name=_('email'))

    class Meta:
        verbose_name = _('book comment')
        verbose_name_plural = _('books comment')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.name

class Newsletter_email(models.Model):
    email = models.EmailField(verbose_name=_('email'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True,verbose_name=_('select course'))

    class Meta:
        verbose_name = _('newsletter email')
        verbose_name_plural = _('newsletter emaills')
        app_label = 'accounts'

    def __str__(self) -> str:
        return self.email

class EmailSending(models.Model):
    course = models.ForeignKey(Course, related_name='emial_course', on_delete=models.DO_NOTHING,null=True,blank=True, verbose_name=_('select course'))
    subject = models.TextField(verbose_name=_("subject email"))
    message = models.TextField(verbose_name=_('message email'))
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, verbose_name=_('user sending'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date sending email'))

    class Meta:
        verbose_name = _('email sending')
        verbose_name_plural = _('emails sending')
        app_label = 'accounts'    
        ordering = ('-date',)
    
    def __str__(self) -> str:
        return self.user.email


def path_save_newsblog(instance, filename):
    name = os.path.join('newsblog', str(instance.date), filename)
    return name

class NewsBlog(models.Model):
    title = models.CharField(max_length=300, verbose_name=_('news title'))
    description = models.TextField(verbose_name=_('news dewcription'))
    date = models.DateField(auto_now_add=True, verbose_name=_('publish date'))
    image = models.ImageField(upload_to = path_save_newsblog, verbose_name=_('awatar'))

    def delete(self, *args, **kwargs):
        self.image.delete()
        super(NewsBlog, self).delete()

    def save(self, *args, **kwargs):
        try:
            this = NewsBlog.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except: 
            pass
        super(NewsBlog, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('news')
        verbose_name_plural = _('news')

    def __str__(self) -> str:
        return self.title


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('select user'), related_name='user')
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    price_paide = models.PositiveIntegerField(default=0, verbose_name=_('price pay ment'))
    is_paid = models.BooleanField(default=False, verbose_name=_('is paid'))
    code_payment = models.CharField(max_length=30, null=True, blank=True,verbose_name=_('code payment'))
    is_book = models.BooleanField(default=False)
    date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('order ')
        verbose_name_plural = _('orders ')
        app_label = 'accounts'
