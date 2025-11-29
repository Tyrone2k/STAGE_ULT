import os
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse
import paypalrestsdk
from django.http import JsonResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import*
from .forms import*
from django.db.models import Sum, Count
import hashlib
from time import time
from django.contrib import messages
# import geocoder

logger = logging.getLogger(__name__)

# Fonctions utilitaires pour vérifier les rôles
def is_customer(user):
    return user.groups.filter(name='CLIENT').exists()

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def is_supervisor(user):
    return user.groups.filter(name='SUPERVISEUR').exists()

# -------------------------------------------------------------------
# ------------ C L I E N T   D A S H B O A R D-----------------------
# -------------------------------------------------------------------

def login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                if is_admin(user):
                    return redirect('admin_dashboard')
                elif is_supervisor(user):
                    return redirect('superviseur_dashboard')
                elif is_customer(user):
                    return redirect('client-home')
                return redirect('home')  # Si aucun groupe ne correspond
            else:
                error = "Votre compte est désactivé. Veuillez contacter l'administrateur."
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect."

    return render(request, 'login.html', {'error': error})


def signin(request):
    userForm = ClientUserForm()
    clientForm = ClientForm()
    if request.method == 'POST':
        userForm = ClientUserForm(request.POST)  # Corrigé 'request.Post' en 'request.POST'
        clientForm = ClientForm(request.POST, request.FILES)
        if userForm.is_valid() and clientForm.is_valid():
            user = userForm.save(commit=False)  # Corrigé 'save' en 'save()'
            user.set_password(userForm.cleaned_data['password'])  # Corrigé 'cleaned_data'
            user.is_active = False  # Ajouté pour que le compte soit inactif jusqu'à approbation
            user.save()  # Corrigé 'save' en 'save()'
            client = clientForm.save(commit=False)  # Corrigé 'save' en 'save()'
            client.user = user
            client.save()  # Corrigé 'save' en 'save()'
            print(f"Created user: {user}, client: {client}")  # Log pour débogage
            
            # Ajout du nouvel utilisateur au groupe 'CLIENT'
            try:
                client_group = Group.objects.get(name='CLIENT')  # Corrigé l'espace dans ' CLIENT'
                client_group.user_set.add(user)
            except Group.DoesNotExist:
                print("Groupe 'CLIENT' n'existe pas, veuillez le créer.")
                messages.error(request, "Erreur interne : groupe 'CLIENT' non trouvé.")
                return redirect('signin')
            
            messages.success(request, "Inscription réussie ! Votre compte est en attente d'approbation.")
            return redirect('login')
        else:
            print(f"User form errors: {userForm.errors}")
            print(f"Client form errors: {clientForm.errors}")
            for field in userForm:
                if field.errors:
                    messages.error(request, f"{field.label}: {field.errors.as_text()}")
            for field in clientForm:
                if field.errors:
                    messages.error(request, f"{field.label}: {field.errors.as_text()}")
    return render(request, 'signin.html', {'userForm': userForm, 'clientForm': clientForm})

