# =============================================================================
# IMPORTATIONS
# =============================================================================
from django.shortcuts import render, get_object_or_404, redirect  # render: transforme un template en HTML, get_object_or_404: récupère un objet ou renvoie une erreur 404, redirect: redirige vers une autre URL
from django.db import models  # Pour utiliser les fonctionnalités des modèles Django et les requêtes complexes (Q)
from django.contrib import messages  # Système de messages pour afficher des notifications à l'utilisateur (erreur, succès, etc.)
from django.contrib.auth.hashers import make_password, check_password  # make_password: crypte un mot de passe, check_password: vérifie un mot de passe crypté
from functools import wraps  # Utilisé pour créer des décorateurs personnalisés qui préservent les métadonnées de la fonction d'origine
from .models import Voiture, ImageVoiture, Utilisateur, Transaction  # Importation des modèles de l'application
from django.db.models import Sum, Count, Q  # Sum: somme des valeurs, Count: comptage, Q: requêtes complexes avec OR/AND
from django.utils import timezone  # Pour obtenir la date et l'heure actuelles
from datetime import timedelta  # Pour effectuer des calculs sur les dates (ajouter/soustraire des jours)
from django.core.paginator import Paginator  # Pour diviser les résultats en pages


# =============================================================================
# FONCTIONS DE VISUALISATION PUBLIQUES
# =============================================================================

# Fonction pour la page d'accueil accessible à tous les visiteurs
def accueil(request):
    voitures = Voiture.objects.all()  # Récupère toutes les voitures de la base de données sans filtrage
    return render(request, 'ventelocavoiture/index.html', {'voitures': voitures})  # Affiche le template index.html avec les voitures

# Fonction pour afficher les détails d'une voiture spécifique
def detail_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)  # Récupère la voiture avec l'ID spécifié ou renvoie une erreur 404 si elle n'existe pas
    utilisateur_connecte = 'utilisateur_id' in request.session  # Vérifie si un utilisateur est connecté en vérifiant la présence de son ID dans la session
    return render(request, 'ventelocavoiture/detail_voiture.html', {
        'voiture': voiture,
        'utilisateur_connecte': utilisateur_connecte  # Passe cette information au template pour afficher des options différentes selon l'état de connexion
    })
    
# Fonction pour afficher uniquement les voitures à vendre
def voitures_a_vendre(request):
    # Récupère les voitures disponibles ET qui sont soit à vendre, soit à vendre et à louer
    voitures = Voiture.objects.filter(etat='disponible').filter(
        models.Q(type_offre='vente') | models.Q(type_offre='les_deux')  # Opérateur OR logique avec Q
    )
    return render(request, 'ventelocavoiture/voitures_a_vendre.html', {
        'voitures': voitures,
        'categorie': 'vente'  # Pour indiquer au template la catégorie active
    })

# Fonction pour afficher uniquement les voitures à louer
def voitures_a_louer(request):
    # Récupère les voitures disponibles ET qui sont soit à louer, soit à vendre et à louer
    voitures = Voiture.objects.filter(etat='disponible').filter(
        models.Q(type_offre='location') | models.Q(type_offre='les_deux')  # Opérateur OR logique avec Q
    )
    return render(request, 'ventelocavoiture/voitures_a_louer.html', {
        'voitures': voitures,
        'categorie': 'location'  # Pour indiquer au template la catégorie active
    })
    
# =============================================================================
# FONCTIONS D'AUTHENTIFICATION
# =============================================================================
    
# Fonction pour créer un nouveau compte utilisateur
def inscription(request):
    if request.method == 'POST':  # Si le formulaire a été soumis (méthode POST)
        # Récupération des données du formulaire soumis
        nom = request.POST.get('nom')  # Obtient la valeur du champ 'nom'
        prenom = request.POST.get('prenom')
        sexe = request.POST.get('sexe')
        numeros = request.POST.get('numeros')  # Numéros de téléphone
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Vérifier si l'email existe déjà pour éviter les doublons
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà !")  # Affiche un message d'erreur visible à l'utilisateur
            return render(request, 'ventelocavoiture/inscription_voiture.html')  # Réaffiche le formulaire d'inscription

        # Créer un nouvel utilisateur s'il n'existe pas déjà
        try:
            utilisateur = Utilisateur(
                nom=nom,
                prenom=prenom,
                sexe=sexe,
                numeros=numeros,
                email=email,
                password=make_password(password)  # Crypte le mot de passe pour ne pas le stocker en clair dans la base de données
            )
            utilisateur.save()  # Enregistre l'utilisateur dans la base de données
            messages.success(request, "Inscription réussie !")  # Message de succès
            return redirect('ventelocavoiture:connexion')  # Redirige vers la page de connexion
        except Exception as e:
            # En cas d'erreur lors de la création de l'utilisateur
            messages.error(request, "Une erreur s'est produite lors de l'inscription.")
            return render(request, 'ventelocavoiture/inscription_voiture.html')
        
    # Si la méthode est GET (affichage initial du formulaire)
    return render(request, 'ventelocavoiture/inscription_voiture.html')


