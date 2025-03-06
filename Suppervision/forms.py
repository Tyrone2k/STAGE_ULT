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
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = Stock
        fields = ['produit', 'fournisseur', 'quantite_initiale', 'prix',  'delais_expiration']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'quantite_initiale': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'delais_expiration': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at

class CommandeForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = Commande
        fields = ['created_by', 'category']
        widgets = {
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(CommandeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at

class ProduitCommandeForm(forms.ModelForm):
    category_produit = forms.ModelChoiceField(
        queryset=CategoryProduit.objects.all(),
        required=False,
        empty_label="Sélectionner une catégorie de produit"
    )
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.none(),  # Chargé dynamiquement via AJAX
        required=False,
        empty_label="Sélectionner un produit"
    )
    category_design = forms.ModelChoiceField(
        queryset=CategoryDesign.objects.all(),
        required=False,
        empty_label="Sélectionner une catégorie de design"
    )

    class Meta:
        model = ProduitCommande
        fields = ['commande', 'category_design', 'design', 'produit', 'category_produit', 'quantite']
        widgets = {
            'commande': forms.Select(attrs={'class': 'form-control'}),
            'category_design': forms.Select(attrs={'class': 'form-control'}),
            'design': forms.Select(attrs={'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaiementForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = Paiement
        fields = ['type_paiement', 'montant', 'created_by', 'commande']
        widgets = {
            'type_paiement': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'commande': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(PaiementForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at

class ListeAttenteForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = ListeAttente
        fields = ['created_by', 'client']
        widgets = {
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(ListeAttenteForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at

class SuppervisionTravauxForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = SuppervisionTravaux
        fields = ['client', 'budget1', 'description', 'image']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'budget1': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(SuppervisionTravauxForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at

class RenovationFaiteForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
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
    def __init__(self, *args, **kwargs):
        super(RenovationFaiteForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at


class ContactForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at