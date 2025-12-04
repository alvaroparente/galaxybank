from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    """Modelo base para todos os tipos de usuário"""
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('gerente', 'Gerente'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente'
    )
    telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"

class Cliente(models.Model):
    """Modelo específico para clientes"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r'^\d{11}$', message='CPF deve conter 11 dígitos')]
    )
    score_pontos = models.IntegerField(default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    limite_credito_aprovado = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - CPF: {self.cpf}"

class Gerente(models.Model):
    """Modelo específico para gerentes"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    codigo_gerente = models.CharField(max_length=10, unique=True)
    data_admissao = models.DateField()
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
    
    def __str__(self):
        return f"Gerente {self.usuario.first_name} {self.usuario.last_name} - {self.codigo_gerente}"

class Transacao(models.Model):
    """Modelo para registrar transações dos clientes"""
    TIPO_TRANSACAO_CHOICES = [
        ('deposito', 'Depósito'),
        ('transferencia_enviada', 'Transferência Enviada'),
        ('transferencia_recebida', 'Transferência Recebida'),
        ('compra', 'Compra'),
        ('pagamento_fatura', 'Pagamento de Fatura'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='transacoes_origem')
    tipo = models.CharField(max_length=25, choices=TIPO_TRANSACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    data_transacao = models.DateTimeField(auto_now_add=True)
    
    # Para transferências
    destinatario = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes_recebidas')
    origem = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes_como_origem')
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data_transacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} - {self.cliente.usuario.first_name}"
    
    @property
    def eh_entrada(self):
        """Retorna True se a transação representa entrada de dinheiro"""
        return self.tipo in ['deposito', 'transferencia_recebida']
    
    @property
    def eh_saida(self):
        """Retorna True se a transação representa saída de dinheiro"""
        return self.tipo in ['transferencia_enviada', 'compra', 'pagamento_fatura']
