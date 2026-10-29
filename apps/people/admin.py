from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Person, PersonRole

class PersonRoleInline(admin.TabularInline):
    model = PersonRole
    extra = 1

@admin.register(Person)
class PersonAdmin(SimpleHistoryAdmin):
    list_display = ("name", "title", "group", "consent_recorded", "status", "verified", "sort_order", "updated_at")
    list_filter = ("group", "consent_recorded", "status", "verified")
    search_fields = ("name", "title", "bio")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PersonRoleInline]

@admin.register(PersonRole)
class PersonRoleAdmin(admin.ModelAdmin):
    list_display = ("person", "role_title", "company", "brand", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("person__name", "role_title")
