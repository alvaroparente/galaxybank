from django.db import models
from django.contrib.auth import get_user_model
from usuarios.models import Cliente, Gerente

User = get_user_model()

class SolicitacaoCredito(models.Model):
    """Modelo para solicitações de crédito dos clientes"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('reprovada', 'Reprovada'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitacoes_credito')
    valor_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
    justificativa = models.TextField()
    renda_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    profissao = models.CharField(max_length=100, default='Não informado')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    
    # Campos para aprovação/reprovação
    gerente_responsavel = models.ForeignKey(Gerente, on_delete=models.SET_NULL, null=True, blank=True, related_name='avaliacoes_credito')
    data_avaliacao = models.DateTimeField(null=True, blank=True)
    observacoes_gerente = models.TextField(blank=True)
    valor_aprovado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Solicitação de Crédito'
        verbose_name_plural = 'Solicitações de Crédito'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação {self.id} - {self.cliente.usuario.first_name} - R$ {self.valor_solicitado}"

class HistoricoCredito(models.Model):
    """Modelo para histórico de uso do crédito"""
    TIPO_OPERACAO_CHOICES = [
        ('utilizacao', 'Utilização'),
        ('pagamento', 'Pagamento'),
        ('ajuste', 'Ajuste'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='historico_credito')
    tipo_operacao = models.CharField(max_length=15, choices=TIPO_OPERACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_posterior = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=200)
    data_operacao = models.DateTimeField(auto_now_add=True)
    compra_relacionada = models.ForeignKey('loja.Compra', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Histórico de Crédito'
        verbose_name_plural = 'Histórico de Crédito'
        ordering = ['-data_operacao']
    
    def __str__(self):
        return f"{self.cliente.usuario.first_name} - {self.tipo_operacao} - R$ {self.valor}"