@login_required(login_url='login')
def after_login(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_supervisor(request.user):
            return redirect('superviseur_dashboard')
        elif is_customer(request.user):
            return redirect('client-home')
    return redirect('login')



@login_required(login_url='login')
@user_passes_test(is_admin)
def create_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            # Logique personnalisée pour définir longitude et latitude
            # Par exemple, obtenir ces valeurs à partir d'une API de géolocalisation
            # ou d'une autre source
            commande.longitude = 0.0  # Remplacez par votre logique
            commande.latitude = 0.0   # Remplacez par votre logique
            commande.save()
            return redirect('manage_commandes')  # Redirigez vers une page de gestion des commandes
    else:
        form = CommandeForm()
    return render(request, 'create_commande.html', {'form': form})

def home_view(request):
    return render(request, 'home.html')

def galerie(request):
    query = request.GET.get('q', '')  # Récupérer la valeur de la recherche
    if query:
        designs = Design.objects.filter(nom__icontains=query)  # Filtrer les designs par nom
    else:
        designs = Design.objects.all()
    return render(request, 'galerie.html', {'designs': designs, 'query': query})

def services(request):
    return render(request, 'services.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Envoyer un email ou autre logique
            return redirect('success_page')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ---------------------------------------------------------------------------------------------------------------
# ------- C L I E N T   D A S H B O A R D -----------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
@user_passes_test(is_customer)
def client_home_view(request):
    return render(request, 'Client/clienthome.html', {'user': request.user})


@login_required(login_url='login')
@user_passes_test(is_customer)
def design_interieur(request):
    designs = Design.objects.filter(category__nom="Intérieur")  # Supposons que vous avez une catégorie
    return render(request, 'Client/design_interieur.html', {'designs': designs})

@login_required(login_url='login')
@user_passes_test(is_customer)
def design_exterieur(request):
    designs = Design.objects.filter(category__nom="Extérieur")  # Supposons que vous avez une catégorie
    return render(request, 'Client/design_exterieur.html', {'designs': designs})


@login_required(login_url='login')
@user_passes_test(is_customer)
def client_galerie(request):
    designs = Design.objects.all()
    return render(request, 'Client/client_galerie.html', {'designs': designs})

@login_required(login_url='login')
@user_passes_test(is_customer)
def ajout_produits(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    categories_produit = CategoryProduit.objects.all()
    categories_design = CategoryDesign.objects.all()
    
    # Filtrer les produits par catégorie de produit si sélectionnée
    produits = Produit.objects.all()
    category_produit_id = request.GET.get('category_produit')
    if category_produit_id:
        produits = produits.filter(type_id=category_produit_id)
    
    # Filtrer par catégorie de design si sélectionnée (optionnel, basé sur le design)
    category_design_id = request.GET.get('category_design')
    if category_design_id:
        produits = produits.filter(produitcommande__category_design_id=category_design_id).distinct()

    context = {
        'design': design,
        'categories_produit': categories_produit,
        'categories_design': categories_design,
        'produits': produits,
        'category_produit_selected': category_produit_id,
        'category_design_selected': category_design_id,
    }
    return render(request, 'Client/ajout_produits.html', context)

class FiltrerProduitsView(APIView):
    def get(self, request):
        category_produit_id = request.query_params.get('category_produit_id')
        category_design_id = request.query_params.get('category_design_id')
        produits = Produit.objects.all()
        if category_produit_id:
            produits = produits.filter(type_id=category_produit_id)
        if category_design_id:
            produits = produits.filter(produitcommande__category_design_id=category_design_id).distinct()
        return Response(list(produits.values('id', 'nom')), status=status.HTTP_200_OK)

@login_required(login_url='login')
@user_passes_test(is_customer)
def enregistrer_commande(request):
    if request.method == 'POST':
        design_id = request.POST.get('design_id')
        produit_ids = request.POST.getlist('produits')
        category_design_id = request.POST.get('category_design')
        
        design = get_object_or_404(Design, id=design_id)
        category_design = get_object_or_404(CategoryDesign, id=category_design_id) if category_design_id else None

        # Créer une nouvelle commande
        commande = Commande.objects.create(
            created_by=request.user.client,
            category=design,
        )

        # Ajouter les produits sélectionnés (quantité fixée à 1, pour le superviseur)
        total_budget = 0
        for produit_id in produit_ids:
            produit = get_object_or_404(Produit, id=produit_id)
            quantite = 1  # Quantité fixée à 1, modifiable par le superviseur
            prix = produit.prix * quantite
            ProduitCommande.objects.create(
                produit=produit,
                commande=commande,
                design=design,
                category_design=category_design,
                quantite=quantite,
                prix=prix
            )
            total_budget += prix

        # Mise à jour du budget total
        commande.budget = total_budget
        commande.save()

        messages.success(request, "Commande soumise avec succès. La quantité sera définie par le superviseur.")
        return redirect('client_orders')
    return redirect('client_galerie')

@login_required(login_url='login')
@user_passes_test(is_customer)
def client_orders(request):
    client = request.user.client
    orders = Commande.objects.filter(created_by=client).order_by('-created_at')
    return render(request, 'Client/client_orders.html', {'orders': orders})

@csrf_exempt
def annuler_commande(request, order_id):
    if request.method == "POST":
        try:
            commande = get_object_or_404(Commande, id=order_id)
            commande.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})

@csrf_exempt
def select_category(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category = data.get("category")

            commande = get_object_or_404(Commande, id=order_id)
            commande.category.nom = category
            commande.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})


@login_required(login_url='login')
@user_passes_test(is_customer)
def panier(request):
    client = request.user.client
    cart_items = ProduitCommande.objects.filter(created_by=client).order_by('id')
    categories = {}
    for item in cart_items:
        cat = item.produit.nom
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    total_price = sum(item.produit.prix for item in cart_items)
    return render(request, 'Client/panier.html', {'categories': categories, 'total_price': total_price})

@login_required(login_url='login')
@user_passes_test(is_customer)
def paiement(request):
    return render(request, 'Client/paiement.html')
