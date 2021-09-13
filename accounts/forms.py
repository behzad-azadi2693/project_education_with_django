from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import fields
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from .models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField



messages = {
    'required':_("this field is required"),
    'invalid':_("It is not correct"),
    'max_length':_("The size of the characters is large of 15 character"),
    'min_length':_("The size of the characters is small of 9 character"),
    'max_value':_("out of range maximum size"),
    'min_value':_("out of range minimum size"),
}

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label=_('password'), widget=forms.PasswordInput)
    password_confierm = forms.CharField(label=_('password_confierm'), widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('email', 'email_check', 'password', 'password_confierm')

    def clean_password_confierm(self):
        cd = self.cleaned_data
        if cd['password'] and cd['password_confierm'] and cd['password'] != cd['password_confierm']:
            raise forms.ValidationError(_("password and confirm password must be match "))

        return cd['password_confierm']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserRegister(forms.Form):
    email = forms.EmailField(
        error_messages=messages,
        required=True,
        help_text = _('please rnter password egain'),
        widget=forms.TextInput(attrs={'placeholder':_('your email'),'class':'form-control','type':'email'})
    )

    password = forms.CharField( 
        error_messages=messages,
        required=True,
        help_text = _('please rnter password egain'),
        widget=forms.PasswordInput(attrs={'placeholder':_('password confirm'),'class':'form-control','type':'password'})
    )

    password_confierm = forms.CharField(
        error_messages=messages,
        required=True,
        help_text = _('please rnter password egain'),
        widget=forms.PasswordInput(attrs={'placeholder':_('password confirm'),'class':'form-control','type':'password'})
    )
    
    def clean_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        
        if len(cleaned_data['password']) < 8 and password:
            raise forms.ValidationError(_('this fields must of 8 character'))
        return password

    def clean_password_confierm(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confierm = cleaned_data.get('password_confierm')


        if password and password_confierm and password_confierm != password:
            raise forms.ValidationError(_('password and confierm passqord must be matched'))
        return password_confierm
        
class UserLogin(forms.Form):
   
    email = forms.EmailField(
        error_messages=messages,
        required=True,
        help_text = _('please rnter password egain'),
        widget=forms.TextInput(attrs={'placeholder':_('your email'),'class':'form-control','type':'email'})
    )
    password = forms.CharField( 
            error_messages=messages,
            required=True,
            help_text = _('please inter password '),
            widget=forms.PasswordInput(attrs={'placeholder':_('password'),'class':'form-control','type':'password'})
        )


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        models = User
        fields = ('email', 'email_check', 'password')

    def clean_password(self):
        return self.initial['password']
    
class EmailForm(forms.Form):
   
    email = forms.EmailField(
        error_messages=messages,
        required=True,
        help_text = _('please rnter password egain'),
        widget=forms.TextInput(attrs={'placeholder':_('your email'),'class':'form-control','type':'email'})
    )
   

    def clean_email(self):
        cd = self.cleaned_data
        try:
            user = get_user_model().objects.get(email=cd['email'], email_check=True)
            return cd['email']
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(_('this email is not validation'))


class PasswordForm(forms.Form):
   
    new_password = forms.CharField( 
            error_messages=messages,
            required=True,
            help_text = _('please inter password '),
            widget=forms.PasswordInput(attrs={'placeholder':_('new password'),'class':'form-control','type':'password'})
        )

    confirm_new_password = forms.CharField( 
            error_messages=messages,
            required=True,
            help_text = _('please inter password egain'),
            widget=forms.PasswordInput(attrs={'placeholder':_('password confirm'),'class':'form-control','type':'password'})
        )

    def clean_new_password(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        
        if len(cleaned_data['new_password']) < 8 and new_password:
            raise forms.ValidationError(_('this fields must of 8 character'))
            
        return new_password
    
    def clean_confirm_new_password(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('password')
        confirm_new_password = cleaned_data.get('password_confierm')

        if new_password and confirm_new_password and confirm_new_password != new_password:
            raise forms.ValidationError(_('password and confierm passqord must be matched'))
        return confirm_new_password
