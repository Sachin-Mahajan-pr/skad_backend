class AdminContentSecurityPolicyMiddleware:
    """
    Enforces Content Security Policy on the Django Admin interface
    per Page 19 of SKAD Backend Specification ('CSP on admin').
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            csp_policy = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "script-src 'self' 'unsafe-inline'; "
                "frame-ancestors 'none'; "
                "form-action 'self';"
            )
            response.headers["Content-Security-Policy"] = csp_policy
        return response

