from .models import User
from django.contrib.auth.backends import ModelBackend

class EmailLoginBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            return None

        except user.DosNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        
        except User.DosNotExist:
            return None