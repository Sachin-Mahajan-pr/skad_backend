from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import FoundationInitiative

@admin.register(FoundationInitiative)
class FoundationInitiativeAdmin(SimpleHistoryAdmin):
    list_display = ("title", "focus_area", "status_label", "status", "verified", "date")
    list_filter = ("focus_area", "status", "verified")
    search_fields = ("title", "verified_impact_details")
    prepopulated_fields = {"slug": ("title",)}
