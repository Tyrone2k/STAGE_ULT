from django import forms
from django.contrib.auth.models import User
from . import models


class ClientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
class ClientForm(forms.ModelForm):
    class Meta:
        model=models.Client
        fields=['age','address','mobile','profile_pic']

class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)


#for updating status of order
class CommandeForm(forms.ModelForm):
    class Meta:
        model=models.Commande
        fields=['created_by']

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))        