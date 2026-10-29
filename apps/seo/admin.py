from django.contrib import admin
from .models import Redirect, SeoGlobalSettings

@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "permanent", "created_at")
    list_filter = ("permanent",)
    search_fields = ("old_path", "new_path")

@admin.register(SeoGlobalSettings)
class SeoGlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ("default_meta_title", "schema_organization_name")
