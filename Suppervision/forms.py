from django import forms
from django.contrib.auth.models import User
from .models import *


class ClientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),  
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['age', 'address', 'mobile', 'profile_pic']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AprroveUserForm(forms.Form):
    action = forms.ChoiceField(choices=[('approve','Approuver'), ('reject','Refuser')], widget=forms.RadioSelect)


class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ['nom', 'image', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CategoryDesignForm(forms.ModelForm):
    class Meta:
        model = CategoryDesign
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CategoryProduitForm(forms.ModelForm):
    class Meta:
        model = CategoryProduit
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TypePaiementForm(forms.ModelForm):
    class Meta:
        model = TypePaiement
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'type', 'unite', 'prix']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'unite': forms.TextInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['user', 'adresse', 'contact', 'description']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit', 'fournisseur', 'quantite_initiale', 'prix', 'delais_expiration']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'quantite_initiale': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'delais_expiration': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['created_by', 'category', 'budget']
        widgets = {
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProduitCommandeForm(forms.ModelForm):
    class Meta:
        model = ProduitCommande
        fields = ['produit', 'commande', 'design']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'commande': forms.Select(attrs={'class': 'form-control'}),
            'design': forms.Select(attrs={'class': 'form-control'}),
        }

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['type_paiement', 'montant', 'created_by', 'commande']
        widgets = {
            'type_paiement': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'commande': forms.Select(attrs={'class': 'form-control'}),
        }

class ListeAttenteForm(forms.ModelForm):
    class Meta:
        model = ListeAttente
        fields = ['created_by', 'client']
        widgets = {
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
        }

class SuppervisionTravauxForm(forms.ModelForm):
    class Meta:
        model = SuppervisionTravaux
        fields = ['client', 'budget1', 'description', 'image']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'budget1': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RenovationFaiteForm(forms.ModelForm):
    class Meta:
        model = RenovationFaite
        fields = ['client', 'budget2', 'description', 'image']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'budget2': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AddressForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mobile = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }