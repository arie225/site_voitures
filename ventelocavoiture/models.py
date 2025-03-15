from django.db import models
from django.core.validators import MinValueValidator

class Voiture(models.Model):
    ETAT_CHOIX = [
        ('disponible', 'Disponible'),
        ('vendu', 'Vendu'),
        ('loué', 'Loué'),
    ]
    
    TYPE_CHOIX = [
        ('vente', 'À vendre'),
        ('location', 'À louer'),
        ('les_deux', 'À vendre et à louer'),
    ]
    
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    kilometrage = models.IntegerField()
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_location_jour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    etat = models.CharField(max_length=20, choices=ETAT_CHOIX, default='disponible')
    type_offre = models.CharField(max_length=20, choices=TYPE_CHOIX, default='vente')
    date_ajout = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/')  # Image principale
    
    def __str__(self):
        return f"{self.marque} {self.modele}"

class ImageVoiture(models.Model):
    voiture = models.ForeignKey(Voiture, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return f"Image de {self.voiture}"
    
    
class Utilisateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('F', 'Feminin'), ('M', 'Masculin')])
    numeros = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.nom} {self.prenom}"
    


class Transaction(models.Model):
    TYPE_TRANSACTION = [
        ('achat', 'Achat'),
        ('location', 'Location'),
    ]
    
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    voiture = models.ForeignKey(Voiture, on_delete=models.CASCADE)
    date_transaction = models.DateTimeField(auto_now_add=True)
    type_transaction = models.CharField(max_length=10, choices=TYPE_TRANSACTION)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut_location = models.DateField(null=True, blank=True)
    date_fin_location = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.type_transaction} de {self.voiture} par {self.utilisateur}"