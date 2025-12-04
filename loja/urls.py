from django.urls import path
from . import views

app_name = 'loja'

urlpatterns = [
    path('', views.loja_home, name='home'),
    path('produtos/', views.lista_produtos, name='produtos'),
    path('produto/<int:produto_id>/', views.detalhes_produto, name='produto_detalhes'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('adicionar-carrinho/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('compras/', views.compras, name='compras'),
]