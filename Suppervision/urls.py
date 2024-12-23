from django.urls import path
from .views import*
from django.contrib.auth.views import LoginView,LogoutView
from . import views

urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',signin, name="signin" ),
    path('client-home/', client_home_view,name='client-home'),
    path('login/', views.login, name='login'),
    path('services/', views.services, name='services'),
]