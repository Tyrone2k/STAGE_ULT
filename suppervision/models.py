from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    age = models.PositiveIntegerField()
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/',null=True,blank=True)
    address = models.CharField(max_length=40, null=True)
    mobile = models.CharField(max_length=20,null=True)
    is_rejected = models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id

    @property
    def get_email_field_name(self):
        return self.user.email


    def __str__(self) :
        return f"{self.user.username}"
    

@receiver(post_save, sender=User)
def add_user_approved_field(sender, instance, created, **kwargs):
    if created:
        instance.is_rejected = False
        instance.save()
   
    
class Design(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    description = models.CharField(max_length=300,null=True)
    image= models.ImageField(upload_to='design_image/',null=True,blank=True)   

    def __str__(self) :
        return f"{self.nom} : {self.description}"
    
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
    quantite = models.FloatField( null=True)
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    quantite_initiale = models.FloatField()
    quantite_actuelle = models.FloatField(editable=False)  # Mise à jour automatique
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    delais_expiration = models.PositiveIntegerField(null=True, blank=True)
    prix = models.FloatField()  # Calculé automatiquement

    def save(self, *args, **kwargs):
        """ Mise à jour automatique du prix et de la quantité actuelle """
        if self.pk:  # Si l'objet existe déjà
            old_instance = Stock.objects.get(pk=self.pk)
            self.quantite_actuelle = old_instance.quantite_actuelle + self.quantite_initiale
        else:  # Si c'est un nouvel enregistrement
            self.quantite_actuelle = self.quantite_initiale

        # Calcul automatique du prix total
        self.prix = self.produit.prix * self.quantite_actuelle

        super(Stock, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.fournisseur.user.username} nous a fourni {self.produit.nom} ({self.quantite_actuelle} unités) à {self.prix}€"
    
class Commande(models.Model):
    id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(Client, on_delete=models.PROTECT, null=True)
    category = models.ForeignKey(Design,null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    longitude = models.FloatField(default=0, editable=False)
    latitude = models.FloatField(default=0, editable=False)

    def __str__(self) :
        return f"Commande de {self.created_by.user.username} {self.category}"
        
class ProduitCommande(models.Model):
    id = models.BigAutoField(primary_key=True)
    commande = models.ForeignKey(Commande, null=True, on_delete=models.SET_NULL)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    category_design = models.ForeignKey(CategoryDesign, null=True, on_delete=models.CASCADE)  # Filtre pour CategoryDesign
    design = models.ForeignKey(Design, null=True, on_delete=models.CASCADE)  # Lien avec Design au lieu de CategoryDesign
    quantite = models.FloatField(default=0)
    prix = models.FloatField(default=0)

    def __str__(self):
        return f"{self.commande.created_by.user.username}  {self.quantite} {self.produit.unite} de {self.produit}"

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Panier"
 
class Paiement(models.Model):
    id = models.AutoField(primary_key=True)
    type_paiement = models.ForeignKey(TypePaiement,null=True, on_delete=models.PROTECT)
    montant = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    commande = models.ForeignKey(Commande, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) :
        return f"Les frais de {self.type_paiement.nom} de {self.montant.prix} sur {self.commande} à {self.created_by}"

class Facture(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('EMISE', 'Émise'),
        ('PAYEE', 'Payée'),
        ('ANNULEE', 'Annulée'),
    ]

    id = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='facture')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    date_emission = models.DateTimeField(auto_now_add=True, verbose_name="Date d'émission")
    date_echeance = models.DateTimeField(verbose_name="Date d'échéance")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EMISE')
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant HT")
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="TVA")
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant TTC")
    description = models.TextField(blank=True, null=True, verbose_name="Description des services")
    paypal_payment_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Paiement PayPal")
    paypal_transaction_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Transaction PayPal")
    reference_virement = models.CharField(max_length=100, blank=True, null=True)
    commentaire_virement = models.TextField(blank=True, null=True)
    date_validation_virement = models.DateTimeField(blank=True, null=True)
    
    # Champs pour l'entreprise
    entreprise_nom = models.CharField(max_length=100, default="RENOVATION IMMOBILIERE SARL")
    entreprise_adresse = models.TextField(default="60 Avenue de la mission, Bujumbura, Burundi")
    entreprise_telephone = models.CharField(max_length=20, default="+257 62 152 303")
    entreprise_email = models.EmailField(default="contact@renovation-bi.com")
    entreprise_siret = models.CharField(max_length=50, default="344 54 31749")
    entreprise_tva = models.CharField(max_length=50, default="BI 12.055.1/56")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']

    def save(self, *args, **kwargs):
        if not self.numero:
            # Générer un numéro de facture unique
            annee = timezone.now().year
            dernier_numero = Facture.objects.filter(date_emission__year=annee).count() + 1
            self.numero = f"FACT-{annee}-{dernier_numero:05d}"
        
        if not self.date_echeance:
            # Date d'échéance par défaut : 30 jours après l'émission
            self.date_echeance = timezone.now() + timezone.timedelta(days=30)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture {self.numero} - {self.client.get_name} - {self.montant_ttc} BIF"

    def generer_pdf(self):
        """Génère le PDF de la facture (à implémenter avec reportlab ou weasyprint)"""
        pass
    
    def marquer_comme_payee(self):
        """Marquer la facture comme payée après validation du virement"""
        self.statut = 'PAYEE'
        self.date_validation_virement = timezone.now()
        self.save()
          
    @property
    def est_en_retard(self):
        """Vérifie si la facture est en retard de paiement"""
        return self.statut == 'EMISE' and timezone.now() > self.date_echeance

    @property
    def jours_retard(self):
        """Retourne le nombre de jours de retard"""
        if self.est_en_retard:
            return (timezone.now() - self.date_echeance).days
        return 0
    
class JustificatifPaiement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='justificatifs')
    fichier = models.FileField(upload_to='justificatifs_paiement/')
    date_upload = models.DateTimeField(auto_now_add=True)
    type_paiement = models.CharField(max_length=50, default='virement')
    
    def __str__(self):
        return f"Justificatif {self.fichier.name} pour {self.facture.numero}"
    
class ListeAttente(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT)
    justificatif = models.FileField(
        upload_to='justificatifs_visite/',
        null=True,
        blank=True
    )
    done = models.BooleanField(default=False, editable=False)

    def __str__(self) :
        return f"Le client {self.client} a été enregristré par {self.created_by} sur la liste d'attente # {self.id}"
    
class SuppervisionTravaux(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    budget1 = models.ForeignKey(Paiement, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='travaux_en_cours/',null=True,blank=True)
    description = models.CharField(max_length=500,null=True)
    justificatif = models.FileField(
        upload_to='justificatifs_avance/',
        null=True,
        blank=True
    )


    def __str__(self) :
        return f"La description des travaux du client {self.client} est en cours"
    
class RenovationFaite(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    budget2 = models.ForeignKey(Paiement,  on_delete=models.PROTECT)  
    image = models.ImageField(upload_to='fin_travaux/',null=True,blank=True)
    description = models.CharField(max_length=500,null=True)  
    done = models.BooleanField(default=False)
    justificatif = models.FileField(
        upload_to='justificatifs_final/',
        null=True,
        blank=True
    )

    def __str__(self) :
        return f"La description des fins de travaux du client {self.client} a été faite {self.done}"

class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_read = models.BooleanField(default=False, verbose_name="Message lu")
    subject = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sujet")

    def __str__(self):
        return f"Message de {self.name} ({self.email})"    
# Create your models here.
