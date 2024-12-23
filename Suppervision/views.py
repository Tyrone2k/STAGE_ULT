from django.shortcuts import render,redirect
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test


# Create your views here.



def login(request):
    return render(request,'login.html')




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
    userForm=forms.ClientUserForm()
    clientForm=forms.ClientForm()
    mydict={'userForm':userForm,'clientForm':clientForm}
    if request.method=='POST':
        userForm=forms.ClientUserForm(request.POST)
        clientForm=forms.ClientForm(request.POST,request.FILES)
        if userForm.is_valid() and clientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            client=clientForm.save(commit=False)
            client.user=user
            client.save()
            mon_client_group = Group.objects.get_or_create(name='CLIENT')
            mon_client_group[0].user_set.add(user)
        return HttpResponseRedirect('login')
    return render(request, 'signin.html', context=mydict)


def is_customer(user):
    return user.groups.filter(name='CLIENT').exists()

# def afterlogin_view(request):
#     if is_customer(request.user):
#         return redirect('client-home')
#     else:
#         return redirect('home')
    
    
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
    



def services(request):
    return render(request,'services.html')