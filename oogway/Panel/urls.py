from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
     path('login/', views.CustomLoginView.as_view(template_name='login.html'), name='login'),
     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
     path('', views.home, name='home')
]