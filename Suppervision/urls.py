from django import views
from django.urls import path
from django.conf import Settings
from .views import*

urlpatterns = [
    path('',home_view,name='home'),
    path('signin',signin, name="signin" )
]