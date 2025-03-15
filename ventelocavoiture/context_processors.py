# Dans context_processors.py
from .models import Utilisateur

def utilisateur_connecte(request):
    context = {
        'utilisateur_connecte': False,
        'utilisateur': None
    }
    
    if 'utilisateur_id' in request.session:
        try:
            utilisateur = Utilisateur.objects.get(id=request.session['utilisateur_id'])
            context['utilisateur_connecte'] = True
            context['utilisateur'] = utilisateur
        except Utilisateur.DoesNotExist:
            pass
            
    return context