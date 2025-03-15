from django.contrib import admin
from .models import Voiture
from .models import ImageVoiture
from .models import Utilisateur
from .models import Transaction


# Enregistrez votre modèle pour qu'il apparaisse dans l'admin
admin.site.register(Voiture)
admin.site.register(ImageVoiture)
admin.site.register(Utilisateur)
admin.site.register(Transaction)


# Register your models here.
