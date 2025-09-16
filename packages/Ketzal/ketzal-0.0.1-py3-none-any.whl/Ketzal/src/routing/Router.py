from Ketzal.src.http.HttpMethod import HttpMethod
from Ketzal.src.routing.RouteDefinition import RouteDefinition

class Router:
    # Inicializar el diccionario correctamente
    routes = {}
    
    @staticmethod
    def _ensure_routes_initialized():
        """Ensures the routes dictionary is initialized"""
        if not Router.routes:
            Router.routes = {
                HttpMethod.GET: [],
                HttpMethod.POST: [],
                HttpMethod.PUT: [],
                HttpMethod.DELETE: []
            }

    @staticmethod
    def add_route(method, path, handler):
        """Adds a new route to the router"""
        Router._ensure_routes_initialized()
        
        route = RouteDefinition(method, path, handler)
        
        # Verify the method exists in the dictionary
        if method not in Router.routes:
            Router.routes[method] = []
            
        Router.routes[method].append(route)
        return route

    @staticmethod
    def get(path, handler):
        """Registers a GET route"""
        return Router.add_route(HttpMethod.GET, path, handler)

    @staticmethod
    def post(path, handler):
        """Registers a POST route"""
        return Router.add_route(HttpMethod.POST, path, handler)
        
    @staticmethod
    def put(path, handler):
        """Registers a PUT route"""
        return Router.add_route(HttpMethod.PUT, path, handler)
        
    @staticmethod
    def delete(path, handler):
        """Registers a DELETE route"""
        return Router.add_route(HttpMethod.DELETE, path, handler)

    @staticmethod
    def resolve(method, path):
        """Resolves a route based on the HTTP method and path"""
        Router._ensure_routes_initialized()
        
        if method not in Router.routes:
            return None, {}
            
        for route in Router.routes[method]:
            match = route.regex.match(path)
            if match:
                params = dict(zip(route.param_names, match.groups()))
                return route, params
                
        return None, {}
    
    @staticmethod
    def clear_routes():
        """Clears all registered routes"""
        Router.routes.clear()
        Router._ensure_routes_initialized()