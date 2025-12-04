from django.urls import path
from . import views

app_name = 'faturas'

urlpatterns = [
    path('', views.minhas_faturas, name='minhas_faturas'),
    path('fatura/<int:fatura_id>/', views.detalhes_fatura, name='detalhes_fatura'),
    path('pagar/<int:fatura_id>/', views.pagar_fatura, name='pagar_fatura'),
    path('atual/', views.fatura_atual, name='fatura_atual'),
    path('configurar-vencimento/', views.configurar_vencimento, name='configurar_vencimento'),
]