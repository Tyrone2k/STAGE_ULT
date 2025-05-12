# Site Web de Rénovation Immobilière

## Aperçu du Projet
Cette application web basée sur Django est conçue pour une entreprise de rénovation immobilière, offrant une plateforme pour gérer les projets de rénovation, les commandes des clients, les stocks, les paiements et les designs. L'application prend en charge trois rôles d'utilisateurs distincts — Client, Administrateur et Superviseur — chacun disposant d'un tableau de bord dédié et de fonctionnalités spécifiques. Le système facilite l'authentification des utilisateurs, la gestion des commandes, le suivi des stocks, le traitement des paiements et la supervision des projets, garantissant une expérience fluide pour toutes les parties prenantes.

## Fonctionnalités

### Rôles des Utilisateurs et Tableaux de Bord
- **Client** :
  - S'inscrire et se connecter pour accéder à un tableau de bord personnalisé.
  - Parcourir et sélectionner des designs (intérieur/extérieur) dans une galerie.
  - Créer et gérer des commandes en sélectionnant des produits et des designs.
  - Afficher et modifier les informations du profil.
  - Effectuer des paiements pour des services comme les visites de sites.
  - Annuler des commandes et suivre l'historique des commandes.
  - Ajouter des produits à un panier et les filtrer par catégorie de produit ou de design.
- **Administrateur** :
  - Gérer les comptes utilisateurs (approuver/rejeter les inscriptions des clients).
  - Superviser l'inventaire des stocks (ajouter, modifier, supprimer des entrées de stock).
  - Gérer les produits et les designs (ajouter, modifier, supprimer, filtrer par catégorie).
  - Afficher les enregistrements de paiement et générer des statistiques (par exemple, ventes totales, ventes par catégorie de design).
  - Accéder à un tableau de bord avec une vue d'ensemble des activités du système.
- **Superviseur** :
  - Gérer les listes d'attente pour les clients demandant des visites de sites.
  - Suivre les projets de rénovation en cours et les rénovations terminées.
  - Marquer les projets et les entrées de la liste d'attente comme terminés.
  - Afficher des informations détaillées sur les projets et les rénovations.

### Fonctionnalités Générales
- **Authentification** : Système sécurisé d'inscription et de connexion des utilisateurs avec un contrôle d'accès basé sur les rôles, utilisant le framework d'authentification de Django.
- **Fonctionnalité de Recherche** : Les clients et les administrateurs peuvent rechercher des designs et des produits par nom.
- **Support Multimédia** : Téléchargement et affichage d'images pour les profils, les designs et les projets de rénovation.
- **Intégration AJAX** : Filtrage dynamique des produits par catégorie et actions asynchrones (par exemple, ajout/suppression de produits).
- **Design Réactif** : Les templates (supposés basés sur Bootstrap) garantissent une interface utilisateur conviviale sur tous les appareils (actuellement définis à des valeurs par défaut).

## Structure du Projet
L'application suit une structure de projet Django standard avec les fichiers clés suivants :

- **Modèles (`models.py`)** : Définit les modèles de base de données pour les clients, les designs, les produits, les commandes, les paiements, les stocks, les fournisseurs, les listes d'attente, les rénovations, etc.
- **Formulaires (`forms.py`)** : Formulaires Django pour la validation et le rendu des entrées utilisateur, incluant des formulaires pour les clients, les produits, les commandes, les paiements et les designs.
- **Vues (`views.py`)** : Gère les requêtes et réponses HTTP, implémentant la logique pour les tableaux de bord, l'authentification, les opérations CRUD et les requêtes AJAX.
- **URLs (`urls.py`)** : Définit les motifs d'URL pour router les requêtes vers les vues appropriées, incluant la gestion des fichiers multimédias statiques.
- **Admin (`admin.py`)** : Personnalise l'interface d'administration de Django pour gérer tous les modèles.
- **Templates** : Templates HTML (non fournis mais référencés dans les vues) pour rendre les tableaux de bord, les formulaires et les pages.

## Installation et Configuration

### Prérequis
- Python 3.8+
- Django 3.2+
- PostgreSQL (ou SQLite pour le développement)
- Virtualenv (recommandé)
- Git

### Étapes
1. **Cloner le Répertoire** :
   ```bash
   git clone <url-du-répertoire>
   cd <répertoire-du-projet>
   ```

2. **Configurer un Environnement Virtuel** :
   ```bash
   python -m venv venv
   venv\Scripts\activate # Sur Linux : source venv/bin/activate
   ```