@login_required(login_url='login')
@user_passes_test(is_customer)
def visite_local(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        if montant:
            paiement = Paiement.objects.create(
                type_paiement=TypePaiement.objects.get(nom='Visite du local'),
                montant=montant,
                created_by=request.user,
                commande=True
            )
            ListeAttente.objects.create(
                created_by=request.user,
                client=request.user.client,
                done=False
            )
            return redirect('superviseur_dashboard')
    return render(request, 'Client/visite_local.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def visite_paiement(request):
    """
    Vue pour gérer le paiement de la visite du local avec PayPal
    """
    if request.method == 'POST':
        # Utiliser PayPal pour le paiement
        amount = 100000  
        description = "Paiement pour visite du local"
        custom_data = f"visite_{request.user.id}"
        
        return create_paypal_payment(request, 'visite', amount, description, custom_data)
    
    return render(request, 'Client/visite_paiement.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def budget_avance_paiement(request):
    """
    Vue pour gérer le paiement du budget d'avance avec PayPal
    """
    if request.method == 'POST':
        # Utiliser PayPal pour le paiement
        amount = 500000  
        description = "Paiement du budget d'avance"
        custom_data = f"avance_{request.user.id}"
        
        return create_paypal_payment(request, 'avance', amount, description, custom_data)
    
    return render(request, 'Client/budget_avance_paiement.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def budget_final_paiement(request):
    """
    Vue pour gérer le paiement du budget final avec PayPal
    """
    # Calculs existants...
    cout_total = 50000000
    budget_avance = 25000000
    visite_payee = 100000
    autres_frais = 500000
    tva = int((cout_total - budget_avance - visite_payee + autres_frais) * 0.18)
    montant_final = cout_total - budget_avance - visite_payee + autres_frais + tva
    
    context = {
        'cout_total': cout_total,
        'budget_avance': budget_avance,
        'visite_payee': visite_payee,
        'autres_frais': autres_frais,
        'tva': tva,
        'montant_final': montant_final,
    }
    
    if request.method == 'POST':
        # Utiliser PayPal pour le paiement final
        amount = montant_final
        description = "Paiement final du projet de rénovation"
        custom_data = f"final_{request.user.id}"
        
        return create_paypal_payment(request, 'final', amount, description, custom_data)
    
    return render(request, 'Client/budget_final_paiement.html', context)

@login_required(login_url='login')
@user_passes_test(is_customer)
def versement_budget_final(request):
    """
    Vue pour gérer les versements du budget final par virement bancaire
    """
    # Calculs des montants
    cout_total = 50000000
    budget_avance = 25000000
    visite_payee = 100000
    autres_frais = 500000
    tva = int((cout_total - budget_avance - visite_payee + autres_frais) * 0.18)
    montant_final = cout_total - budget_avance - visite_payee + autres_frais + tva
    
    # Récupérer le dernier projet du client
    try:
        projet = SuppervisionTravaux.objects.filter(client=request.user).last()
    except:
        projet = None
    
    context = {
        'montant_final': montant_final,
        'projet': projet,
    }
    
    if request.method == 'POST':
        justificatif = request.FILES.get('justificatif')
        reference = request.POST.get('reference')
        commentaire = request.POST.get('commentaire', '')
        
        if justificatif and reference:
            try:
                # Validation de la taille du fichier
                if justificatif.size > 10 * 1024 * 1024:  # 10MB
                    return JsonResponse({
                        'success': False,
                        'message': 'Le fichier est trop volumineux. Taille maximale: 10MB'
                    })
                
                # Créer le type de paiement
                type_paiement_obj, created = TypePaiement.objects.get_or_create(
                    nom='Budget final - Virement'
                )
                
                # Créer le paiement
                paiement = Paiement.objects.create(
                    type_paiement=type_paiement_obj,
                    montant=montant_final,
                    created_by=request.user,
                    commande=None
                )
                
                # Créer la facture
                montant_ht = montant_final / 1.18
                tva_amount = montant_ht * 0.18
                
                facture = Facture.objects.create(
                    paiement=paiement,
                    client=request.user.client,
                    montant_ht=montant_ht,
                    tva=tva_amount,
                    montant_ttc=montant_final,
                    statut='EMISE',
                    description="Solde final du projet de rénovation complète - Honoraires, matériaux et finitions (Virement bancaire)",
                    reference_virement=reference,
                    commentaire_virement=commentaire
                )
                
                # Sauvegarder le justificatif
                JustificatifPaiement.objects.create(
                    facture=facture,
                    fichier=justificatif,
                    type_paiement='virement_final'
                )
                
                # Créer ou mettre à jour RenovationFaite avec le justificatif
                renovation, created = RenovationFaite.objects.get_or_create(
                    client=request.user,
                    defaults={
                        'budget2': paiement,
                        'description': 'Rénovation finalisée - Paiement final reçu',
                        'justificatif': justificatif
                    }
                )
                if not created:
                    renovation.justificatif = justificatif
                    renovation.save()
                
                # Envoyer une notification (exemple)
                envoyer_notification_validation(request, facture)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Justificatif de paiement final uploadé avec succès! Votre paiement sera vérifié sous 24h.',
                    'facture_numero': facture.numero,
                    'facture_id': facture.id,
                    'redirect_url': reverse('detail_facture', args=[facture.id])
                })
                
            except Exception as e:
                logger.error(f"Erreur versement budget final: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors du traitement: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Veuillez remplir tous les champs obligatoires.'
            })
    
    return render(request, 'Client/versement_budget_final.html', context)

def envoyer_notification_validation(request, facture):
    """
    Envoyer une notification pour validation du virement
    (À implémenter selon vos besoins - email, notification interne, etc.)
    """
    try:
        # Exemple d'envoi d'email aux administrateurs
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"Nouveau justificatif de paiement - {facture.numero}"
        message = f"""
        Un nouveau justificatif de paiement a été uploadé :
        
        Facture: {facture.numero}
        Client: {facture.client.get_name}
        Montant: {facture.montant_ttc} BIF
        Référence: {facture.reference_virement}
        
        Veuillez valider le paiement dans l'interface d'administration.
        """
        
        # send_mail(
        #     subject,
        #     message,
        #     settings.DEFAULT_FROM_EMAIL,
        #     ['gastephane0@gmail.com'],
        #     fail_silently=True,
        # )
        
        # Pour l'instant, on log juste
        print(f"Notification: {message}")
        
    except Exception as e:
        logger.error(f"Erreur envoi notification: {str(e)}")

@login_required(login_url='login')
def liste_factures(request):
    """Liste des factures pour un client"""
    if is_customer(request.user):
        factures = Facture.objects.filter(client=request.user.client).order_by('-date_emission')
    elif is_admin(request.user) or is_supervisor(request.user):
        factures = Facture.objects.all().order_by('-date_emission')
    else:
        factures = Facture.objects.none()

    context = {
        'factures': factures
    }
    return render(request, 'Client/liste_factures.html', context)

@login_required(login_url='login')
def detail_facture(request, facture_id):
    """Détail d'une facture"""
    facture = get_object_or_404(Facture, id=facture_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette facture
    if is_customer(request.user) and facture.client != request.user.client:
        return HttpResponseForbidden("Vous n'avez pas accès à cette facture.")
    
    context = {
        'facture': facture
    }
    return render(request, 'Client/detail_facture.html', context)

@login_required(login_url='login')
def telecharger_facture_pdf(request, facture_id):
    """Télécharger la facture en PDF"""
    facture = get_object_or_404(Facture, id=facture_id)
    
    # Vérifier les permissions
    if is_customer(request.user) and facture.client != request.user.client:
        return HttpResponseForbidden("Vous n'avez pas accès à cette facture.")
    
    # Générer le HTML
    html_string = render_to_string('Client/facture_pdf.html', {'facture': facture})
    
    # Créer un PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    
    # Créer la réponse
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
    
    return response

@login_required(login_url='login')
@user_passes_test(is_customer)
def view_profile(request):
    try:
        client = request.user.client
    except Client.DoesNotExist:
        return render(request, 'Client/error.html', {'message': "Aucun profil client trouvé pour cet utilisateur."})
    return render(request, 'Client/view_profile.html', {'client': client})


@login_required(login_url='login')
@user_passes_test(is_customer)
def edit_profile_view(request):
    """
    Permet à un client de modifier son profil, incluant les informations utilisateur et client.
    
    Args:
        request: L'objet HttpRequest contenant les données de la requête.
    
    Returns:
        HttpResponse: Rendu de la page 'Client/edit_profile.html' avec les formulaires, ou redirection après succès.
    """
    try:
        client = request.user.client
        user = client.user
        if request.method == 'POST':
            userForm = ClientUserForm(request.POST, instance=user)
            clientForm = ClientForm(request.POST, request.FILES, instance=client)
            if userForm.is_valid() and clientForm.is_valid():
                user = userForm.save(commit=False)
                password = userForm.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                clientForm.save()
                messages.success(request, "Profil mis à jour avec succès.")
                return redirect('view_profile')
            else:
                messages.error(request, "Erreur dans le formulaire. Veuillez corriger les champs.")
                for field in userForm:
                    if field.errors:
                        messages.error(request, f"{field.label}: {field.errors.as_text()}")
                for field in clientForm:
                    if field.errors:
                        messages.error(request, f"{field.label}: {field.errors.as_text()}")
        else:
            userForm = ClientUserForm(instance=user)
            clientForm = ClientForm(instance=client)
        return render(request, 'Client/edit_profile.html', {'userForm': userForm, 'clientForm': clientForm})
    except Client.DoesNotExist:
        messages.error(request, "Aucun profil client trouvé pour cet utilisateur.")
        return redirect('view_profile')
    except Exception as e:
        messages.error(request, f"Une erreur inattendue est survenue : {str(e)}")
        return redirect('view_profile')    

# @login_required(login_url='login')
# @user_passes_test(is_customer)
# def notifications(request):
#     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'notifications.html', {'notifications': notifications})


# --------------------------------------------------------------------------------------------------------------
# ------- A D M I N   D A S H B O A R D ------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url='login')
@user_passes_test(is_admin)
def admindashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_accounts(request):
    pending_users = User.objects.filter(is_active=False, client__is_rejected=False)
    return render(request, 'approve_accounts.html', {'pending_users': pending_users})

@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    client = getattr(user, 'client', None)  # Vérifier si l'utilisateur a un profil client
    if request.method == 'POST' and client:
        action = request.POST.get('action')
        if action == 'approve':
            user.is_active = True
            client.is_rejected = False
        elif action == 'reject':
            user.is_active = False
            client.is_rejected = True
        user.save()
        client.save()  # Sauvegarder aussi le client
    return redirect('manage_accounts')



def generate_color_from_id(obj_id):
    """Génère une couleur unique à partir de l'ID de l'objet."""
    hash_object = hashlib.md5(str(obj_id).encode())  # Crée un hash MD5 de l'ID
    hex_dig = hash_object.hexdigest()  # Obtenir la représentation hexadécimale
    return f"#{hex_dig[:6]}"  # Utiliser les 6 premiers caractères pour une couleur hexadécimale

@login_required(login_url='login')
@user_passes_test(is_admin)
def statistics(request):
    # Nombre de clients et commandes
    nombre_clients = Client.objects.count()
    nombre_commandes = Commande.objects.count()
    
    # Calcul du total des ventes
    total_ventes = Paiement.objects.aggregate(Sum('montant'))['montant__sum'] or 0

    # Analyse des ventes par catégorie de design
    ventes_par_categorie = {}
    for cat in Design.objects.all():
        # Total des ventes pour chaque design (calculé en fonction des produits associés aux commandes)
        total_ventes_design = ProduitCommande.objects.filter(design=cat).aggregate(Sum('prix'))['prix__sum'] or 0
        ventes_par_categorie[cat] = total_ventes_design

    # Générer des couleurs dynamiques pour chaque design
    couleurs = [generate_color_from_id(cat.id) for cat in ventes_par_categorie.keys()]

    context = {
        'nombre_clients': nombre_clients,
        'nombre_commandes': nombre_commandes,
        'total_ventes': total_ventes,
        'ventes_par_categorie': ventes_par_categorie,
        'couleurs': couleurs,
    }
    return render(request, 'statistics.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_stock(request):
    stocks = Stock.objects.all().order_by('-created_at')
    context = {
        'stocks': stocks
    }
    return render(request, 'manage_stock.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)

            # Vérification de l'authentification
            if request.user.is_authenticated:
                stock.created_by = request.user  # Assigner l'objet User
            else:
                return HttpResponse("Erreur : utilisateur non authentifié", status=400)

            stock.quantite_actuelle = form.cleaned_data['quantite_initiale']
            stock.save()

            return redirect('manage_stock')

    else:
        form = StockForm()

    return render(request, 'add_stock.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(is_admin)
def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_by = request.user  #  On garde le bon utilisateur
            stock.save()
            return redirect('manage_stock')
    else:
        form = StockForm(instance=stock)

    return render(request, 'edit_stock.html', {'form': form, 'stock': stock})


@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    #  Vérification des droits avant suppression
    if stock.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer ce stock.")

    if request.method == 'POST':
        stock.delete()
        return redirect('manage_stock')

    return render(request, 'delete_stock.html', {'stock': stock})


@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_payments(request):
    paiements = Paiement.objects.all().order_by('-created_at')
    context = {'paiements': paiements}
    return render(request, 'manage_payments.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_orders(request):
    orders = (
        Commande.objects
        .select_related('created_by__user', 'category')
        .prefetch_related('produitcommande_set__produit__type')
        .annotate(total_price=Sum('produitcommande__prix'))
        .order_by('-created_at')
    )
    return render(request, 'admin_orders.html', {'orders': orders})


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_completed_works(request):
    """
    Vue pour afficher tous les travaux finalisés avec le client et le superviseur
    """
    # Récupérer les rénovations terminées (done=True)
    completed_renovations = (
        RenovationFaite.objects
        .filter(done=True)
        .select_related('client', 'budget2__created_by')
        .order_by('-created_at')
    )
    
    # Récupérer aussi les projets de supervision
    supervision_projects = (
        SuppervisionTravaux.objects
        .select_related('client', 'budget1__created_by')
        .order_by('-created_at')
    )
    
    context = {
        'completed_renovations': completed_renovations,
        'supervision_projects': supervision_projects,
    }
    return render(request, 'admin_completed_works.html', context)


def configure_paypal():
    """Configuration de PayPal"""
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET
    })

# Nouvelle vue pour créer un paiement PayPal
@login_required(login_url='login')
def create_paypal_payment(request, payment_type, amount, description, custom_data):
    """Créer un paiement PayPal et rediriger vers l'approbation"""
    configure_paypal()
    
    # Générer un ID unique pour la commande
    order_id = f"{payment_type}_{request.user.id}"
    
    # Préparer les URLs de retour
    return_url = request.build_absolute_uri(
        reverse('execute_paypal_payment', kwargs={'payment_type': payment_type})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payment_cancel')
    )
    
    # Créer le paiement PayPal
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "BIF"
            },
            "description": description,
            "custom": custom_data,
            "invoice_number": order_id
        }],
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    })
    
    if payment.create():
        # Sauvegarder les informations en session
        request.session['payment_id'] = payment.id
        request.session['payment_type'] = payment_type
        request.session['order_id'] = order_id
        request.session['amount'] = amount
        
        # Rediriger vers PayPal
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    
    # En cas d'erreur
    messages.error(request, f"Erreur lors de la création du paiement: {payment.error}")
    return redirect('payment_error')

