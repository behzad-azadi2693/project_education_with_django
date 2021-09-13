from django.urls import path
from .views_user import signup, signin, signout,index


app_name = 'api'

urlpatterns = [
    path('signup/',signup, name='signup'),
    path('signin/',signin, name='signin'),
    path('signout/',signout, name='signout'),
    path('index/',index, name='index'),
]
