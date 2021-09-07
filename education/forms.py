from django import forms
from django.forms import ModelForm
from django import forms
from .models import Course, Book, CourseVideo, Category, Comment, BookComment
from django.utils.translation import gettext_lazy as _

messages = {
    'required':_("this field is required"),
    'invalid':_("It is not correct"),
    'max_length':_("The size of the characters is large of 15 character"),
    'min_length':_("The size of the characters is small of 9 character"),
}


class CourseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].error_messages = messages

    class Meta:
        model = Course
        fields = ('category','name','title','description','discount','is_free','date','time','price','image','translate')


class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].error_messages = messages

    class Meta:
        model = Category
        fields = ('category','sub_category')


class CourseVideoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseVideoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].error_messages = messages

    class Meta:
        model = CourseVideo
        fields = ('number','title','file')


class BookForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].error_messages = messages

    class Meta:
        model = Book
        fields = ('name','title','author','description','date','language','page','price','discount','is_free','image','file')


class CommentCourseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentCourseForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = messages

    class Meta:
        model = Comment
        fields = ('name','email','message')
        widgets ={
            'name':forms.TextInput(attrs={'placeholder':_("your name ..."), 'class':'form-control'}),
            'email':forms.TextInput(attrs={'placeholder':_("your email ..."), 'class':'form-control'}),
            'message':forms.Textarea(attrs={'placeholder':_("your message ..."), 'class':'form-control'}),
        }

class BookCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookCommentForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = messages

    class Meta:
        model = BookComment
        fields = ('name','email','message')
        widgets ={
            'name':forms.TextInput(attrs={'placeholder':_("your name ..."), 'class':'form-control'}),
            'email':forms.TextInput(attrs={'placeholder':_("your email ..."), 'class':'form-control'}),
            'message':forms.Textarea(attrs={'placeholder':_("your message ..."), 'class':'form-control'}),
        }