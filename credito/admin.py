from django.contrib import admin
from .models import SolicitacaoCredito, HistoricoCredito

@admin.register(SolicitacaoCredito)
class SolicitacaoCreditoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'valor_solicitado', 'status', 'data_solicitacao', 'gerente_responsavel']
    list_filter = ['status', 'data_solicitacao']
    search_fields = ['cliente__usuario__first_name', 'cliente__usuario__last_name']
    readonly_fields = ['data_solicitacao']

@admin.register(HistoricoCredito)
class HistoricoCreditoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_operacao', 'valor', 'data_operacao']
    list_filter = ['tipo_operacao', 'data_operacao']
    readonly_fields = ['data_operacao']
