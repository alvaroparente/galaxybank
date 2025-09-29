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
