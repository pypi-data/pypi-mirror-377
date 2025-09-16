import inspect
from Ketzal.src.routing.Router import Router
from Ketzal.src.http.HttpMethod import HttpMethod

class RequestHandler:
    """Handles the processing of HTTP client requests."""

    def handle_client_request(self, client_socket):
        """
        Handles a full client request lifecycle.

        Args:
            client_socket (socket): The connected client socket.

        Returns:
            dict: A dictionary with information for logging (e.g., request line).
        """
        try:
            request = self._receive_request(client_socket)
            if not request:
                return {"request_line": None}  # Always return dict for logging

            method, path = self._parse_request(request)
            if not method or not path:
                self._send_bad_request(client_socket)
                return {"request_line": request.splitlines()[0]}  # For logging

            response = self._process_request(method, path)
            self._send_response(client_socket, response)

            return {"request_line": request.splitlines()[0]}

        except Exception as e:
            return {"request_line": f"ERROR: {e}"}

        finally:
            client_socket.close()

    def _receive_request(self, client_socket):
        """
        Receive and decode the client request.

        Args:
            client_socket (socket): The connected client socket.

        Returns:
            str | None: Decoded request string, or None if empty/failed.
        """
        try:
            request = client_socket.recv(1024).decode("utf-8")
            return request if request else None
        except Exception:
            return None

    def _parse_request(self, request):
        """
        Parse HTTP method and path from the raw request.

        Args:
            request (str): Full raw HTTP request string.

        Returns:
            tuple(HttpMethod | None, str | None): Parsed method and path.
        """
        try:
            first_line = request.split("\r\n")[0]
            method_str, path, _ = first_line.split()

            if method_str not in [m.value for m in HttpMethod]:
                print(f"❌ Unsupported HTTP method: {method_str}")
                return None, None

            method = HttpMethod(method_str)
            path = self._normalize_path(path)
            return method, path
        except Exception as e:
            print(f"❌ Error parsing request: {e}")
            return None, None

    def _normalize_path(self, path):
        """
        Normalize request path (leading/trailing slashes).

        Args:
            path (str): Raw path from request.

        Returns:
            str: Normalized path.
        """
        if not path.startswith("/"):
            path = "/" + path
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        return path

    def _process_request(self, method, path):
        """
        Process the request by resolving the route and executing its handler.

        Args:
            method (HttpMethod): Parsed HTTP method.
            path (str): Normalized request path.

        Returns:
            str: HTTP response string.
        """
        route, params = Router.resolve(method, path)

        if not route:
            return self._create_404_response()

        try:
            response_data = self._execute_handler(route.handler, params)
            return self._create_success_response(response_data)
        except Exception as e:
            return self._create_error_response(e)

    def _execute_handler(self, handler, params):
        """
        Execute the appropriate route handler.

        Args:
            handler (callable | tuple): Route handler definition.
            params (dict): Path parameters.

        Returns:
            Any: Result of handler execution.
        """
        if callable(handler):
            return self._execute_callable_handler(handler, params)
        elif isinstance(handler, (list, tuple)) and len(handler) == 2:
            return self._execute_controller_handler(handler, params)
        else:
            return "Handler error"

    def _execute_callable_handler(self, handler, params):
        """
        Execute a callable handler (function or lambda).

        Args:
            handler (callable): Function to execute.
            params (dict): Path parameters.

        Returns:
            Any: Handler result.
        """
        sig = inspect.signature(handler)
        args = self._get_handler_args(sig, params)
        return handler(*args)

    def _execute_controller_handler(self, handler, params):
        """
        Execute a controller handler defined as [ControllerClass, "method"].

        Args:
            handler (tuple): [ControllerClass, method_name].
            params (dict): Path parameters.

        Returns:
            Any: Handler result.
        """
        controller_class, func_name = handler
        controller = controller_class()
        method_obj = getattr(controller, func_name)

        sig = inspect.signature(method_obj)
        args = self._get_handler_args(sig, params)

        return method_obj(*args) if args else method_obj()

    def _get_handler_args(self, signature, params):
        """
        Extract handler arguments from parameters using its signature.

        Args:
            signature (inspect.Signature): Handler function signature.
            params (dict): Path parameters.

        Returns:
            list: Arguments to pass to handler.
        """
        arg_names = list(signature.parameters.keys())
        return [params[name] for name in arg_names if name in params]

    def _create_success_response(self, response_data):
        """
        Create an HTTP 200 success response.

        Args:
            response_data (Any): Data returned by the route handler.

        Returns:
            str: HTTP response string.
        """
        body = str(response_data)
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{body}"

    def _create_404_response(self):
        """
        Create an HTTP 404 Not Found response.

        Returns:
            str: HTTP response string.
        """
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nNot Found"

    def _create_error_response(self, error):
        """
        Create an error response when a handler fails.

        Args:
            error (Exception): The raised exception.

        Returns:
            str: HTTP response string.
        """
        body = f"Error executing handler: {error}"
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{body}"

    def _send_response(self, client_socket, response):
        """
        Send an HTTP response to the client.

        Args:
            client_socket (socket): The connected client socket.
            response (str): Full HTTP response string.
        """
        client_socket.sendall(response.encode("utf-8"))

    def _send_bad_request(self, client_socket):
        """
        Send an HTTP 400 Bad Request response.

        Args:
            client_socket (socket): The connected client socket.
        """
        response = "HTTP/1.1 400 Bad Request\r\n\r\nBad Request"
        self._send_response(client_socket, response)