# Fonction pour connecter un utilisateur existant
def connexion(request):
    if request.method == 'POST':  # Si le formulaire a été soumis
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            utilisateur = Utilisateur.objects.get(email=email)  # Cherche l'utilisateur par son email
            if check_password(password, utilisateur.password):  # Vérifie si le mot de passe correspond à celui crypté en base
                # Stocker l'ID de l'utilisateur dans la session pour le maintenir connecté
                request.session['utilisateur_id'] = utilisateur.id
                return redirect('ventelocavoiture:accueil')  # Redirection vers l'accueil après connexion réussie
            else:
                messages.error(request, "Mot de passe incorrect")  # Message d'erreur si le mot de passe est incorrect
        except Utilisateur.DoesNotExist:
            messages.error(request, "Email non trouvé")  # Message d'erreur si l'email n'existe pas
        
        return render(request, 'ventelocavoiture/connexion_voiture.html')  # Réaffiche le formulaire en cas d'erreur

    # Si la méthode est GET (affichage initial du formulaire)
    return render(request, 'ventelocavoiture/connexion_voiture.html')


# Décorateur personnalisé pour vérifier si l'utilisateur est connecté
# Ce décorateur permet de protéger les vues qui nécessitent une authentification
def utilisateur_connecte_requis(view_func):
    @wraps(view_func)  # Préserve les métadonnées de la fonction d'origine
    def _wrapped_view(request, *args, **kwargs):
        # Vérifie si l'ID utilisateur est présent dans la session
        if 'utilisateur_id' not in request.session:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('ventelocavoiture:connexion')  # Redirige vers la page de connexion si non connecté
        # Si l'utilisateur est connecté, exécute la vue originale
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# =============================================================================
# FONCTIONS DE TRANSACTION
# =============================================================================

