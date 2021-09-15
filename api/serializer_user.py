from datetime import date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import fields
from rest_framework import serializers


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, label='email')
    password = serializers.CharField(required=True, label='password')
    password_confirm = serializers.CharField(required=True, label='confierm password')
    
    def validate_email(self, value):
        email = value
        user = get_user_model().objects.filter(email=email, email_check=True).first()

        if user:
            raise ValidationError('this user is exists')

        return value

    def validate_password_confirm(self, value):
        data = self.get_initial()
        password = data.get('password')
        password_confirm = value

        if password_confirm != password:
            raise ValidationError('password and password confirm must be match')
        return value
    
    def validate_password(self, value):
        password = value

        if not password:
            raise ValidationError('this field is required')
        
        if len(password) < 8:
            raise ValidationError('password is short please inter must of 8 character')
        
        return value

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, label='email')
    password = serializers.CharField(required=True, label='password')
        