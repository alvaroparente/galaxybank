from django.db import models
from django.contrib.auth import get_user_model
from usuarios.models import Cliente
import requests
from decimal import Decimal

User = get_user_model()

class CategoriaProduto(models.Model):
    """Modelo para categorias de produtos"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoria de Produto'
        verbose_name_plural = 'Categorias de Produtos'
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    """Modelo para produtos da loja"""
    api_id = models.IntegerField(unique=True, null=True, blank=True)  # ID da API externa
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    preco_vista = models.DecimalField(max_digits=10, decimal_places=2)
    preco_prazo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE, null=True, blank=True)
    imagem_url = models.URLField(max_length=500, blank=True)
    estoque = models.IntegerField(default=100)  # Estoque fictício
    ativo = models.BooleanField(default=True)
    avaliacao = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        # Se não tem preço a prazo definido, calcula 10% de juros
        if not self.preco_prazo:
            self.preco_prazo = self.preco_vista * Decimal('1.10')
        super().save(*args, **kwargs)

class Compra(models.Model):
    """Modelo para compras realizadas pelos clientes"""
    FORMA_PAGAMENTO_CHOICES = [
        ('saldo', 'Saldo'),
        ('credito', 'Crédito'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('cancelada', 'Cancelada'),
        ('entregue', 'Entregue'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='compras')
    data_compra = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=10, choices=FORMA_PAGAMENTO_CHOICES)
    parcelas = models.IntegerField(default=1)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='aprovada')
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-data_compra']
    
    def __str__(self):
        return f"Compra {self.id} - {self.cliente.usuario.first_name} - R$ {self.valor_total}"

class ItemCompra(models.Model):
    """Modelo para itens de uma compra"""
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item da Compra'
        verbose_name_plural = 'Itens da Compra'
    
    def __str__(self):
        return f"{self.produto.titulo} - Qtd: {self.quantidade}"
    
    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)

class CarrinhoCompras(models.Model):
    """Modelo para carrinho de compras temporário"""
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrinho de Compras'
        verbose_name_plural = 'Carrinhos de Compras'
    
    def __str__(self):
        return f"Carrinho - {self.cliente.usuario.first_name}"
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.itens.all())
    
    def get_quantidade_total(self):
        return sum(item.quantidade for item in self.itens.all())

class ItemCarrinho(models.Model):
    """Modelo para itens no carrinho de compras"""
    carrinho = models.ForeignKey(CarrinhoCompras, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    data_adicionado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['carrinho', 'produto']
    
    def __str__(self):
        return f"{self.produto.titulo} - Qtd: {self.quantidade}"
    
    def get_subtotal(self):
        return self.quantidade * self.produto.preco_vista

# Função utilitária para sincronizar produtos da API
def sincronizar_produtos_api():
    """Sincroniza produtos da FakeStore API"""
    try:
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            produtos_api = response.json()
            
            for produto_data in produtos_api:
                # Criar ou buscar categoria
                categoria_nome = produto_data['category'].title()
                categoria, _ = CategoriaProduto.objects.get_or_create(
                    nome=categoria_nome,
                    defaults={'descricao': f'Categoria {categoria_nome}'}
                )
                
                # Criar ou atualizar produto
                produto, created = Produto.objects.get_or_create(
                    api_id=produto_data['id'],
                    defaults={
                        'titulo': produto_data['title'],
                        'descricao': produto_data['description'],
                        'preco_vista': Decimal(str(produto_data['price'])),
                        'categoria': categoria,
                        'imagem_url': produto_data['image'],
                        'avaliacao': Decimal(str(produto_data['rating']['rate'])),
                    }
                )
                
                if not created:
                    # Atualizar produto existente
                    produto.titulo = produto_data['title']
                    produto.descricao = produto_data['description']
                    produto.preco_vista = Decimal(str(produto_data['price']))
                    produto.imagem_url = produto_data['image']
                    produto.avaliacao = Decimal(str(produto_data['rating']['rate']))
                    produto.save()
            
            return True
    except Exception as e:
        print(f"Erro ao sincronizar produtos: {e}")
        return False
