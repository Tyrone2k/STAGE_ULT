from typing import Any
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models.query import QuerySet
from .models import *


admin.site.site_header='RENOVATION IMMOBILIERE'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = "user", "age", "address", "mobile", "profile_pic"



@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display =  "nom", "image", "description"

@admin.register(CategoryDesign)
class CategoryDesignAdmin(admin.ModelAdmin):
    list_display =  ("nom",)

@admin.register(CategoryProduit)
class CategoryProduitAdmin(admin.ModelAdmin):
    list_display =  ('nom',)

@admin.register(TypePaiement)
class TypePaiementAdmin(admin.ModelAdmin):
    list_display =  ("nom",)    


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = "nom", "type", "unite", "quantite", "prix"


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = "user", "adresse", "contact", "description" 


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = "created_by", "produit", "fournisseur", "quantite_initiale", "quantite_actuelle", "created_at", "delais_expiration", "prix" 


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = "created_by", "created_at", "category", "longitude", "latitude"


@admin.register(ProduitCommande)
class ProduitCommandeAdmin(admin.ModelAdmin):
    list_display = "commande", "category_design", "design", "produit", "quantite", "prix"


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = "type_paiement", "commande", "montant", "created_by", "created_at"


@admin.register(ListeAttente)
class ListeAttenteAdmin(admin.ModelAdmin):
    list_display = "created_by", "client", "created_at", "done"


@admin.register(SuppervisionTravaux)
class SuppervisionTravauxAdmin(admin.ModelAdmin):
    list_display = "client", "created_at", "budget1", "description", "image"


@admin.register(RenovationFaite)
class RenovationFaiteAdmin(admin.ModelAdmin):
    list_display = "client", "created_at", "budget2", "description", "image", "done"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = "name", "email", "message", "created_at"