# Fonction pour acheter une voiture (accessible uniquement aux utilisateurs connectés)
@utilisateur_connecte_requis  # Applique le décorateur pour vérifier la connexion
def acheter_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)  # Récupère la voiture par son ID
    
    # Récupère l'objet utilisateur connecté à partir de la session
    utilisateur = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])
    
    # Vérifier si la voiture est disponible à la vente
    # Une voiture doit être disponible ET (à vendre OU à vendre et à louer)
    if voiture.etat != 'disponible' or (voiture.type_offre != 'vente' and voiture.type_offre != 'les_deux'):
        messages.error(request, "Cette voiture n'est pas disponible à la vente.")
        return redirect('ventelocavoiture:detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':  # Si le formulaire de confirmation a été soumis
        # Créer une nouvelle transaction d'achat
        transaction = Transaction(
            utilisateur=utilisateur,
            voiture=voiture,
            type_transaction='achat',
            montant=voiture.prix_vente  # Utilise le prix de vente enregistré
        )
        transaction.save()
        
        # Mettre à jour l'état de la voiture pour qu'elle ne soit plus disponible
        voiture.etat = 'vendu'
        voiture.save()
        
        messages.success(request, "Félicitations! Vous avez acheté cette voiture.")
        return redirect('ventelocavoiture:accueil')
    
    # Si la méthode est GET, affiche le formulaire de confirmation d'achat
    return render(request, 'ventelocavoiture/confirmer_achat.html', {
        'voiture': voiture,
        'utilisateur': utilisateur
    })


# Fonction pour louer une voiture (accessible uniquement aux utilisateurs connectés)
@utilisateur_connecte_requis  # Applique le décorateur pour vérifier la connexion
def louer_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)  # Récupère la voiture par son ID
    
    # Récupère l'objet utilisateur connecté à partir de la session
    utilisateur = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])
    
    # Vérifier si la voiture est disponible à la location
    # Une voiture doit être disponible ET (à louer OU à vendre et à louer)
    if voiture.etat != 'disponible' or (voiture.type_offre != 'location' and voiture.type_offre != 'les_deux'):
        messages.error(request, "Cette voiture n'est pas disponible à la location.")
        return redirect('ventelocavoiture:detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':  # Si le formulaire de confirmation a été soumis
        date_debut = request.POST.get('date_debut')  # Date de début de location
        date_fin = request.POST.get('date_fin')  # Date de fin de location
        
        # Calculer le nombre de jours de location
        from datetime import datetime
        date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')  # Convertit la chaîne en objet date
        date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
        nb_jours = (date_fin_obj - date_debut_obj).days  # Calcule la différence en jours
        
        # Calculer le montant total de la location
        montant_total = voiture.prix_location_jour * nb_jours
        
        # Créer une nouvelle transaction de location
        transaction = Transaction(
            utilisateur=utilisateur,
            voiture=voiture,
            type_transaction='location',
            montant=montant_total,
            date_debut_location=date_debut,
            date_fin_location=date_fin
        )
        transaction.save()
        
        # Mettre à jour l'état de la voiture pour qu'elle ne soit plus disponible
        voiture.etat = 'loué'
        voiture.save()
        
        messages.success(request, f"Félicitations! Vous avez loué cette voiture pour {nb_jours} jours.")
        return redirect('ventelocavoiture:accueil')
    
    # Si la méthode est GET, affiche le formulaire de confirmation de location
    return render(request, 'ventelocavoiture/confirmer_location.html', {
        'voiture': voiture,
        'utilisateur': utilisateur
    })
    
# Fonction pour déconnecter l'utilisateur
def deconnexion(request):
    # Supprimer l'ID utilisateur de la session pour le déconnecter
    if 'utilisateur_id' in request.session:
        del request.session['utilisateur_id']  # Supprime l'ID de la session
    
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('ventelocavoiture:accueil')  # Redirige vers la page d'accueil


# =============================================================================
# FONCTIONS DE RECHERCHE
# =============================================================================

# Fonction pour rechercher des voitures avec différents critères
def recherche_voitures(request):
    # Récupère tous les paramètres de recherche à partir de l'URL (paramètres GET)
    query = request.GET.get('q', '')  # Terme de recherche général
    type_offre = request.GET.get('type_offre', '')  # Type d'offre (vente, location, les_deux)
    marque = request.GET.get('marque', '')  # Marque de la voiture
    prix_min = request.GET.get('prix_min', '')  # Prix minimum
    prix_max = request.GET.get('prix_max', '')  # Prix maximum
    
    # Commence avec toutes les voitures
    voitures = Voiture.objects.all()
    
    # Filtre par terme de recherche (marque, modèle ou description)
    if query:
        voitures = voitures.filter(
            Q(marque__icontains=query) |  # Recherche insensible à la casse dans la marque
            Q(modele__icontains=query) |  # Recherche insensible à la casse dans le modèle
            Q(description__icontains=query)  # Recherche insensible à la casse dans la description
        )
    
    # Filtre par type d'offre
    if type_offre:
        if type_offre == 'les_deux':
            voitures = voitures.filter(type_offre=type_offre)
        else:
            # Si on cherche vente ou location, inclut aussi les voitures disponibles pour les deux
            voitures = voitures.filter(Q(type_offre=type_offre) | Q(type_offre='les_deux'))
    
    # Filtre par marque
    if marque:
        voitures = voitures.filter(marque=marque)  # Filtre exact sur la marque
    
    # Filtre par prix minimum (vente ou location)
    if prix_min:
        voitures = voitures.filter(Q(prix_vente__gte=prix_min) | Q(prix_location_jour__gte=prix_min))
    
    # Filtre par prix maximum (vente ou location)
    if prix_max:
        voitures = voitures.filter(Q(prix_vente__lte=prix_max) | Q(prix_location_jour__lte=prix_max))
    
    # Obtenir une liste unique de toutes les marques pour le filtre
    marques = Voiture.objects.values_list('marque', flat=True).distinct()
    
    context = {
        'voitures': voitures,  # Voitures filtrées
        'query': query,  # Terme de recherche (pour l'afficher dans l'interface)
        'marques': marques,  # Liste des marques pour le filtre
    }
    
    return render(request, 'ventelocavoiture/resultats_recherche.html', context)


# =============================================================================
# FONCTIONS D'ADMINISTRATION
# =============================================================================

# Décorateur pour vérifier si l'utilisateur est un administrateur
def admin_requis(view_func):
    @wraps(view_func)  # Préserve les métadonnées de la fonction d'origine
    def _wrapped_view(request, *args, **kwargs):
        # Vérifie d'abord si l'utilisateur est connecté
        if 'utilisateur_id' not in request.session:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('ventelocavoiture:connexion')
        
        # Vérifie ensuite si l'utilisateur est un administrateur
        try:
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            
            # Vérifie si l'attribut is_admin est True
            if not getattr(utilisateur, 'is_admin', False):
                messages.error(request, "Vous n'avez pas les droits d'administrateur.")
                return redirect('ventelocavoiture:accueil')
        except Utilisateur.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")
            return redirect('ventelocavoiture:connexion')
            
        # Si l'utilisateur est un administrateur, exécute la vue originale
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Vue du tableau de bord principal pour les administrateurs
@admin_requis  # Applique le décorateur pour vérifier les droits d'administration
def dashboard(request):
    # Statistiques sur les voitures
    total_voitures = Voiture.objects.count()  # Nombre total de voitures
    voitures_disponibles = Voiture.objects.filter(etat='disponible').count()  # Nombre de voitures disponibles
    voitures_vendues = Voiture.objects.filter(etat='vendu').count()  # Nombre de voitures vendues
    voitures_louees = Voiture.objects.filter(etat='loué').count()  # Nombre de voitures louées
    
    # Statistiques sur les utilisateurs
    total_utilisateurs = Utilisateur.objects.count()  # Nombre total d'utilisateurs
    
    # Statistiques sur les transactions
    total_transactions = Transaction.objects.count()  # Nombre total de transactions
    # Somme des montants pour les transactions d'achat
    revenus_ventes = Transaction.objects.filter(type_transaction='achat').aggregate(Sum('montant'))['montant__sum'] or 0
    # Somme des montants pour les transactions de location
    revenus_locations = Transaction.objects.filter(type_transaction='location').aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Récupère les 5 transactions les plus récentes pour les afficher
    transactions_recentes = Transaction.objects.all().order_by('-date_transaction')[:5]
    
    context = {
        'total_voitures': total_voitures,
        'voitures_disponibles': voitures_disponibles,
        'voitures_vendues': voitures_vendues,
        'voitures_louees': voitures_louees,
        'total_utilisateurs': total_utilisateurs,
        'total_transactions': total_transactions,
        'revenus_ventes': revenus_ventes,
        'revenus_locations': revenus_locations,
        'transactions_recentes': transactions_recentes,
        'section': 'apercu'  # Indique la section active dans le menu
    }
    
    return render(request, 'ventelocavoiture/dashboard.html', context)

# Vue pour gérer les voitures dans le tableau de bord admin
@admin_requis
def dashboard_voitures(request):
    # Récupère toutes les voitures, triées par date d'ajout (la plus récente d'abord)
    voitures = Voiture.objects.all().order_by('-date_ajout')
    
    # Système de pagination pour ne pas afficher trop de voitures à la fois
    paginator = Paginator(voitures, 10)  # 10 voitures par page
    page_number = request.GET.get('page')  # Récupère le numéro de page demandé
    voitures_page = paginator.get_page(page_number)  # Récupère les voitures pour la page demandée
    
    return render(request, 'ventelocavoiture/dashboard_voitures.html', {
        'voitures': voitures_page,
        'section': 'voitures'  # Indique la section active dans le menu
    })

# Vue pour ajouter une nouvelle voiture dans le tableau de bord admin
@admin_requis
def dashboard_ajouter_voiture(request):
    if request.method == 'POST':  # Si le formulaire a été soumis
        # Récupère toutes les données du formulaire
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        annee = request.POST.get('annee')
        kilometrage = request.POST.get('kilometrage')
        prix_vente = request.POST.get('prix_vente') or None  # Si vide, met None
        prix_location_jour = request.POST.get('prix_location_jour') or None  # Si vide, met None
        description = request.POST.get('description')
        etat = request.POST.get('etat')
        type_offre = request.POST.get('type_offre')
        image_principale = request.FILES.get('image')  # Récupère le fichier téléchargé
        
        # Créer la nouvelle voiture
        try:
            voiture = Voiture(
                marque=marque,
                modele=modele,
                annee=annee,
                kilometrage=kilometrage,
                prix_vente=prix_vente,
                prix_location_jour=prix_location_jour,
                description=description,
                etat=etat,
                type_offre=type_offre,
                image=image_principale
            )
            voiture.save()  # Enregistre la voiture dans la base de données
            
            # Traiter les images supplémentaires (peut y en avoir plusieurs)
            for img in request.FILES.getlist('images_supplementaires'):
                ImageVoiture.objects.create(voiture=voiture, image=img)  # Crée une entrée pour chaque image supplémentaire
                
            messages.success(request, "Voiture ajoutée avec succès!")
            return redirect('ventelocavoiture:dashboard_voitures')  # Redirige vers la liste des voitures
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de la voiture: {str(e)}")
    
    # Si la méthode est GET, affiche le formulaire d'ajout
    return render(request, 'ventelocavoiture/dashboard_ajouter_voiture.html', {
        'section': 'voitures'  # Indique la section active dans le menu
    })

# Vue pour modifier une voiture existante dans le tableau de bord admin
@admin_requis
def dashboard_modifier_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)  # Récupère la voiture à modifier
    
    if request.method == 'POST':  # Si le formulaire a été soumis
        # Met à jour les données de la voiture avec les valeurs du formulaire
        voiture.marque = request.POST.get('marque')
        voiture.modele = request.POST.get('modele')
        voiture.annee = int(request.POST.get('annee'))  # Convertit en entier
        voiture.kilometrage = int(request.POST.get('kilometrage'))  # Convertit en entier
        voiture.prix_vente = request.POST.get('prix_vente') or None  # Si vide, met None
        voiture.prix_location_jour = request.POST.get('prix_location_jour') or None  # Si vide, met None
        voiture.description = request.POST.get('description')
        voiture.etat = request.POST.get('etat')
        voiture.type_offre = request.POST.get('type_offre')
        
        # Met à jour l'image principale si une nouvelle est fournie
        if 'image' in request.FILES:
            voiture.image = request.FILES['image']
        
        try:
            voiture.save()  # Enregistre les modifications
            
            # Traite les nouvelles images supplémentaires
            for img in request.FILES.getlist('images_supplementaires'):
                ImageVoiture.objects.create(voiture=voiture, image=img)
                
            messages.success(request, "Voiture modifiée avec succès!")
            return redirect('ventelocavoiture:dashboard_voitures')  # Redirige vers la liste des voitures
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification de la voiture: {str(e)}")
    
    # Si la méthode est GET, affiche le formulaire de modification avec les données actuelles
    return render(request, 'ventelocavoiture/dashboard_modifier_voiture.html', {
        'voiture': voiture,
        'section': 'voitures'  # Indique la section active dans le menu
    })

