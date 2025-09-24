from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cliente, Gerente, Atendente

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario', 'telefone')}),
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cpf', 'score_pontos', 'data_cadastro')
    list_filter = ('data_cadastro',)
    search_fields = ('usuario__first_name', 'usuario__last_name', 'cpf')
    readonly_fields = ('data_cadastro',)

@admin.register(Gerente)
class GerenteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'codigo_gerente', 'data_admissao', 'ativo')
    list_filter = ('ativo', 'data_admissao')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'codigo_gerente')

@admin.register(Atendente)
class AtendenteAdmin(admin.ModelAdmin):
    list_display = ('nome_bot', 'versao', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'versao', 'data_criacao')
    search_fields = ('nome_bot', 'versao')
    readonly_fields = ('data_criacao',)
