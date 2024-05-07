from django.shortcuts import render


# Create your views here.
def home_view(request):
    return render(request,'home.html')

def signin(request):
    return render(request, 'signin.html')