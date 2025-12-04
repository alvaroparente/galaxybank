from django.urls import path
from . import views

app_name = 'faturas'

urlpatterns = [
    path('', views.minhas_faturas, name='minhas_faturas'),
    path('fatura/<int:fatura_id>/', views.detalhes_fatura, name='detalhes_fatura'),
    path('pagar/<int:fatura_id>/', views.pagar_fatura, name='pagar_fatura'),
    path('atual/', views.fatura_atual, name='fatura_atual'),
    path('fechar/<int:fatura_id>/', views.fechar_fatura, name='fechar_fatura'),
    path('pagar-fatura-completa/<int:fatura_id>/', views.pagar_fatura_completa, name='pagar_fatura_completa'),
    path('pagar-parcela/<int:pagamento_id>/', views.pagar_parcela, name='pagar_parcela'),
    path('configurar-vencimento/<int:fatura_id>/', views.configurar_vencimento, name='configurar_vencimento'),
]