# Vue pour supprimer une voiture dans le tableau de bord admin
@admin_requis
def dashboard_supprimer_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)  # Récupère la voiture à supprimer
    
    if request.method == 'POST':  # Si le formulaire de confirmation a été soumis
        try:
            voiture.delete()  # Supprime la voiture de la base de données
            messages.success(request, "Voiture supprimée avec succès!")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de la voiture: {str(e)}")
        
        return redirect('ventelocavoiture:dashboard_voitures')  # Redirige vers la liste des voitures
    
    # Si la méthode est GET, affiche la page de confirmation de suppression
    return render(request, 'ventelocavoiture/dashboard_confirmer_suppression.html', {
        'voiture': voiture,
        'section': 'voitures',  # Indique la section active dans le menu
        'type': 'voiture'  # Indique qu'il s'agit d'une voiture (pour le message)
    })

# Vue pour gérer les utilisateurs dans le tableau de bord admin
@admin_requis
def dashboard_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()  # Récupère tous les utilisateurs
    
    # Système de pagination pour ne pas afficher trop d'utilisateurs à la fois
    paginator = Paginator(utilisateurs, 10)  # 10 utilisateurs par page
    page_number = request.GET.get('page')  # Récupère le numéro de page demandé
    utilisateurs_page = paginator.get_page(page_number)  # Récupère les utilisateurs pour la page demandée
    
    return render(request, 'ventelocavoiture/dashboard_utilisateurs.html', {
        'utilisateurs': utilisateurs_page,
        'section': 'utilisateurs'  # Indique la section active dans le menu
    })

# Vue pour gérer les transactions dans le tableau de bord admin
@admin_requis
def dashboard_transactions(request):
    # Récupère toutes les transactions, triées par date (la plus récente d'abord)
    transactions = Transaction.objects.all().order_by('-date_transaction')
    
    # Système de pagination pour ne pas afficher trop de transactions à la fois
    paginator = Paginator(transactions, 10)  # 10 transactions par page
    page_number = request.GET.get('page')  # Récupère le numéro de page demandé
    transactions_page = paginator.get_page(page_number)  # Récupère les transactions pour la page demandée
    
    return render(request, 'ventelocavoiture/dashboard_transactions.html', {
        'transactions': transactions_page,
        'section': 'transactions'  # Indique la section active dans le menu
    })