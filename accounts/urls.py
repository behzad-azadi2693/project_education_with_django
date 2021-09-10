from django.urls import path
from .views import signup, signin, logoutg, remove_session, profile

app_name = 'accounts'

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('signin/', signin, name="signin"),
    path('logout/', logoutg, name="logout"),
    path('remove_session/', remove_session, name="remove_session"),
    path('profile/', profile, name='profile'),

]
