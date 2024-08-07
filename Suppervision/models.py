from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    age = models.PositiveIntegerField()
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40, null=True)
    mobile = models.CharField(max_length=20,null=True)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id

    def __str__(self) :
        return f"{self.user.username}"
    
class Design(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    image= models.ImageField(upload_to='design_image/',null=True,blank=True)   

    def __str__(self) :
        return f"{self.nom}"
    
class CategoryDesign(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)

    def __str__(self) :
        return f"{self.nom}"


class CategoryProduit(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)        

    def __str__(self) :
        return f"{self.nom}"

class TypePaiement(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=30, null=True)   

    def __str__(self) :
        return f"{self.nom}"    
    

class Produit(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    type = models.ForeignKey(CategoryProduit, null=True, on_delete=models.CASCADE) 
    unite = models.CharField(max_length=31)
    quantite = models.FloatField(editable=False, null=True)
    prix = models.FloatField()

    def __str__(self) :
        return f"{self.nom} {self.type} de {self.prix}"

class Fournisseur(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User,max_length=30,null=True, on_delete=models.CASCADE )
    adresse = models.CharField(max_length=63)
    contact = models.BigIntegerField(null=True)
    description = models.CharField(max_length=128)

    def __str__(self) :
        return f"{self.user.username}"
    
class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    quantite_initiale = models.FloatField(default=0)
    quantite_actuelle = models.FloatField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delais_expiration = models.PositiveIntegerField(null=True, blank=True)
    prix = models.FloatField()

    def __str__(self) :
        return f"{self.fournisseur.user.username} nous a founit {self.produit.nom} à {self.prix}"
    
class Commande(models.Model):
    id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(Client, on_delete=models.PROTECT, null=True)
    category = models.ForeignKey(Design,null=True, on_delete=models.SET_NULL)
    budget = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    longitude = models.FloatField(default=0, editable=False)
    latitude = models.FloatField(default=0, editable=False)

    def __str__(self) :
        return f"Commande de {self.created_by.user.username} {self.category} valant {self.budget}"
        
class ProduitCommande(models.Model):
    id = models.BigAutoField(primary_key=True)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    commande = models.ForeignKey(Commande, null=True, on_delete=models.SET_NULL)
    design = models.ForeignKey(CategoryDesign, null=True, on_delete=models.CASCADE)
    quantite = models.FloatField(editable=False,default=0)
    prix = models.FloatField(editable=False,default=0)

    def __str__(self) :
        return f"{self.commande.created_by.user.username} {self.quantite} {self.produit.unite} de {self.produit}"
    
    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Panier"

 
class Paiement(models.Model):
    id = models.AutoField(primary_key=True)
    type_paiement = models.ForeignKey(TypePaiement,null=True, on_delete=models.PROTECT)
    montant = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)

    def __str__(self) :
        return f"Les frais de {self.type_paiement} de {self.montant} sur {self.commande} à {self.created_by}"

class ListeAttente(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT)
    done = models.BooleanField(default=False, editable=False)

    def __str__(self) :
        return f"Le client {self.client} a été enregristré par {self.created_by} sur la liste d'attente"
    
class SuppervisionTravaux(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT)
    budget1 = models.ForeignKey(Paiement, on_delete=models.PROTECT)
    #image = 
    description = models.CharField(max_length=500,null=True) 


    def __str__(self) :
        return f"La description des travaux du client {self.client} a été faite"
    
class RenovationFaite(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT)
    budget2 = models.ForeignKey(Paiement,  on_delete=models.PROTECT)  
    #image = 
    description = models.CharField(max_length=500,null=True)  

    def __str__(self) :
        return f"La description des fins de travaux du client {self.client} a été validé"
# Create your models here.
