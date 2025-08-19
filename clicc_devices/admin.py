from django.contrib import admin
from .models import Set, ItemType


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("alma_set_id", "name", "unit", "type")
    search_fields = ("alma_set_id", "name", "unit")
    list_filter = ("type", "unit")


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
