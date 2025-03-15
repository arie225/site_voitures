from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from .models import Voiture, ImageVoiture, Utilisateur, Transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator




def accueil(request):
    voitures = Voiture.objects.all()
    return render(request, 'ventelocavoiture/index.html', {'voitures': voitures})

def detail_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)
    utilisateur_connecte = 'utilisateur_id' in request.session
    return render(request, 'ventelocavoiture/detail_voiture.html', {
        'voiture': voiture,
        'utilisateur_connecte': utilisateur_connecte
    })
    
    
def voitures_a_vendre(request):
    # Récupère les voitures à vendre (type_offre = 'vente' ou 'les_deux')
    voitures = Voiture.objects.filter(etat='disponible').filter(
        models.Q(type_offre='vente') | models.Q(type_offre='les_deux')
    )
    return render(request, 'ventelocavoiture/voitures_a_vendre.html', {
        'voitures': voitures,
        'categorie': 'vente'
    })

def voitures_a_louer(request):
    # Récupère les voitures à louer (type_offre = 'location' ou 'les_deux')
    voitures = Voiture.objects.filter(etat='disponible').filter(
        models.Q(type_offre='location') | models.Q(type_offre='les_deux')
    )
    return render(request, 'ventelocavoiture/voitures_a_louer.html', {
        'voitures': voitures,
        'categorie': 'location'
    })
    
def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        sexe = request.POST.get('sexe')
        numeros = request.POST.get('numeros')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Vérifier si l'email existe déjà
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà !")
            return render(request, 'ventelocavoiture/inscription_voiture.html')

        # Créer un nouvel utilisateur
        try:
            utilisateur = Utilisateur(
                nom=nom,
                prenom=prenom,
                sexe=sexe,
                numeros=numeros,
                email=email,
                password=make_password(password)  # Crypter le mot de passe
            )
            utilisateur.save()
            messages.success(request, "Inscription réussie !")
            return redirect('ventelocavoiture:connexion')
        except Exception as e:
            messages.error(request, "Une erreur s'est produite lors de l'inscription.")
            return render(request, 'ventelocavoiture/inscription_voiture.html')
        
    return render(request, 'ventelocavoiture/inscription_voiture.html')


# Dans views.py - Modifiez la fonction connexion
def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            utilisateur = Utilisateur.objects.get(email=email)
            if check_password(password, utilisateur.password):
                # Stocker les informations de l'utilisateur dans la session
                request.session['utilisateur_id'] = utilisateur.id
                return redirect('ventelocavoiture:accueil')  # Redirection vers l'accueil
            else:
                messages.error(request, "Mot de passe incorrect")
        except Utilisateur.DoesNotExist:
            messages.error(request, "Email non trouvé")
        
        return render(request, 'ventelocavoiture/connexion_voiture.html')

    return render(request, 'ventelocavoiture/connexion_voiture.html')


# Dans views.py - Modifiez les fonctions acheter_voiture et louer_voiture
def utilisateur_connecte_requis(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'utilisateur_id' not in request.session:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('ventelocavoiture:connexion')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@utilisateur_connecte_requis
def acheter_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    # Récupérer l'objet utilisateur
    utilisateur = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])
    
    # Vérifier si la voiture est disponible à la vente
    if voiture.etat != 'disponible' or (voiture.type_offre != 'vente' and voiture.type_offre != 'les_deux'):
        messages.error(request, "Cette voiture n'est pas disponible à la vente.")
        return redirect('ventelocavoiture:detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':
        # Créer la transaction
        transaction = Transaction(
            utilisateur=utilisateur,
            voiture=voiture,
            type_transaction='achat',
            montant=voiture.prix_vente
        )
        transaction.save()
        
        # Mettre à jour l'état de la voiture
        voiture.etat = 'vendu'
        voiture.save()
        
        messages.success(request, "Félicitations! Vous avez acheté cette voiture.")
        return redirect('ventelocavoiture:accueil')
    
    return render(request, 'ventelocavoiture/confirmer_achat.html', {
        'voiture': voiture,
        'utilisateur': utilisateur
    })


@utilisateur_connecte_requis
def louer_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    # Récupérer l'objet utilisateur
    utilisateur = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])
    
    # Vérifier si la voiture est disponible à la location
    if voiture.etat != 'disponible' or (voiture.type_offre != 'location' and voiture.type_offre != 'les_deux'):
        messages.error(request, "Cette voiture n'est pas disponible à la location.")
        return redirect('ventelocavoiture:detail_voiture', voiture_id=voiture_id)
    
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        # Calculer le nombre de jours
        from datetime import datetime
        date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
        date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
        nb_jours = (date_fin_obj - date_debut_obj).days
        
        # Calculer le montant total
        montant_total = voiture.prix_location_jour * nb_jours
        
        # Créer la transaction
        transaction = Transaction(
            utilisateur=utilisateur,
            voiture=voiture,
            type_transaction='location',
            montant=montant_total,
            date_debut_location=date_debut,
            date_fin_location=date_fin
        )
        transaction.save()
        
        # Mettre à jour l'état de la voiture
        voiture.etat = 'loué'
        voiture.save()
        
        messages.success(request, f"Félicitations! Vous avez loué cette voiture pour {nb_jours} jours.")
        return redirect('ventelocavoiture:accueil')
    
    return render(request, 'ventelocavoiture/confirmer_location.html', {
        'voiture': voiture,
        'utilisateur': utilisateur
    })
    
    
