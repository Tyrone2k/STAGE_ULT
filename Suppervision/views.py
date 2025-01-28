from django.shortcuts import render,redirect
from . import forms,models
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate, login as auth_login


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
                return redirect('admin_dashboard')  # Redirection après connexion
            else:
                error = "Votre compte est désactivé. Veuillez contacter l'administrateur."
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect."

    return render(request, 'login.html', {'error': error})

def is_customer(user):
    return user.groups.filter(name='CLIENT').exists()

def after_login(request):
    if request.user.groups.filter(name='ADMIN').exists():
        return redirect('admin-dashboard')  # Page pour l'administrateur
    elif request.user.groups.filter(name='SUPERVISEUR').exists():
        return redirect('superviseur-dashboard')  # Page pour le superviseur
    elif request.user.groups.filter(name='CLIENT').exists():
        return redirect('client-home')  # Page pour le client
    else:
        return redirect('login')  # Redirection par défaut




def home_view(request):
    # designs=models.Design.objects.all()
    # if 'id_design' in request.COOKIES:
    #     id_design = request.COOKIES['id_design']
    #     compter = id_design.split('|')
    #     compter_design_panier = len(set(compter))
    # else:
    #     compter_design_panier = 0
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect('afterlogin')    

    # return render(request,'home.html',{'designs':designs, 'compter_design_panier':compter_design_panier})
    return render (request, 'home.html')

def signin(request):
    userForm = forms.ClientUserForm()
    clientForm = forms.ClientForm()
    if request.method == 'POST':
        userForm = forms.ClientUserForm(request.POST)
        clientForm = forms.ClientForm(request.POST, request.FILES)
        if userForm.is_valid() and clientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
            client = clientForm.save(commit=False)
            client.user = user
            client.save()
            client_group = Group.objects.get(name='CLIENT')
            client_group.user_set.add(user)
            return redirect('login')
        else:
            return render(request, 'signin.html', {'userForm': userForm, 'clientForm': clientForm})
    return render(request, 'signin.html', {'userForm': userForm, 'clientForm': clientForm})



    
@login_required(login_url='login')
@user_passes_test(is_customer)
def client_home_view(request):
    designs=models.Design.objects.all()
    if 'id_design' in request.COOKIES:
        id_design = request.COOKIES['id_design']
        compter = id_design.split('|')
        compter_design_panier = len(set(compter))
    else:
        compter_design_panier = 0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')    

    return render(request,'home.html',{'designs':designs, 'compter_design_panier':compter_design_panier})    
    

def galerie(request):
    return render(request,'galerie.html')

def services(request):
    return render(request,'services.html')

def designs(request):
    return render(request,'designs.html')

def contact(request):
    return render(request,'contact.html')




# ----------------------------------------------------------------
# ------- A D M I N   D A S H B O A R D --------------------------
# ----------------------------------------------------------------
@login_required(login_url='login')
@user_passes_test(lambda u: is_admin)
def admindashboard(request):
    return render(request, 'admin_dashboard')

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def manage_accounts(request):
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'approve_accounts.html', {'pending_users': pending_users})


@user_passes_test(is_customer)
def approve_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('manage_accounts')


# ----------------------------------------------------------------
# ------- S U P E R V I S E U R  D A S H B O A R D ---------------
# ----------------------------------------------------------------

@login_required(login_url='login')
@user_passes_test(lambda u: is_employee)
def superviseurdashboard(request):
    return render(request, 'superviseur_dashboard')

def is_employee(user):
    return user.groups.filter(name='SUPERVISEUR').exists()
