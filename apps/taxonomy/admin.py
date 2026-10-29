from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Industry, Capability, Market, Category, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Industry)
class IndustryAdmin(SimpleHistoryAdmin):
    list_display = ("name", "slug", "status", "verified", "sort_order", "updated_at")
    list_filter = ("status", "verified")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Capability)
class CapabilityAdmin(SimpleHistoryAdmin):
    list_display = ("name", "group", "status", "verified", "sort_order", "updated_at")
    list_filter = ("group", "status", "verified")
    search_fields = ("name", "group", "description", "proof_notes")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Market)
class MarketAdmin(SimpleHistoryAdmin):
    list_display = ("region", "country", "status", "verified", "show_cta", "updated_at")
    list_filter = ("status", "verified", "region")
    search_fields = ("region", "country", "description", "evidence_note")
    filter_horizontal = ("companies", "brands", "capabilities")
