from django.db import models
from django.core.validators import MinValueValidator

class Voiture(models.Model):
    """
    Modèle représentant une voiture dans le système.
    Une voiture peut être à vendre, à louer ou les deux.
    """
    # Options pour l'état de la voiture
    ETAT_CHOIX = [
        ('disponible', 'Disponible'),
        ('vendu', 'Vendu'),
        ('loué', 'Loué'),
    ]
    
    # Options pour le type d'offre
    TYPE_CHOIX = [
        ('vente', 'À vendre'),
        ('location', 'À louer'),
        ('les_deux', 'À vendre et à louer'),
    ]
    
    # Caractéristiques de base de la voiture
    marque = models.CharField(max_length=100)  # Marque de la voiture
    modele = models.CharField(max_length=100)  # Modèle de la voiture
    annee = models.IntegerField()  # Année de fabrication
    kilometrage = models.IntegerField()  # Kilométrage actuel
    
    # Prix de vente et de location (optionnels selon le type d'offre)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_location_jour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    description = models.TextField()  # Description détaillée
    etat = models.CharField(max_length=20, choices=ETAT_CHOIX, default='disponible')  # État actuel
    type_offre = models.CharField(max_length=20, choices=TYPE_CHOIX, default='vente')  # Type d'offre
    date_ajout = models.DateTimeField(auto_now_add=True)  # Date d'ajout au système
    image = models.ImageField(upload_to='images/')  # Image principale
    
    def __str__(self):
        """Représentation textuelle de la voiture"""
        return f"{self.marque} {self.modele}"

class ImageVoiture(models.Model):
    """
    Modèle représentant des images supplémentaires pour une voiture.
    Relation un-à-plusieurs avec le modèle Voiture.
    """
    voiture = models.ForeignKey(Voiture, related_name='images', on_delete=models.CASCADE)  # Lien vers la voiture
    image = models.ImageField(upload_to='images/')  # Chemin de l'image
    
    def __str__(self):
        """Représentation textuelle de l'image"""
        return f"Image de {self.voiture}"
    
    
class Utilisateur(models.Model):
    """
    Modèle représentant un utilisateur du système.
    Implémentation personnalisée d'utilisateur au lieu du modèle User de Django.
    """
    nom = models.CharField(max_length=100)  # Nom de famille
    prenom = models.CharField(max_length=100)  # Prénom
    sexe = models.CharField(max_length=1, choices=[('F', 'Feminin'), ('M', 'Masculin')])  # Genre
    numeros = models.CharField(max_length=100, null=True)  # Numéro de téléphone (optionnel)
    email = models.EmailField(unique=True)  # Email (identifiant unique)
    password = models.CharField(max_length=100)  # Mot de passe (stocké hashé)
    is_admin = models.BooleanField(default=False)  # Indicateur de droits administrateur

    def __str__(self):
        """Représentation textuelle de l'utilisateur"""
        return f"{self.nom} {self.prenom}"
    

class Transaction(models.Model):
    """
    Modèle représentant une transaction d'achat ou de location de voiture.
    """
    TYPE_TRANSACTION = [
        ('achat', 'Achat'),
        ('location', 'Location'),
    ]
    
    # Relations avec l'utilisateur et la voiture concernés
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    voiture = models.ForeignKey(Voiture, on_delete=models.CASCADE)
    
    date_transaction = models.DateTimeField(auto_now_add=True)  # Date de la transaction
    type_transaction = models.CharField(max_length=10, choices=TYPE_TRANSACTION)  # Type (achat ou location)
    montant = models.DecimalField(max_digits=10, decimal_places=2)  # Montant de la transaction
    
    # Champs spécifiques pour la location
    date_debut_location = models.DateField(null=True, blank=True)  # Date de début (pour location)
    date_fin_location = models.DateField(null=True, blank=True)  # Date de fin (pour location)
    
    def __str__(self):
        """Représentation textuelle de la transaction"""
        return f"{self.type_transaction} de {self.voiture} par {self.utilisateur}"