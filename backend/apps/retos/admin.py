from django import forms
from django.contrib import admin

from .models import (
    Categoria,
    Intento,
    MovimientoCubo,
    MovimientoReto,
    Pista,
    PistaDesbloqueada,
    PreguntaMascota,
    ProgresoCubo,
    Reto,
    RetoResuelto,
)


class FormularioReto(forms.ModelForm):
    """Permite escribir la flag en claro; se guarda hasheada."""

    flag = forms.CharField(
        required=False,
        label="flag (texto plano)",
        help_text="Se almacena hasheada con pepper. Dejar vacio para no cambiarla.",
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = Reto
        fields = "__all__"

    def save(self, commit=True):
        reto = super().save(commit=False)
        flag_en_claro = self.cleaned_data.get("flag")
        if flag_en_claro:
            reto.establecer_flag(flag_en_claro)
        if commit:
            reto.save()
            self.save_m2m()
        return reto


@admin.register(Categoria)
class AdminCategoria(admin.ModelAdmin):
    list_display = ("nombre", "slug", "color", "orden", "activa")
    list_editable = ("color", "orden", "activa")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(MovimientoCubo)
class AdminMovimientoCubo(admin.ModelAdmin):
    list_display = ("notacion", "descripcion", "orden")
    list_editable = ("orden",)
    search_fields = ("notacion", "descripcion")


class InlineMovimientoReto(admin.TabularInline):
    model = MovimientoReto
    extra = 1
    autocomplete_fields = ("movimiento",)


class InlinePista(admin.TabularInline):
    model = Pista
    extra = 1


@admin.register(Reto)
class AdminReto(admin.ModelAdmin):
    form = FormularioReto
    list_display = ("nombre", "categoria", "dificultad", "puntos", "activo", "tiene_flag")
    list_filter = ("categoria", "dificultad", "activo")
    search_fields = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = (InlineMovimientoReto, InlinePista)
    readonly_fields = ("hash_flag", "creado_en", "actualizado_en")
    fieldsets = (
        (None, {"fields": ("nombre", "slug", "descripcion", "categoria")}),
        ("Puntuacion", {"fields": ("dificultad", "puntos", "activo")}),
        ("Flag", {"fields": ("flag", "hash_flag")}),
        ("Fechas", {"fields": ("creado_en", "actualizado_en"), "classes": ("collapse",)}),
    )

    @admin.display(boolean=True, description="flag")
    def tiene_flag(self, obj) -> bool:
        return bool(obj.hash_flag)


@admin.register(Intento)
class AdminIntento(admin.ModelAdmin):
    list_display = ("usuario", "reto", "es_correcto", "creado_en")
    list_filter = ("es_correcto",)
    search_fields = ("usuario__username", "reto__slug")
    readonly_fields = ("usuario", "reto", "hash_enviado", "es_correcto", "creado_en")


@admin.register(RetoResuelto)
class AdminRetoResuelto(admin.ModelAdmin):
    list_display = ("usuario", "reto", "puntos_otorgados", "resuelto_en")
    search_fields = ("usuario__username", "reto__slug")
    readonly_fields = ("resuelto_en",)


@admin.register(ProgresoCubo)
class AdminProgresoCubo(admin.ModelAdmin):
    list_display = ("usuario", "cantidad_movimientos", "actualizado_en")
    readonly_fields = ("movimientos_aplicados", "actualizado_en")

    @admin.display(description="movimientos")
    def cantidad_movimientos(self, obj) -> int:
        return len(obj.movimientos_aplicados or [])


@admin.register(Pista)
class AdminPista(admin.ModelAdmin):
    list_display = ("reto", "orden", "coste", "activa")
    list_filter = ("activa",)
    search_fields = ("reto__slug", "texto")


@admin.register(PreguntaMascota)
class AdminPreguntaMascota(admin.ModelAdmin):
    list_display = ("texto", "tema", "pista", "activa")
    list_filter = ("tema", "activa")
    search_fields = ("texto", "respuesta")


@admin.register(PistaDesbloqueada)
class AdminPistaDesbloqueada(admin.ModelAdmin):
    list_display = ("usuario", "pista", "desbloqueada_en")
    search_fields = ("usuario__username",)