def deconnexion(request):
    # Supprimer l'ID utilisateur de la session
    if 'utilisateur_id' in request.session:
        del request.session['utilisateur_id']
    
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('ventelocavoiture:accueil')

# fonction pour la bare de recherche
def recherche_voitures(request):
    query = request.GET.get('q', '')
    type_offre = request.GET.get('type_offre', '')
    marque = request.GET.get('marque', '')
    prix_min = request.GET.get('prix_min', '')
    prix_max = request.GET.get('prix_max', '')
    
    voitures = Voiture.objects.all()
    
    if query:
        voitures = voitures.filter(
            Q(marque__icontains=query) | 
            Q(modele__icontains=query) |
            Q(description__icontains=query)
        )
    
    if type_offre:
        if type_offre == 'les_deux':
            voitures = voitures.filter(type_offre=type_offre)
        else:
            voitures = voitures.filter(Q(type_offre=type_offre) | Q(type_offre='les_deux'))
    
    if marque:
        voitures = voitures.filter(marque=marque)
    
    if prix_min:
        voitures = voitures.filter(Q(prix_vente__gte=prix_min) | Q(prix_location_jour__gte=prix_min))
    
    if prix_max:
        voitures = voitures.filter(Q(prix_vente__lte=prix_max) | Q(prix_location_jour__lte=prix_max))
    
    # Obtenir une liste unique de marques pour le filtre
    marques = Voiture.objects.values_list('marque', flat=True).distinct()
    
    context = {
        'voitures': voitures,
        'query': query,
        'marques': marques,
    }
    
    return render(request, 'ventelocavoiture/resultats_recherche.html', context)

# Décorateur pour vérifier si l'utilisateur est un administrateur
def admin_requis(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'utilisateur_id' not in request.session:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('ventelocavoiture:connexion')
        
        # Ici vous pouvez ajouter votre propre logique pour vérifier si l'utilisateur est admin
        # Par exemple, ajouter un champ is_admin dans le modèle Utilisateur
        try:
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            # Supposons que vous avez ajouté un champ is_admin (voir ci-dessous dans les modifications du modèle)
            if not getattr(utilisateur, 'is_admin', False):
                messages.error(request, "Vous n'avez pas les droits d'administrateur.")
                return redirect('ventelocavoiture:accueil')
        except Utilisateur.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")
            return redirect('ventelocavoiture:connexion')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_requis
def dashboard(request):
    # Statistiques générales
    total_voitures = Voiture.objects.count()
    voitures_disponibles = Voiture.objects.filter(etat='disponible').count()
    voitures_vendues = Voiture.objects.filter(etat='vendu').count()
    voitures_louees = Voiture.objects.filter(etat='loué').count()
    
    total_utilisateurs = Utilisateur.objects.count()
    
    total_transactions = Transaction.objects.count()
    revenus_ventes = Transaction.objects.filter(type_transaction='achat').aggregate(Sum('montant'))['montant__sum'] or 0
    revenus_locations = Transaction.objects.filter(type_transaction='location').aggregate(Sum('montant'))['montant__sum'] or 0
    
    # Dernières transactions
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
        'section': 'apercu'
    }
    
    return render(request, 'ventelocavoiture/dashboard.html', context)

