from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Partner

@admin.register(Partner)
class PartnerAdmin(SimpleHistoryAdmin):
    list_display = ("name", "partner_type", "website_url", "status", "verified", "sort_order")
    list_filter = ("partner_type", "status", "verified")
    search_fields = ("name", "relationship_description")