# Vue pour exécuter le paiement après retour de PayPal
@login_required(login_url='login')
@csrf_exempt
def execute_paypal_payment(request, payment_type):
    """Exécuter le paiement après retour de PayPal et créer la facture"""
    configure_paypal()
    
    payment_id = request.session.get('payment_id')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, "Paramètres de paiement manquants")
        return redirect('payment_error')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        # Paiement réussi
        order_id = request.session.get('order_id')
        amount = request.session.get('amount')
        
        try:
            # Créer le type de paiement
            type_paiement_obj, created = TypePaiement.objects.get_or_create(
                nom=payment_type.capitalize()
            )
            
            # Créer le paiement
            paiement = Paiement.objects.create(
                type_paiement=type_paiement_obj,
                montant=float(amount) * 7000,  # Conversion USD vers BIF
                created_by=request.user,
                commande=None
            )
            
            # CRÉER LA FACTURE
            montant_ht = float(amount) / 1.18
            tva = montant_ht * 0.18
            
            facture = Facture.objects.create(
                paiement=paiement,
                client=request.user.client,
                montant_ht=montant_ht,
                tva=tva,
                montant_ttc=montant_ht + tva,
                statut='PAYEE',
                paypal_payment_id=payment_id,
                paypal_transaction_id=payment.transactions[0].related_resources[0].sale.id,
                description=get_description_paiement(payment_type)
            )
            
            # Actions spécifiques selon le type de paiement
            if payment_type == 'visite':
                ListeAttente.objects.create(
                    created_by=request.user,
                    client=request.user.client,
                    done=False
                )
                success_url = 'liste_projet'
            elif payment_type == 'avance':
                success_url = 'liste_renovation'
            elif payment_type == 'final':
                success_url = 'paiement_success'
            
            # Nettoyer la session
            request.session.pop('payment_id', None)
            request.session.pop('payment_type', None)
            request.session.pop('order_id', None)
            request.session.pop('amount', None)
            
            messages.success(request, f"Paiement effectué avec succès! Facture {facture.numero} générée.")
            return redirect(success_url, type_paiement=payment_type)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
            return redirect('payment_error')
    else:
        messages.error(request, f"Erreur lors du paiement: {payment.error}")
        return redirect('payment_error')

