from django.urls import path
from .views import*
from django.contrib.auth.views import LoginView,LogoutView
from . import views

urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',signin, name="signin" ),
    path('client-home/', client_home_view,name='client-home'),
    path('login/', views.login, name='login'),
    path('designs/', views.designs, name='designs'),
    path('services/', views.services, name='services'),
    path('galerie/', views.galerie, name='galerie'),
    path('contact/', views.contact, name='contact'),
]