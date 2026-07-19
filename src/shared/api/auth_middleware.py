class AuthMiddleware:
    pass

    # def __init__(self, app):
    #     self.app = app
    #
    # async def __call__(self, scope, receive, send):
    #     # Check if the request is for a protected route
    #     if scope["type"] == "http" and scope["path"].startswith("/protected"):
    #         # Perform authentication logic here
    #         # For example, check for a valid token in headers
    #         headers = dict(scope["headers"])
    #         token = headers.get(b"authorization")
    #
    #         if not token or not self.is_valid_token(token):
    #             # If the token is invalid or missing, return a 401 response
    #             await self.send_unauthorized_response(send)
    #             return
    #
    #     # If the request is not for a protected route or the token is valid,
    #     # continue processing
    #     await self.app(scope, receive, send)
    #
    # def is_valid_token(self, token):
    #     # Implement your token validation logic here
    #     # For example, check if the token matches a predefined value
    #     return token == b"Bearer valid_token"
    #
    # async def send_unauthorized_response(self, send):
    #     response = {
    #         "type": "http.response.start",
    #         "status": 401,
    #         "headers": [(b"content-type", b"application/json")],
    #     }
    #     await send(response)
    #     body = {"detail": "Unauthorized"}
    #     await send({"type": "http.response.body", "body": str(body).encode()})
