from django.contrib import admin

from .models import Categoria, Conta, Transacao


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "saldo_inicial", "usuario"]
    list_filter = ["tipo"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "usuario"]
    list_filter = ["tipo"]


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ["data", "descricao", "valor", "tipo", "categoria", "conta"]
    list_filter = ["tipo", "categoria"]
    search_fields = ["descricao"]
    date_hierarchy = "data"