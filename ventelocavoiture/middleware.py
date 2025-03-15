# Créez un nouveau fichier middleware.py dans votre application
class SessionUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exécuté avant la vue
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # Si la réponse a un contexte, ajoutez les informations de l'utilisateur
        if hasattr(response, 'context_data'):
            if 'utilisateur_id' in request.session:
                response.context_data['utilisateur_connecte'] = True
            else:
                response.context_data['utilisateur_connecte'] = False
        return response