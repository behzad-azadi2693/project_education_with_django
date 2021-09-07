from django.urls import path
from .views import signup, logining, logoutg

app_name = 'accounts'

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('login/', logining, name="login"),
    path('logout/', logoutg, name="logout"),
]
