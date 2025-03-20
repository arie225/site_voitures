# Ce middleware ajoute des informations sur l'utilisateur connecté au contexte des templates
class SessionUserMiddleware:
    """
    Middleware qui ajoute des informations sur l'utilisateur au contexte de réponse.
    Alternative au context processor, utilisable lorsque le middleware est plus approprié.
    """
    def __init__(self, get_response):
        """
        Initialise le middleware avec la fonction get_response qui représente
        le prochain middleware dans la chaîne ou la vue à appeler.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Méthode appelée pour chaque requête avant d'atteindre la vue.
        
        Args:
            request: L'objet HttpRequest en cours de traitement
            
        Returns:
            HttpResponse: La réponse renvoyée par la vue ou le middleware suivant
        """
        # Exécuté avant la vue
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        """
        Méthode appelée après l'exécution de la vue si celle-ci renvoie un objet
        qui possède un attribut 'context_data' (généralement TemplateResponse).
        
        Args:
            request: L'objet HttpRequest en cours de traitement
            response: L'objet de réponse qui contient un contexte de template
            
        Returns:
            response: L'objet de réponse modifié
        """
        # Si la réponse a un contexte, ajoutez les informations de l'utilisateur
        if hasattr(response, 'context_data'):
            if 'utilisateur_id' in request.session:
                response.context_data['utilisateur_connecte'] = True
            else:
                response.context_data['utilisateur_connecte'] = False
        return response