from django import forms
from django.contrib.auth import get_user_model
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
        
    #def clean_email(self):
    #    cd = self.cleaned_data
    #    user = User.objects.filter(email=cd['email'], email_check = True).first()
    #    
    #    if user:
    #        raise forms.ValidationError(_(''))
    #    else:
    #        return cd['email']

    def clean_password_confierm(self):
        cd = self.cleaned_data
        if len(cd['password']) < 8:
            raise forms.ValidationError(_('length password must of 8 character'))
        
        if cd['password'] and cd['password_confierm'] and cd['password'] != cd['password_confierm']:
            raise forms.ValidationError(_("password and confirm password must be match "))
        return cd['password_confierm']


class UserLogin(forms.ModelForm):
   
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        widgets ={
            'email':forms.TextInput(attrs={'placeholder':_("your email ..."), 'class':'form-control'}),
            'password':forms.TextInput(attrs={'placeholder':_("your password ..."), 'type':'password','class':'form-control'}),
        }

    def clean(self):
        cd = self.cleaned_data
        user = get_user_model().objects.filter(email=cd['email'])
        if not user:            
            raise forms.ValidationError(_("this user dosen't exict"))

        if not user.check_email:
            raise forms.ValidationError(_("this user don't email confirmation"))

        if user:
            if user.password != cd['password']:
                raise forms.ValidationError(_("user or password wrong"))
        
        return cd['user']


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        models = User
        fields = ('email', 'email_check', 'password')

    def clean_password(self):
        return self.initial['password']
    