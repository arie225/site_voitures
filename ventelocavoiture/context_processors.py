# Ce module définit des fonctions qui ajoutent des variables au contexte de tous les templates
from .models import Utilisateur

def utilisateur_connecte(request):
    """
    Processeur de contexte qui ajoute des informations sur l'utilisateur connecté
    à tous les templates.
    
    Args:
        request: L'objet HttpRequest en cours de traitement
        
    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur pour le template
    """
    context = {
        'utilisateur_connecte': False,  # Par défaut, l'utilisateur n'est pas connecté
        'utilisateur': None
    }
    
    # Vérifie si l'ID utilisateur est présent dans la session
    if 'utilisateur_id' in request.session:
        try:
            # Tente de récupérer l'utilisateur correspondant à l'ID
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            context['utilisateur_connecte'] = True
            context['utilisateur'] = utilisateur
        except Utilisateur.DoesNotExist:
            # Si l'utilisateur n'existe pas, on garde les valeurs par défaut
            pass
            
    return context