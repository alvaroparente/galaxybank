from django.contrib import admin
from .models import ConfiguracaoFatura, Fatura, ItemFatura, PagamentoFatura

@admin.register(ConfiguracaoFatura)
class ConfiguracaoFaturaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'dia_vencimento', 'ativo']
    list_filter = ['dia_vencimento', 'ativo']

@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'mes_referencia', 'data_vencimento', 'valor_total', 'status']
    list_filter = ['status', 'mes_referencia']
    readonly_fields = ['data_criacao', 'data_atualizacao']

@admin.register(ItemFatura)
class ItemFaturaAdmin(admin.ModelAdmin):
    list_display = ['fatura', 'compra', 'parcela_numero', 'parcela_total', 'valor_parcela']

@admin.register(PagamentoFatura)
class PagamentoFaturaAdmin(admin.ModelAdmin):
    list_display = ['fatura', 'valor_pago', 'forma_pagamento', 'data_pagamento']
    list_filter = ['forma_pagamento', 'data_pagamento']
    readonly_fields = ['data_pagamento']
