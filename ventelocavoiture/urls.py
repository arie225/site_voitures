from django.urls import path
from . import views

app_name = 'ventelocavoiture'
urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('voiture/<int:voiture_id>/', views.detail_voiture, name='detail_voiture'),
    path('voitures-a-vendre/', views.voitures_a_vendre, name='voitures_a_vendre'),
    path('voitures-a-louer/', views.voitures_a_louer, name='voitures_a_louer'),
    path("connexion/", views.connexion, name="connexion"),
    path('inscription/', views.inscription, name='inscription'),
    path('voiture/<int:voiture_id>/acheter/', views.acheter_voiture, name='acheter_voiture'),
    path('voiture/<int:voiture_id>/louer/', views.louer_voiture, name='louer_voiture'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('recherche/', views.recherche_voitures, name='recherche'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/voitures/', views.dashboard_voitures, name='dashboard_voitures'),
    path('dashboard/voitures/ajouter/', views.dashboard_ajouter_voiture, name='dashboard_ajouter_voiture'),
    path('dashboard/voitures/<int:voiture_id>/modifier/', views.dashboard_modifier_voiture, name='dashboard_modifier_voiture'),
    path('dashboard/voitures/<int:voiture_id>/supprimer/', views.dashboard_supprimer_voiture, name='dashboard_supprimer_voiture'),
    path('dashboard/utilisateurs/', views.dashboard_utilisateurs, name='dashboard_utilisateurs'),
    path('dashboard/transactions/', views.dashboard_transactions, name='dashboard_transactions'),
        
]