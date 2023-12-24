from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'Panel'

urlpatterns = [
     path('login/', views.CustomLoginView.as_view(template_name='login.html'), name='login'),
     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
     path('channels/', views.channel_list, name='channel_list'),
     path('channels/<int:channel_id>/', views.channel_detail, name='channel_detail'),
     path('posts/', views.post_list, name='post_list'),
     path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
     path('', views.home, name='home')
]