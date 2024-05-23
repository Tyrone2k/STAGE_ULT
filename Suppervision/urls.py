from django.urls import path
from .views import*
from django.contrib.auth.views import LoginView,LogoutView

urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',signin, name="signin" ),
    path('client-home/', client_home_view,name='client-home'),
    path('login/', LoginView.as_view(template_name='Suppervision/login.html'),name='login'),
    path('afterlogin/', afterlogin_view,name='afterlogin'),
]