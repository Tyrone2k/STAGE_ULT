from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from . import forms, models
from .models import*
from .forms import*
from django.db.models import Sum, Count
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
    designs = Design.objects.all()
    return render(request, 'galerie.html', {'designs': designs})

def services(request):
    return render(request, 'services.html')

def designs(request):
    return render(request, 'designs.html')

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


# ----------------------------------------------------------------
# ------- C L I E N T   D A S H B O A R D --------------------------
# ----------------------------------------------------------------


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
    design = Design.objects.get(id=design_id)
    categories_produit = CategoryProduit.objects.all()
    categories_design = CategoryDesign.objects.all()
    
    # Récupérer les produits associés au design via ProduitCommande
    produits = Produit.objects.filter(produitcommande__design=design).distinct()

    # Appliquer les filtres
    category_produit_id = request.GET.get('category_produit')
    category_design_id = request.GET.get('category_design')
    if category_produit_id:
        produits = produits.filter(type_id=category_produit_id)
    if category_design_id:
        produits = produits.filter(produitcommande__category_design_id=category_design_id)

    context = {
        'design': design,
        'categories_produit': categories_produit,
        'categories_design': categories_design,
        'produits': produits,
    }
    return render(request, 'Client/ajout_produits.html', context)


@login_required(login_url='login')
@user_passes_test(is_customer)
def enregistrer_commande(request):
    """
    Enregistre une commande avec les produits sélectionnés et redirige vers client_orders.
    """
    if request.method == 'POST':
        design_id = request.POST.get('design_id')
        produit_ids = request.POST.getlist('produits')
        quantites = request.POST.getlist('quantites')
        category_design_id = request.POST.get('category_design')
        
        design = get_object_or_404(Design, id=design_id)
        
        # Créer une nouvelle commande
        commande = Commande.objects.create(
            created_by=request.user.client,
            category=design,
            budget=0  # À ajuster selon votre logique
        )

        # Ajouter les produits sélectionnés à la commande
        total_budget = 0
        for produit_id, quantite in zip(produit_ids, quantites):
            produit = get_object_or_404(Produit, id=produit_id)
            quantite = float(quantite) if quantite else 0
            if quantite > 0:
                prix = produit.prix * quantite
                ProduitCommande.objects.create(
                    produit=produit,
                    commande=commande,
                    design=design,
                    category_design_id=category_design_id if category_design_id else None,
                    quantite=quantite,
                    prix=prix
                )
                total_budget += prix
        
        # Mise à jour du budget total de la commande
        commande.budget = total_budget
        commande.save()
        
        messages.success(request, "Commande enregistrée avec succès.")
        return redirect('client_orders')
    return redirect('client_galerie')

@login_required(login_url='login')
@user_passes_test(is_customer)
def client_orders(request):
    client = request.user.client
    orders = Commande.objects.filter(created_by=client).order_by('-created_at')
    return render(request, 'Client/client_orders.html', {'orders': orders})


@login_required(login_url='login')
@user_passes_test(is_customer)
def visite_local(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        if montant:
            paiement = Paiement.objects.create(
                type_paiement_id=1,  # Supposons un TypePaiement pour visite
                montant=montant,
                created_by=request.user,
                commande=None  # Peut être None si pas lié à une commande
            )
            # Ajouter à la liste d'attente
            ListeAttente.objects.create(
                created_by=request.user,
                client=request.user.client,
                done=False
            )
            return redirect('superviseur_dashboard')  # Rediriger vers la page du superviseur pour vérification
    return render(request, 'Client/visite_local.html')

@login_required(login_url='login')
@user_passes_test(is_customer)
def panier(request):
    client = request.user.client
    cart_items = ProduitCommande.objects.filter(commande__isnull=True, created_by=client).order_by('id')
    total_price = sum(item.prix for item in cart_items)
    return render(request, 'Client/panier.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='login')
@user_passes_test(is_customer)
def paiement(request, type_paiement):
    try:
        type_paiement_obj = TypePaiement.objects.get(nom=type_paiement)
    except TypePaiement.DoesNotExist:
        return render(request, 'error.html', {'message': 'Type de paiement non trouvé.'})

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.type_paiement = type_paiement_obj
            paiement.created_by = request.user
            paiement.save()

            # Logique spécifique pour la visite locale
            if type_paiement == 'Visite du local':
                ListeAttente.objects.create(
                    created_by=request.user,
                    client=request.user.client,
                    done=False
                )
                return redirect('superviseur_dashboard')  # Rediriger vers la page du superviseur pour vérification

            return redirect('paiement_success', type_paiement=type_paiement)
    else:
        form = PaiementForm(initial={'type_paiement': type_paiement_obj})
    return render(request, 'Client/paiement.html', {'form': form, 'type_paiement': type_paiement})

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


# ----------------------------------------------------------------
# ------- A D M I N   D A S H B O A R D --------------------------
# ----------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(is_admin)
def admindashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_accounts(request):
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'approve_accounts.html', {'pending_users': pending_users})

@login_required(login_url='login')
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            user.is_active = True
        elif action == 'reject':
            user.is_active = False  # Peut-être garder l'utilisateur inactif si refusé
        user.save()
    return redirect('manage_accounts')


@login_required(login_url='login')
@user_passes_test(is_admin)
def statistics(request):
    nombre_clients = Client.objects.count()
    nombre_commandes = Commande.objects.count()
    total_ventes = Paiement.objects.aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Analyse des ventes par catégorie de design
    ventes_par_categorie = {}
    for cat in CategoryDesign.objects.all():
        total = ProduitCommande.objects.filter(design=cat).aggregate(Sum('prix'))['prix__sum'] or 0
        ventes_par_categorie[cat] = total

    context = {
        'nombre_clients': nombre_clients,
        'nombre_commandes': nombre_commandes,
        'total_ventes': total_ventes,
        'ventes_par_categorie': ventes_par_categorie
    }
    return render(request, 'statistics.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def manage_stock(request):
    stocks = Stock.objects.all().order_by('-created_at')
    context = {'stocks': stocks}
    return render(request, 'manage_stock.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin)
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_by = request.user
            stock.quantite_actuelle = form.cleaned_data['quantite_initiale']  # Initialiser quantite_actuelle
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
            form.save()
            return redirect('manage_stock')
    else:
        form = StockForm(instance=stock)
    return render(request, 'edit_stock.html', {'form': form, 'stock': stock})

@login_required(login_url='login')
@user_passes_test(is_admin)
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
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

# ----------------------------------------------------------------
# ------- S U P E R V I S E U R  D A S H B O A R D ---------------
# ----------------------------------------------------------------

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

