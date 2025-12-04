from django.contrib import admin
from .models import CategoriaProduto, Produto, Compra, ItemCompra, CarrinhoCompras, ItemCarrinho

@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'preco_vista', 'preco_prazo', 'estoque', 'ativo']
    list_filter = ['categoria', 'ativo']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['api_id']

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data_compra', 'valor_total', 'forma_pagamento', 'status']
    list_filter = ['forma_pagamento', 'status', 'data_compra']
    readonly_fields = ['data_compra']

@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ['compra', 'produto', 'quantidade', 'preco_unitario', 'valor_total']
