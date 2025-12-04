from django.urls import path
from . import views

app_name = 'credito'

urlpatterns = [
    # URLs do Cliente
    path('solicitar/', views.solicitar_credito, name='solicitar'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path('historico/', views.historico_credito, name='historico'),
    
    # URLs do Gerente
    path('avaliar/', views.avaliar_solicitacoes, name='avaliar_solicitacoes'),
    path('solicitacao/<int:solicitacao_id>/', views.detalhes_solicitacao, name='detalhes_solicitacao'),
    path('processar/<int:solicitacao_id>/', views.processar_solicitacao, name='processar_solicitacao'),
    path('avaliadas/', views.solicitacoes_avaliadas, name='solicitacoes_avaliadas'),
]