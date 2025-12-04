from django.db import models
from django.contrib.auth import get_user_model
from usuarios.models import Cliente
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

class ConfiguracaoFatura(models.Model):
    """Configuração de vencimento de faturas do cliente"""
    DIA_VENCIMENTO_CHOICES = [(i, str(i)) for i in range(1, 29)]  # Dias 1 a 28
    
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='config_fatura')
    dia_vencimento = models.IntegerField(choices=DIA_VENCIMENTO_CHOICES, default=10)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Configuração de Fatura'
        verbose_name_plural = 'Configurações de Faturas'
    
    def __str__(self):
        return f"{self.cliente.usuario.first_name} - Vencimento dia {self.dia_vencimento}"

class Fatura(models.Model):
    """Modelo para faturas mensais dos clientes"""
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('fechada', 'Fechada'),
        ('paga', 'Paga'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='faturas')
    mes_referencia = models.DateField()  # Primeiro dia do mês de referência
    data_vencimento = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='aberta')
    data_pagamento = models.DateTimeField(null=True, blank=True)
    juros_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        unique_together = ['cliente', 'mes_referencia']
        ordering = ['-mes_referencia']
    
    def __str__(self):
        return f"Fatura {self.cliente.usuario.first_name} - {self.mes_referencia.strftime('%m/%Y')}"
    
    @property
    def valor_restante(self):
        return self.valor_total - self.valor_pago
    
    @property
    def esta_vencida(self):
        return date.today() > self.data_vencimento and self.status != 'paga'
    
    def calcular_juros_mora(self):
        """Calcula juros de mora se a fatura estiver vencida"""
        if self.esta_vencida and self.valor_restante > 0:
            dias_atraso = (date.today() - self.data_vencimento).days
            # 2% ao mês + 0.5% por dia de atraso (máximo 20%)
            taxa_juros = min(0.02 + (dias_atraso * 0.005), 0.20)
            self.juros_mora = self.valor_restante * Decimal(str(taxa_juros))
            if self.status == 'fechada':
                self.status = 'vencida'
            self.save()

class ItemFatura(models.Model):
    """Modelo para itens de uma fatura"""
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='itens')
    compra = models.ForeignKey('loja.Compra', on_delete=models.CASCADE)
    parcela_numero = models.IntegerField(default=1)  # Número da parcela (1, 2, 3...)
    parcela_total = models.IntegerField(default=1)   # Total de parcelas
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=200)
    data_inclusao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item da Fatura'
        verbose_name_plural = 'Itens da Fatura'
    
    def __str__(self):
        if self.parcela_total > 1:
            return f"{self.descricao} - {self.parcela_numero}/{self.parcela_total}"
        return self.descricao

class PagamentoFatura(models.Model):
    """Modelo para registrar pagamentos de faturas"""
    FORMA_PAGAMENTO_CHOICES = [
        ('saldo', 'Saldo'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
    ]
    
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='pagamentos')
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=15, choices=FORMA_PAGAMENTO_CHOICES)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Pagamento de Fatura'
        verbose_name_plural = 'Pagamentos de Faturas'
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f"Pagamento R$ {self.valor_pago} - Fatura {self.fatura.id}"

# Função utilitária para criar faturas mensais
def criar_fatura_mensal(cliente, mes_referencia=None):
    """Cria uma nova fatura mensal para o cliente"""
    if not mes_referencia:
        mes_referencia = date.today().replace(day=1)
    
    # Verificar se já existe fatura para este mês
    if Fatura.objects.filter(cliente=cliente, mes_referencia=mes_referencia).exists():
        return None
    
    # Buscar configuração de vencimento
    try:
        config = cliente.config_fatura
        dia_vencimento = config.dia_vencimento
    except:
        dia_vencimento = 10  # Padrão
    
    # Calcular data de vencimento (próximo mês)
    if mes_referencia.month == 12:
        data_vencimento = date(mes_referencia.year + 1, 1, dia_vencimento)
    else:
        data_vencimento = date(mes_referencia.year, mes_referencia.month + 1, dia_vencimento)
    
    # Criar fatura
    fatura = Fatura.objects.create(
        cliente=cliente,
        mes_referencia=mes_referencia,
        data_vencimento=data_vencimento
    )
    
    return fatura

def processar_compra_parcelada(compra, parcelas):
    """Processa uma compra parcelada criando itens nas faturas futuras"""
    if parcelas <= 1:
        return
    
    valor_parcela = compra.valor_total / parcelas
    cliente = compra.cliente
    
    # Criar ou buscar fatura do mês atual
    mes_atual = date.today().replace(day=1)
    
    for i in range(parcelas):
        # Calcular mês da parcela
        mes_parcela = mes_atual
        if i > 0:
            if mes_atual.month + i > 12:
                ano = mes_atual.year + ((mes_atual.month + i - 1) // 12)
                mes = ((mes_atual.month + i - 1) % 12) + 1
                mes_parcela = date(ano, mes, 1)
            else:
                mes_parcela = mes_atual.replace(month=mes_atual.month + i)
        
        # Criar ou buscar fatura
        fatura = Fatura.objects.filter(cliente=cliente, mes_referencia=mes_parcela).first()
        if not fatura:
            fatura = criar_fatura_mensal(cliente, mes_parcela)
        
        # Criar item da fatura
        ItemFatura.objects.create(
            fatura=fatura,
            compra=compra,
            parcela_numero=i + 1,
            parcela_total=parcelas,
            valor_parcela=valor_parcela,
            descricao=f"Compra #{compra.id} - Parcela {i + 1}/{parcelas}"
        )
        
        # Atualizar valor total da fatura
        fatura.valor_total += valor_parcela
        fatura.save()