@admin_requis
def dashboard_voitures(request):
    voitures = Voiture.objects.all().order_by('-date_ajout')
    
    # Pagination
    paginator = Paginator(voitures, 10)  # 10 voitures par page
    page_number = request.GET.get('page')
    voitures_page = paginator.get_page(page_number)
    
    return render(request, 'ventelocavoiture/dashboard_voitures.html', {
        'voitures': voitures_page,
        'section': 'voitures'
    })

@admin_requis
def dashboard_ajouter_voiture(request):
    if request.method == 'POST':
        # Traiter le formulaire d'ajout de voiture
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        annee = request.POST.get('annee')
        kilometrage = request.POST.get('kilometrage')
        prix_vente = request.POST.get('prix_vente') or None
        prix_location_jour = request.POST.get('prix_location_jour') or None
        description = request.POST.get('description')
        etat = request.POST.get('etat')
        type_offre = request.POST.get('type_offre')
        image_principale = request.FILES.get('image')
        
        # Créer la voiture
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
            voiture.save()
            
            # Traiter les images supplémentaires
            for img in request.FILES.getlist('images_supplementaires'):
                ImageVoiture.objects.create(voiture=voiture, image=img)
                
            messages.success(request, "Voiture ajoutée avec succès!")
            return redirect('ventelocavoiture:dashboard_voitures')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de la voiture: {str(e)}")
    
    return render(request, 'ventelocavoiture/dashboard_ajouter_voiture.html', {
        'section': 'voitures'
    })

@admin_requis
def dashboard_modifier_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    if request.method == 'POST':
        # Traiter le formulaire de modification
        voiture.marque = request.POST.get('marque')
        voiture.modele = request.POST.get('modele')
        voiture.annee = int(request.POST.get('annee'))
        voiture.kilometrage = int(request.POST.get('kilometrage'))
        voiture.prix_vente = request.POST.get('prix_vente') or None
        voiture.prix_location_jour = request.POST.get('prix_location_jour') or None
        voiture.description = request.POST.get('description')
        voiture.etat = request.POST.get('etat')
        voiture.type_offre = request.POST.get('type_offre')
        
        if 'image' in request.FILES:
            voiture.image = request.FILES['image']
        
        try:
            voiture.save()
            
            # Traiter les images supplémentaires
            for img in request.FILES.getlist('images_supplementaires'):
                ImageVoiture.objects.create(voiture=voiture, image=img)
                
            messages.success(request, "Voiture modifiée avec succès!")
            return redirect('ventelocavoiture:dashboard_voitures')
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification de la voiture: {str(e)}")
    
    return render(request, 'ventelocavoiture/dashboard_modifier_voiture.html', {
        'voiture': voiture,
        'section': 'voitures'
    })

@admin_requis
def dashboard_supprimer_voiture(request, voiture_id):
    voiture = get_object_or_404(Voiture, id=voiture_id)
    
    if request.method == 'POST':
        try:
            voiture.delete()
            messages.success(request, "Voiture supprimée avec succès!")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de la voiture: {str(e)}")
        
        return redirect('ventelocavoiture:dashboard_voitures')
    
    return render(request, 'ventelocavoiture/dashboard_confirmer_suppression.html', {
        'voiture': voiture,
        'section': 'voitures',
        'type': 'voiture'
    })

@admin_requis
def dashboard_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    
    # Pagination
    paginator = Paginator(utilisateurs, 10)  # 10 utilisateurs par page
    page_number = request.GET.get('page')
    utilisateurs_page = paginator.get_page(page_number)
    
    return render(request, 'ventelocavoiture/dashboard_utilisateurs.html', {
        'utilisateurs': utilisateurs_page,
        'section': 'utilisateurs'
    })

@admin_requis
def dashboard_transactions(request):
    transactions = Transaction.objects.all().order_by('-date_transaction')
    
    # Pagination
    paginator = Paginator(transactions, 10)  # 10 transactions par page
    page_number = request.GET.get('page')
    transactions_page = paginator.get_page(page_number)
    
    return render(request, 'ventelocavoiture/dashboard_transactions.html', {
        'transactions': transactions_page,
        'section': 'transactions'
    })