@login_required(login_url='login')
def payment_cancel(request):
    """Annulation du paiement"""
    # Nettoyer la session
    request.session.pop('payment_id', None)
    request.session.pop('payment_type', None)
    request.session.pop('order_id', None)
    request.session.pop('amount', None)
    
    messages.info(request, "Paiement annulé. Vous pouvez réessayer quand vous le souhaitez.")
    return render(request, 'Client/payment_cancel.html')

@login_required(login_url='login')
def payment_error(request):
    """Erreur de paiement"""
    return render(request, 'Client/payment_error.html')

def paiement_success(request, type_paiement):
    return render(request, 'Client/paiement_success.html', {'type_paiement': type_paiement})

def error(request):
    return render(request, 'Client/error.html', {'message': 'Une erreur est survenue.'})


@login_required(login_url='login')
@user_passes_test(is_admin)
def tableau_bord_factures(request):
    """Tableau de bord des factures pour l'admin"""
    total_factures = Facture.objects.count()
    factures_payees = Facture.objects.filter(statut='PAYEE').count()
    factures_impayees = Facture.objects.filter(statut='EMISE').count()
    factures_retard = Facture.objects.filter(statut='EMISE', date_echeance__lt=timezone.now()).count()
    
    chiffre_affaires = Facture.objects.filter(statut='PAYEE').aggregate(
        total=Sum('montant_ttc')
    )['total'] or 0
    
    context = {
        'total_factures': total_factures,
        'factures_payees': factures_payees,
        'factures_impayees': factures_impayees,
        'factures_retard': factures_retard,
        'chiffre_affaires': chiffre_affaires,
    }
    return render(request, 'admin_tableau_bord_factures.html', context)


