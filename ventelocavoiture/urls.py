from django.urls import path
from . import views

app_name = 'ventelocavoiture'  # Définit l'espace de nommage pour l'application
urlpatterns = [
    # Routes publiques
    path('', views.accueil, name='accueil'),  # Page d'accueil
    path('voiture/<int:voiture_id>/', views.detail_voiture, name='detail_voiture'),  # Détails d'une voiture
    path('voitures-a-vendre/', views.voitures_a_vendre, name='voitures_a_vendre'),  # Liste des voitures à vendre
    path('voitures-a-louer/', views.voitures_a_louer, name='voitures_a_louer'),  # Liste des voitures à louer
    path("connexion/", views.connexion, name="connexion"),  # Page de connexion
    path('inscription/', views.inscription, name='inscription'),  # Page d'inscription
    
    # Routes pour les actions utilisateur
    path('voiture/<int:voiture_id>/acheter/', views.acheter_voiture, name='acheter_voiture'),  # Achat de voiture
    path('voiture/<int:voiture_id>/louer/', views.louer_voiture, name='louer_voiture'),  # Location de voiture
    path('deconnexion/', views.deconnexion, name='deconnexion'),  # Déconnexion
    path('recherche/', views.recherche_voitures, name='recherche'),  # Recherche de voitures
    
    # Routes d'administration (dashboard)
    path('dashboard/', views.dashboard, name='dashboard'),  # Tableau de bord principal
    path('dashboard/voitures/', views.dashboard_voitures, name='dashboard_voitures'),  # Gestion des voitures
    path('dashboard/voitures/ajouter/', views.dashboard_ajouter_voiture, name='dashboard_ajouter_voiture'),  # Ajout de voiture
    path('dashboard/voitures/<int:voiture_id>/modifier/', views.dashboard_modifier_voiture, name='dashboard_modifier_voiture'),  # Modification de voiture
    path('dashboard/voitures/<int:voiture_id>/supprimer/', views.dashboard_supprimer_voiture, name='dashboard_supprimer_voiture'),  # Suppression de voiture
    path('dashboard/utilisateurs/', views.dashboard_utilisateurs, name='dashboard_utilisateurs'),  # Gestion des utilisateurs
    path('dashboard/transactions/', views.dashboard_transactions, name='dashboard_transactions'),  # Liste des transactions
]