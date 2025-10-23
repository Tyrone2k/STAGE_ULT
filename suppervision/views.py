from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.http import JsonResponse, HttpResponseNotFound
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
from django.utils import timezone
from django.contrib import messages
# import geocoder

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
    Vue pour gérer le paiement de la visite du local
    """
    if request.method == 'POST':
        # Traitement du paiement PayPal ou virement bancaire
        type_paiement = request.POST.get('type_paiement')
        montant = request.POST.get('montant', 50)  # Montant par défaut pour la visite
        
        try:
            # Créer le type de paiement s'il n'existe pas
            type_paiement_obj, created = TypePaiement.objects.get_or_create(
                nom='Visite du local'
            )
            
            # Créer un paiement temporaire (sans commande pour l'instant)
            paiement = Paiement.objects.create(
                type_paiement=type_paiement_obj,
                montant=montant,
                created_by=request.user,
                commande=None  # Pas de commande associée pour la visite
            )
            
            # Ajouter à la liste d'attente
            ListeAttente.objects.create(
                created_by=request.user,
                client=request.user.client,
                done=False
            )
            
            messages.success(request, "Paiement de la visite enregistré avec succès!")
            return redirect('liste_projet')
            
        except Exception as e:
            messages.error(request, f"Erreur lors du traitement du paiement: {str(e)}")
    
    return render(request, 'Client/visite_paiement.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def budget_avance_paiement(request):
    """
    Vue pour gérer le paiement du budget d'avance
    """
    if request.method == 'POST':
        # Traitement du paiement PayPal ou virement bancaire
        type_paiement = request.POST.get('type_paiement')
        montant = request.POST.get('montant', 500)  # Montant par défaut pour l'avance
        
        try:
            # Créer le type de paiement s'il n'existe pas
            type_paiement_obj, created = TypePaiement.objects.get_or_create(
                nom='Budget d\'avance'
            )
            
            # Créer un paiement temporaire (sans commande pour l'instant)
            paiement = Paiement.objects.create(
                type_paiement=type_paiement_obj,
                montant=montant,
                created_by=request.user,
                commande=None  # Pas de commande associée pour l'avance
            )
            
            messages.success(request, "Paiement du budget d'avance enregistré avec succès!")
            return redirect('liste_renovation')
            
        except Exception as e:
            messages.error(request, f"Erreur lors du traitement du paiement: {str(e)}")
    
    return render(request, 'Client/budget_avance_paiement.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def budget_final_paiement(request):
    """
    Vue pour gérer le paiement du budget final
    """
    # Récupérer les informations de paiement du client
    client = request.user.client
    
    # Calculer les montants (exemple de calcul)
    cout_total = 10000  # Coût total du projet
    budget_avance = 2000  # Budget d'avance déjà payé
    visite_payee = 50  # Visite déjà payée
    autres_frais = 500  # Autres frais
    tva = int((cout_total - budget_avance - visite_payee + autres_frais) * 0.18)  # TVA 18%
    montant_final = cout_total - budget_avance - visite_payee + autres_frais + tva
    montant_final_usd = round(montant_final / 2000, 2)  # Conversion approximative BIF vers USD
    
    context = {
        'cout_total': cout_total,
        'budget_avance': budget_avance,
        'visite_payee': visite_payee,
        'autres_frais': autres_frais,
        'tva': tva,
        'montant_final': montant_final,
        'montant_final_usd': montant_final_usd,
    }
    
    if request.method == 'POST':
        # Traitement du paiement PayPal
        try:
            # Créer le type de paiement s'il n'existe pas
            type_paiement_obj, created = TypePaiement.objects.get_or_create(
                nom='Budget final'
            )
            
            # Créer un paiement temporaire
            paiement = Paiement.objects.create(
                type_paiement=type_paiement_obj,
                montant=montant_final,
                created_by=request.user,
                commande=None  # Pas de commande associée pour le budget final
            )
            
            messages.success(request, "Paiement du budget final enregistré avec succès!")
            return redirect('paiement_success', type_paiement='final')
            
        except Exception as e:
            messages.error(request, f"Erreur lors du traitement du paiement: {str(e)}")
    
    return render(request, 'Client/budget_final_paiement.html', context)

@login_required(login_url='login')
@user_passes_test(is_customer)
def versement_budget_final(request):
    """
    Vue pour gérer les versements du budget final par virement bancaire
    """
    # Récupérer les informations de paiement du client
    client = request.user.client
    
    # Calculer le montant final (même logique que budget_final_paiement)
    cout_total = 10000
    budget_avance = 2000
    visite_payee = 50
    autres_frais = 500
    tva = int((cout_total - budget_avance - visite_payee + autres_frais) * 0.18)
    montant_final = cout_total - budget_avance - visite_payee + autres_frais + tva
    
    # Récupérer le dernier projet du client (exemple)
    try:
        projet = SuppervisionTravaux.objects.filter(client=request.user).last()
    except:
        projet = None
    
    context = {
        'montant_final': montant_final,
        'projet': projet,
    }
    
    if request.method == 'POST':
        # Traitement de l'upload du justificatif
        justificatif = request.FILES.get('justificatif')
        reference = request.POST.get('reference')
        commentaire = request.POST.get('commentaire', '')
        
        if justificatif:
            try:
                # Créer le type de paiement s'il n'existe pas
                type_paiement_obj, created = TypePaiement.objects.get_or_create(
                    nom='Budget final - Virement'
                )
                
                # Créer un paiement avec justificatif
                paiement = Paiement.objects.create(
                    type_paiement=type_paiement_obj,
                    montant=montant_final,
                    created_by=request.user,
                    commande=None
                )
                
                # Ici, vous pourriez sauvegarder le fichier justificatif
                # dans un modèle séparé ou dans un champ du modèle Paiement
                
                return JsonResponse({
                    'success': True,
                    'message': 'Justificatif de paiement final uploadé avec succès! Votre paiement sera vérifié sous 24h.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors du traitement: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Veuillez sélectionner un fichier de preuve de paiement.'
            })
    
    return render(request, 'Client/versement_budget_final.html', context)

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

def paiement_success(request, type_paiement):
    return render(request, 'Client/paiement_success.html', {'type_paiement': type_paiement})

def error(request):
    return render(request, 'Client/error.html', {'message': 'Une erreur est survenue.'})

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
@user_passes_test(is_supervisor)
def mark_liste_attente_done(request, liste_attente_id):
    liste_attente = get_object_or_404(ListeAttente, id=liste_attente_id)
    if request.method == 'POST':
        liste_attente.done = True
        liste_attente.save()
        return redirect('liste_attente_detail', liste_attente_id=liste_attente_id)
    return render(request, 'confirm_mark_done.html', {'liste_attente': liste_attente})


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