3. **Installer les Dépendances** :
   Créez un fichier `requirements.txt` avec le contenu suivant (ajustez les versions si nécessaire) :
   ```text
   django>=3.2
   pillow>=8.0
   djangorestframework>=3.12
   ```
   Ensuite, exécutez :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les Paramètres** :
   - Mettez à jour `settings.py` avec la configuration de votre base de données (par exemple, PostgreSQL) ou laissez ce champ tel quel (DBSQLite) :
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'nom_de_votre_base',
             'USER': 'utilisateur_de_votre_base',
             'PASSWORD': 'mot_de_passe_de_votre_base',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```
   - Configurez les chemins pour les fichiers multimédias et statiques :
     ```python
     MEDIA_URL = '/media/'
     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
     STATIC_URL = '/static/'
     STATIC_ROOT = os.path.join(BASE_DIR, 'static')
     ```

5. **Exécuter les Migrations** :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Créer les Groupes d'Utilisateurs** :
   Le superutilisateur doit créer manuellement les groupes requis (`CLIENT`, `ADMIN`, `SUPERVISEUR`) via l'interface d'administration de Django :
   - Connectez-vous au panneau d'administration à `http://localhost:8000/admin/` avec les identifiants du superutilisateur.
   - Accédez à la section **Groupes** (sous **Authentification et Autorisation**).
   - Créez trois groupes avec les noms suivants : `CLIENT`, `ADMIN`, `SUPERVISEUR`.
   - Enregistrez chaque groupe.

7. **Créer un Superutilisateur** :
   ```bash
   python manage.py createsuperuser
   ```

8. **Collecter les Fichiers Statiques** :
   ```bash
   python manage.py collectstatic
   ```

9. **Lancer le Serveur de Développement** :
   ```bash
   python manage.py runserver
   ```
   Accédez à l'application à l'adresse `http://localhost:8000`.

## Utilisation

### Accès à l'Application
- **Page d'Accueil** : `http://localhost:8000/` - Affiche des informations générales et des liens de navigation.
- **Connexion** : `http://localhost:8000/login/` - Authentifiez-vous en tant que client, administrateur ou superviseur.
- **Inscription (Client)** : `http://localhost:8000/signin/` - Inscrivez-vous en tant que client (nécessite une approbation par l'administrateur).
- **Panneau d'Administration** : `http://localhost:8000/admin/` - Gérer tous les modèles (accessible aux superutilisateurs).

### Navigation Basée sur les Rôles
- **Client** :
  - Après connexion, redirigé vers `/client-home/`.
  - Parcourir les designs à `/client-home/galerie/`.
  - Créer des commandes à `/client-home/commande/enregistrer_commande/`.
  - Afficher les commandes à `/client-home/panier/`.
  - Modifier le profil à `/client-home/profile/edit-profile/`.
- **Administrateur** :
  - Redirigé vers `/admin-dashboard/`.
  - Approuver les utilisateurs à `/admin-dashboard/manage-accounts/`.
  - Gérer les stocks à `/admin-dashboard/manage-stock/`.
  - Afficher les statistiques à `/admin-dashboard/statistics/`.
- **Superviseur** :
  - Redirigé vers `/superviseur-dashboard/`.
  - Gérer les listes d'attente à `/superviseur/liste-attente/`.
  - Suivre les rénovations à `/superviseur/renovation/list/`.
  - Superviser les projets à `/superviseur/projet/list/`.

### Flux de Travail Clés
1. **Processus de Commande Client** :
   - Parcourir les designs et sélectionner des produits.
   - Ajouter des produits à une commande avec une quantité fixe (par défaut : 1).
   - Soumettre la commande, qui est enregistrée avec un budget total.
   - Les superviseurs peuvent ajuster les quantités ultérieurement.
2. **Gestion des Comptes par l'Administrateur** :
   - Examiner les inscriptions d'utilisateurs en attente.
   - Approuver ou rejeter les comptes, en mettant à jour le statut de l'utilisateur et les indicateurs de rejet des clients.
3. **Gestion des Stocks** :
   - Les administrateurs ajoutent des stocks avec des quantités initiales et des détails sur les fournisseurs.
   - Les prix des stocks sont calculés automatiquement en fonction des prix des produits.
4. **Tâches du Superviseur** :
   - Ajouter des clients aux listes d'attente pour les visites de sites.
   - Suivre la progression des rénovations et marquer les projets comme terminés.

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact
Pour toute assistance ou question, contactez-moi sur ce mail [gastephane0@gmail.com].
