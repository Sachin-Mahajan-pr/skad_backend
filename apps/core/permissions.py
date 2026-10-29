from rest_framework import permissions

ROLE_SUPERADMIN = "Superadmin / Developer"
ROLE_APPROVER = "Approver (legal / lead)"
ROLE_EDITOR = "Editor"
ROLE_BRAND_OWNER = "Brand / company owner"
ROLE_HR = "HR"
ROLE_ENQUIRY_HANDLER = "Enquiry handler"
ROLE_MEDIA = "Media"
ROLE_AUDITOR = "Read-only / auditor"

ALL_ROLES = [
    ROLE_SUPERADMIN,
    ROLE_APPROVER,
    ROLE_EDITOR,
    ROLE_BRAND_OWNER,
    ROLE_HR,
    ROLE_ENQUIRY_HANDLER,
    ROLE_MEDIA,
    ROLE_AUDITOR,
]

def user_has_role(user, role_name: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    # Match exact or primary keyword (e.g. "Approver" matches "Approver (team lead / legal liaison)")
    first_word = role_name.split()[0]
    return user.groups.filter(name=role_name).exists() or user.groups.filter(name__iexact=first_word).exists()


class IsApproverOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for all, but require Approver or Superuser for edits/publishes.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return user_has_role(request.user, ROLE_APPROVER) or user_has_role(request.user, ROLE_SUPERADMIN)

class IsHROrAdmin(permissions.BasePermission):
    """
    Allow access to job applications and resumes only to HR staff or Superadmins.
    """
    def has_permission(self, request, view):
        return user_has_role(request.user, ROLE_HR) or user_has_role(request.user, ROLE_SUPERADMIN)

class IsEnquiryHandlerOrAdmin(permissions.BasePermission):
    """
    Allow access to enquiries only to assigned handlers or Superadmins.
    """
    def has_permission(self, request, view):
        return user_has_role(request.user, ROLE_ENQUIRY_HANDLER) or user_has_role(request.user, ROLE_SUPERADMIN)
