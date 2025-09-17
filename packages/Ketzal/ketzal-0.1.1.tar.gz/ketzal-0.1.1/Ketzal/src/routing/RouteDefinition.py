import re

class RouteDefinition:
    def __init__(self, method, path, handler):
        """
        Initializes a new RouteDefinition object.

        Args:
            method (HttpMethod): The HTTP method for the route.
            path (str): The path for the route.
            handler (callable): The handler function for the route.

        Attributes:
            method (HttpMethod): The HTTP method for the route.
            path (str): The path for the route.
            handler (callable): The handler function for the route.
            route_name (str): The name of the route.
            param_names (list): A list of parameter names extracted from the path.
            regex (re.Pattern): A regular expression pattern for the path.
        """
        self.method = method
        self.path = path 
        self.handler = handler
        self.route_name = None
        self.param_names = re.findall(r"{(\w+)}", path)
        pattern = re.sub(r"{\w+}", r"([^/]+)", path)
        self.regex = re.compile(f"^{pattern}$")

    def name(self, route_name: str):
        self.route_name = route_name
        return self 
        
    def __str__(self):
        return f"Route({self.method.value} {self.path})"
        
    def __repr__(self):
        return self.__str__()