from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminDjango

from .models import Usuario


@admin.register(Usuario)
class AdminUsuario(UserAdminDjango):
    list_display = ("username", "email", "nombre_visible", "puntuacion", "is_staff")
    ordering = ("-puntuacion", "username")
    fieldsets = UserAdminDjango.fieldsets + (
        ("RUBIK CTF", {"fields": ("nombre_visible", "puntuacion")}),
    )
    add_fieldsets = UserAdminDjango.add_fieldsets + (
        ("RUBIK CTF", {"fields": ("email", "nombre_visible")}),
    )
