from django.urls import path
from django.urls.conf import include, path
from .views_user import signup, signin, signout,index
from .views_cart import add_to_basket, basket, order, send_request, verify
from .views import (
                category,admin_panel, news_blog_create,
                news_blog,news_blog_delete,news_blog_single,
                news_blog_edit,session_delete, profile
            )
from.views_book import book_single,book_all, book_create, book_delete,book_edit,book_comment
from .views_course import (
                course_create, course_edit,course_all,
                course_single,teacher_course,
                email_save,email_sending,course_create_video,
                course_video_edit,course_video_delete,course_delete,
            )

app_name = 'api'

course_urlpatterns = [
    path('create/',course_create, name='course_create'),
    path('create/video/<str:slug>/',course_create_video, name='course_create_video'),
    path('delete/<str:slug>/',course_delete, name='course_delete'),
    path('edit/video/<int:pk>/',course_video_edit, name='course_video_edit'),
    path('delete/video/<int:pk>/',course_video_delete, name='course_video_delete'),
    path('edit/<str:slug>/',course_edit, name='course_edit'),
    path('single/<str:slug>/',course_single, name='course_single'),
]

book_urlpatterns = [
    path('single/<str:slug>/',book_single, name='book_single'),
    path('delete/<str:slug>/',book_delete, name='book_delete'),
    path('edit/<str:slug>/',book_edit, name='book_edit'),
    path('',book_all, name='book_all'),
    path('create/',book_create, name='book_create'),
    path('comment/',book_comment, name='book_comment'),
    path('news/blog/create/',news_blog_create, name='news_blog_create'),
    path('news/blog/',news_blog, name='news_blog'),

]

news_urlpatterns = [
    path('blog/create/',news_blog_create, name='news_blog_create'),
    path('',news_blog, name='news_blog'),
    path('blog/delete/<int:pk>/',news_blog_delete, name='news_blog_delete'),
    path('blog/single/<int:pk>/',news_blog_single, name='news_blog_single'),
    path('blog/edit/<int:pk>/',news_blog_edit, name='news_blog_edit'),
]

cart_urlpatterns = [
    path('basket/', basket, name='basket'),
    path('order/', order, name='order'),
    path('send/request/<int:pk>/', send_request, name='send_request'),
    path('verify/<int:pk>/', verify , name='verify'),
]


urlpatterns = [
    path('signup/',signup, name='signup'),
    path('signin/',signin, name='signin'),
    path('signout/',signout, name='signout'),

    path('index/',index, name='index'),
    path('admin/panel/',admin_panel, name='admin_panel'),
    path('create/category/',category, name='create_category'),
    path('teacher/course/<str:slug>/',teacher_course, name='teacher_course'),
    path('add/to/basket/<str:name>/<int:pk>/',add_to_basket, name='add_to_basket'),
    path('profile/', profile ,name='profile'),
    path('cart/', include(cart_urlpatterns)),

    path('email/save/', email_save, name='email_save'),
    path('email/send/', email_sending, name='email_sending'),
    path('session/delete/', session_delete, name='session_delete'),

   
    path('',course_all, name='course_all'),
    path('course', include(course_urlpatterns)),
    path('book/', include(book_urlpatterns)),
    path('news/', include(news_urlpatterns)),

]