def get_description_paiement(payment_type):
    """Retourne la description selon le type de paiement"""
    descriptions = {
        'visite': "Visite du local et évaluation technique - Frais de déplacement et expertise",
        'avance': "Budget d'avance pour le démarrage des travaux de rénovation",
        'final': "Solde final du projet de rénovation complète - Honoraires et matériaux"
    }
    return descriptions.get(payment_type, "Paiement de services de rénovation")

@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_produit(request):
    return render(request, 'manage_produit.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def afficher_produit(request):
    produits = Produit.objects.all()
    cat = CategoryProduit.objects.all()

    # Moteur de recherche
    query = request.GET.get('q', '')
    if query:
        produits = produits.filter(nom__icontains=query)
        cat = cat.filter(nom__icontains=query)

    # Passer les données au template
    context = {
        'produits': produits,
        'cat': cat,
        'query': query,
    }
    return render(request, 'afficher_produit.html', context)

# Vue pour ajouter un produit via AJAX
@csrf_exempt
def add_produit(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Produit ajouté avec succès'})
        return JsonResponse({'success': False, 'errors': form.errors})  

    form = ProduitForm()
    categories = CategoryProduit.objects.all()
    return render(request, 'add_produit.html', {'categories_produit': categories, 'form': form})

# Vue pour filtrer les produits par catégorie
@login_required(login_url='login')
@user_passes_test(is_admin)
def filtrer_produit(request):
    categories = CategoryProduit.objects.all()
    produits = Produit.objects.all()  # Tous les produits au départ

    return render(request, 'filtrer_produit.html', {
        'categories_produit': categories,
        'produits_all': produits
    })

# Vue AJAX pour récupérer les produits d'une catégorie sélectionnée
@user_passes_test(is_admin)
def get_products_by_category(request):
    category_id = request.GET.get("category_id")

    if category_id:
        try:
            produits = Produit.objects.filter(type_id=int(category_id))
        except ValueError:
            return JsonResponse({"error": "ID de catégorie invalide"}, status=400)
    else:
        produits = Produit.objects.all()
    
    data = {"produits": [{"id": p.id, "nom": p.nom, "unite": p.unite, "prix": p.prix} for p in produits]}
    return JsonResponse(data)

# Vue pour modifier un produit
@login_required(login_url='login')
@user_passes_test(is_admin)
def edit_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('filtrer_produit')  # Redirige après modification
    else:
        form = ProduitForm(instance=produit)

    return render(request, 'edit_produit.html', {'form': form, 'produit': produit})


# Vue pour supprimer un produit via AJAX
@csrf_exempt
def delete_produit(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        produit_id = request.POST.get('produit_id')
        produit = get_object_or_404(Produit, id=produit_id)
        produit.delete()
        return JsonResponse({'success': True, 'message': 'Produit supprimé avec succès'})
    return JsonResponse({'success': False, 'message': 'Requête invalide'})


@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_design(request):
    return render(request, 'manage_design.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def feedbacks(request):
    """
    Vue pour gérer les messages de contact (feedbacks)
    """
    from django.db.models import Q
    from datetime import datetime, date
    
    # Récupérer tous les messages
    messages = Contact.objects.all().order_by('-created_at')
    
    # Appliquer les filtres
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    name_filter = request.GET.get('name')
    
    if status_filter == 'read':
        messages = messages.filter(is_read=True)
    elif status_filter == 'unread':
        messages = messages.filter(is_read=False)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            messages = messages.filter(created_at__date=filter_date)
        except ValueError:
            pass
    
    if name_filter:
        messages = messages.filter(
            Q(name__icontains=name_filter) | Q(email__icontains=name_filter)
        )
    
    # Calculer les statistiques
    total_messages = Contact.objects.count()
    read_messages = Contact.objects.filter(is_read=True).count()
    unread_messages = Contact.objects.filter(is_read=False).count()
    today_messages = Contact.objects.filter(created_at__date=date.today()).count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(messages, 10)  # 10 messages par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'messages': page_obj,
        'total_messages': total_messages,
        'read_messages': read_messages,
        'unread_messages': unread_messages,
        'today_messages': today_messages,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'name_filter': name_filter,
    }
    
    return render(request, 'feedbacks.html', context)

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(is_admin)
def mark_message_read(request, message_id):
    """
    Vue AJAX pour marquer un message comme lu
    """
    if request.method == 'POST':
        try:
            message = get_object_or_404(Contact, id=message_id)
            message.is_read = True
            message.save()
            return JsonResponse({'success': True, 'message': 'Message marqué comme lu'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(is_admin)
def mark_message_unread(request, message_id):
    """
    Vue AJAX pour marquer un message comme non lu
    """
    if request.method == 'POST':
        try:
            message = get_object_or_404(Contact, id=message_id)
            message.is_read = False
            message.save()
            return JsonResponse({'success': True, 'message': 'Message marqué comme non lu'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_message(request, message_id):
    """
    Vue AJAX pour supprimer un message
    """
    if request.method == 'POST':
        try:
            message = get_object_or_404(Contact, id=message_id)
            message.delete()
            return JsonResponse({'success': True, 'message': 'Message supprimé avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(is_admin)
def mark_all_messages_read(request):
    """
    Vue AJAX pour marquer tous les messages comme lus
    """
    if request.method == 'POST':
        try:
            Contact.objects.filter(is_read=False).update(is_read=True)
            return JsonResponse({'success': True, 'message': 'Tous les messages ont été marqués comme lus'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def afficher_design(request):
    # Récupérer tous les designs
    designs = Design.objects.all()

    # Moteur de recherche
    query = request.GET.get('q', '')
    if query:
        designs = designs.filter(nom__icontains=query)

    # Passer les données au template
    context = {
        'designs': designs,
        'query': query,
    }
    return render(request, 'afficher_design.html', context)

@csrf_exempt
def add_design(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = DesignForm(request.POST, request.FILES)  # Prend en charge les fichiers
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Design ajouté avec succès'})
        return JsonResponse({'success': False, 'errors': form.errors})

    form = DesignForm()
    return render(request, 'add_design.html', {'form': form})


# -------------------------------------------------------------------------------------------------------------
# ------- S U P E R V I S E U R  D A S H B O A R D ------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def superviseurdashboard(request):
    return render(request, 'superviseur_dashboard.html')

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def manage_liste_attente(request):
    if request.method == 'POST':
        form = ListeAttenteForm(request.POST)
        if form.is_valid():
            liste_attente = form.save(commit=False)
            liste_attente.created_by = request.user
            liste_attente.save()
            return redirect('liste_attente_detail', liste_attente_id=liste_attente.id)
    else:
        form = ListeAttenteForm()
    return render(request, 'manage_liste_attente.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def liste_attente(request):
    liste_attentes = ListeAttente.objects.all().order_by('-created_at')
    context = {
        'liste_attentes': liste_attentes,
    }
    return render(request, 'liste_attente.html', context)

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def liste_attente_detail(request, liste_attente_id):
    liste_attente = get_object_or_404(ListeAttente, id=liste_attente_id)
    return render(request, 'liste_attente_detail.html', {'liste_attente': liste_attente})

@login_required(login_url='login')
@user_passes_test(is_customer)
def upload_visite_justificatif(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Méthode non autorisée")

    fichier = request.FILES.get('justificatif')
    if not fichier:
        return JsonResponse({'success': False, 'message': 'Aucun fichier reçu.'})

    # Créer ou récupérer l'entrée de liste d'attente pour ce client
    liste_attente, _ = ListeAttente.objects.get_or_create(
        client=request.user.client,
        done=False,
        defaults={'created_by': request.user}
    )

    liste_attente.justificatif = fichier
    liste_attente.save()

    return JsonResponse({
        'success': True,
        'message': 'Preuve de paiement uploadée.',
        'liste_attente_id': liste_attente.id,
    })

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def mark_liste_attente_done(request, liste_attente_id):
    liste_attente = get_object_or_404(ListeAttente, id=liste_attente_id)
    if request.method == 'POST':
        liste_attente.done = True
        liste_attente.save()
        return redirect('liste_attente_detail', liste_attente_id=liste_attente_id)
    return render(request, 'confirm_mark_done.html', {'liste_attente': liste_attente})

@login_required(login_url='login')
@user_passes_test(is_customer)
def upload_avance_justificatif(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Méthode non autorisée")

    fichier = request.FILES.get('justificatif')
    if not fichier:
        return JsonResponse({'success': False, 'message': 'Aucun fichier reçu.'})

    # Validation de la taille du fichier (5MB max)
    if fichier.size > 5 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'Le fichier est trop volumineux. Taille maximale: 5MB'
        })

    # Créer ou récupérer l'entrée de supervision pour ce client
    # Note: Vous devrez peut-être créer un Paiement temporaire ou adapter cette logique
    try:
        # Vérifier si le client a déjà un projet en cours
        projet = SuppervisionTravaux.objects.filter(
            client=request.user
        ).order_by('-created_at').first()
        
        if not projet:
            # Créer un type de paiement pour l'avance si nécessaire
            type_paiement_avance, _ = TypePaiement.objects.get_or_create(
                nom='Budget avance - Virement'
            )
            
            # Créer un paiement temporaire (montant à ajuster selon votre logique)
            paiement_avance = Paiement.objects.create(
                type_paiement=type_paiement_avance,
                montant=25000000,  
                created_by=request.user,
                commande=None
            )
            
            # Créer un nouveau projet
            projet = SuppervisionTravaux.objects.create(
                client=request.user,
                budget1=paiement_avance,
                description="Projet en attente de validation du budget d'avance"
            )
        
        # Attacher le justificatif
        projet.justificatif = fichier
        projet.save()

        return JsonResponse({
            'success': True,
            'message': 'Preuve de paiement uploadée avec succès!',
            'projet_id': projet.id,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors du traitement: {str(e)}'
        })


@login_required(login_url='login')
@user_passes_test(is_customer)
def upload_final_justificatif(request):
    if request.method != 'POST':
        return HttpResponseNotFound("Méthode non autorisée")

    fichier = request.FILES.get('justificatif')
    if not fichier:
        return JsonResponse({'success': False, 'message': 'Aucun fichier reçu.'})

    # Validation de la taille du fichier (10MB max pour le paiement final)
    if fichier.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': 'Le fichier est trop volumineux. Taille maximale: 10MB'
        })

    # Créer ou récupérer l'entrée de rénovation pour ce client
    try:
        # Vérifier si le client a déjà une rénovation en cours
        renovation = RenovationFaite.objects.filter(
            client=request.user
        ).order_by('-created_at').first()
        
        if not renovation:
            # Créer un type de paiement pour le final si nécessaire
            type_paiement_final, _ = TypePaiement.objects.get_or_create(
                nom='Budget final - Virement'
            )
            
            # Créer un paiement temporaire (montant à ajuster selon votre logique)
            paiement_final = Paiement.objects.create(
                type_paiement=type_paiement_final,
                montant=30000000,  
                created_by=request.user,
                commande=None
            )
            
            # Créer une nouvelle rénovation
            renovation = RenovationFaite.objects.create(
                client=request.user,
                budget2=paiement_final,
                description="Rénovation en attente de validation du budget final"
            )
        
        # Attacher le justificatif
        renovation.justificatif = fichier
        renovation.save()

        return JsonResponse({
            'success': True,
            'message': 'Preuve de paiement final uploadée avec succès!',
            'renovation_id': renovation.id,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors du traitement: {str(e)}'
        })

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def liste_renovation(request):
    renovations = RenovationFaite.objects.all().order_by('-id')  # Tri par ID décroissant pour les plus récentes d'abord
    context = {
        'renovations': renovations,
    }
    return render(request, 'liste_renovation.html', context)

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def renovation_detail(request, renovation_id):
    renovation = get_object_or_404(RenovationFaite, id=renovation_id)
    return render(request, 'renovation_detail.html', {'renovation': renovation})

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def mark_renovation_done(request, renovation_id):
    renovation = get_object_or_404(RenovationFaite, id=renovation_id)
    if request.method == 'POST':
        # Si 'done' n'est pas dans le modèle, peut-être ajouter un champ booléen pour indiquer la fin des travaux
        renovation.done = True
        renovation.save()
        return redirect('renovation_detail', renovation_id=renovation_id)
    return render(request, 'confirm_renovation_done.html', {'renovation': renovation})

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def liste_projet(request):
    projets = SuppervisionTravaux.objects.all().order_by('-id')  # Tri par ID décroissant pour les plus récentes d'abord
    context = {
        'projets': projets,
    }
    return render(request, 'liste_projet.html', context)

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def projet_detail(request, projet_id):
    projet = get_object_or_404(SuppervisionTravaux, id=projet_id)
    return render(request, 'orojet_detail.html', {'projet': projet})

@login_required(login_url='login')
@user_passes_test(is_supervisor)
def mark_projet_done(request, projet_id):
    projet = get_object_or_404(SuppervisionTravaux, id=projet_id)
    if request.method == 'POST':
        # Si 'done' n'est pas dans le modèle, peut-être ajouter un champ booléen pour indiquer la fin des travaux
        projet.done = True
        projet.save()
        return redirect('projet_detail', projet_id=projet_id)
    return render(request, 'confirm_projet_done.html', {'projet': projet})