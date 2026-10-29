from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

class EnquiryIPThrottle(AnonRateThrottle):
    """
    Limits enquiry submissions per IP address (5 per hour default).
    Per page 12 & 13 of SKAD Backend Specification.
    """
    scope = "enquiry_ip"

class EnquiryEmailThrottle(SimpleRateThrottle):
    """
    Limits enquiry submissions per email address (3 per day default).
    Per page 12 & 13 of SKAD Backend Specification.
    """
    scope = "enquiry_email"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None
        email = request.data.get("email")
        if not email:
            return None
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.clean_email(email)
        }

    def clean_email(self, email: str) -> str:
        return email.strip().lower()
