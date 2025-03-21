from django.urls import path,include
from .views import*
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import annuler_commande; select_category


urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',views.signin, name="signin" ),
    path('login/', LoginView.as_view(template_name='login.html'),name='login'),
    path('after-login/', views.after_login, name='after_login'),
    path('logout/', LogoutView.as_view(template_name='Client/logout.html'),name='logout'),


    path('services/', views.services, name='services'),
    path('galerie/', views.galerie, name='galerie'),
    path('contact/', views.contact, name='contact'),

    path('client-home/', views.client_home_view,name='client-home'),
    path('client-home/galerie/design-interieur/', views.design_interieur, name='design_interieur'),
    path('client-home/galerie/design-exterieur/', views.design_exterieur, name='design_exterieur'),
    path('client-home/galerie/', views.client_galerie, name='client_galerie'),
    path('client-home/commande/<int:design_id>/', views.ajout_produits, name='ajout_produits'),
    path('client-home/commande/enregistrer_commande/', views.enregistrer_commande, name='commande'),
    path('client-home/annuler-commande/<int:order_id>/', annuler_commande, name='annuler_commande'),
    path('client-home/select-category/<int:order_id>/', select_category, name='select_category'),
    path('client-home/orders/', views.client_orders, name='client_orders'),
    path('client-home/commande/filtrer_produits/', views.FiltrerProduitsView.as_view(), name='filtrer_produits'),
    path('client-home/panier/', views.panier, name='panier'),
    path('client-home/paiement/', views.paiement, name='paiement'),
    path('client-home/paiement/visite-local/', views.visite_local, name='visite_local'),
    path('client-home/paiement/success/<str:type_paiement>/', views.paiement_success, name='paiement_success'),
    path('client-home/error/', views.error, name='error'),
    
    path('client-home/profile/', views.view_profile, name='view_profile'),
    path('client-home/profile/edit-profile/', views.edit_profile_view,name='edit_profile'),


    path('admin-dashboard/', views.admindashboard, name='admin_dashboard'),
    path('manage-accounts/', views.manage_accounts, name='manage_accounts'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('accounts/profile/', RedirectView.as_view(url='admin-dashboard/', permanent=False), name='profile-redirect'),


    path('statistics/', views.statistics, name='statistics'),

    path('manage-stock/', views.manage_stock, name='manage_stock'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('edit-stock/<int:user_id>/', views.edit_stock, name='edit_stock'),
    path('delete-stock/<int:user_id>/', views.delete_stock, name='delete_stock'),

    path('manage-payments/', views.manage_payments, name='manage_payments'),



    path('superviseur-dashboard/', views.superviseurdashboard, name='superviseur_dashboard'),
    path('superviseur/liste-attente/', views.liste_attente, name='liste_attente'),
    path('superviseur/liste-attente/manage/', views.manage_liste_attente, name='manage_liste_attente'),
    path('superviseur/liste-attente/<int:liste_attente_id>/', views.liste_attente_detail, name='liste_attente_detail'),
    path('superviseur/liste-attente/<int:liste_attente_id>/mark-done/', views.mark_liste_attente_done, name='confirm_mark_done'),

    path('superviseur/renovation/list/', views.liste_renovation, name='liste_renovation'),
    path('superviseur/renovation/<int:renovation_id>/', views.renovation_detail, name='renovation_detail'),
    path('superviseur/renovation/<int:renovation_id>/mark-done/', views.mark_renovation_done, name='confirm_renovation_done'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)