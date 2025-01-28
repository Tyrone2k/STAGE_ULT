from django.urls import path
from .views import*
from django.contrib.auth.views import LoginView,LogoutView
from . import views

urlpatterns = [
    path('',home_view,name='home'),
    path('client-home/', client_home_view,name='client-home'),
    path('signin/',views.signin, name="signin" ),
    path('login/', LoginView.as_view(template_name='login.html'),name='login'),
    path('after-login/', views.after_login, name='after_login'),
    path('designs/', views.designs, name='designs'),
    path('services/', views.services, name='services'),
    path('galerie/', views.galerie, name='galerie'),
    path('contact/', views.contact, name='contact'),
    path('admin-dashboard/', views.admindashboard, name='admin_dashboard'),
    path('superviseur-dashboard/', views.superviseurdashboard, name='superviseur_dashboard'),
    path('manage-accounts/', views.manage_accounts, name='manage_accounts'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
]