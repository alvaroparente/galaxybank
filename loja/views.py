from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from .models import Produto, CategoriaProduto, CarrinhoCompras, ItemCarrinho, Compra, ItemCompra
from usuarios.models import Cliente
from faturas.models import processar_compra_parcelada
from decimal import Decimal
import json

@login_required
def loja_home(request):
    """Página inicial da loja"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem acessar a loja.')
        return redirect('usuarios:home_redirect')
    
    # Buscar produtos em destaque
    produtos_destaque = Produto.objects.filter(ativo=True).order_by('-avaliacao')[:8]
    categorias = CategoriaProduto.objects.filter(ativo=True)
    
    # Buscar carrinho do cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        carrinho, _ = CarrinhoCompras.objects.get_or_create(cliente=cliente)
        quantidade_carrinho = carrinho.get_quantidade_total()
    except Cliente.DoesNotExist:
        quantidade_carrinho = 0
    
    context = {
        'produtos_destaque': produtos_destaque,
        'categorias': categorias,
        'quantidade_carrinho': quantidade_carrinho,
    }
    
    return render(request, 'loja/home.html', context)

@login_required
def lista_produtos(request):
    """Lista todos os produtos com filtros e paginação"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem acessar a loja.')
        return redirect('usuarios:home_redirect')
    
    produtos = Produto.objects.filter(ativo=True)
    categorias = CategoriaProduto.objects.filter(ativo=True)
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca')
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    
    if busca:
        produtos = produtos.filter(titulo__icontains=busca)
    
    # Ordenação
    if ordenacao in ['preco_vista', '-preco_vista', 'titulo', '-titulo', 'avaliacao', '-avaliacao']:
        produtos = produtos.order_by(ordenacao)
    else:
        produtos = produtos.order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(produtos, 12)  # 12 produtos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Buscar carrinho do cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        carrinho, _ = CarrinhoCompras.objects.get_or_create(cliente=cliente)
        quantidade_carrinho = carrinho.get_quantidade_total()
    except Cliente.DoesNotExist:
        quantidade_carrinho = 0
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_selecionada': int(categoria_id) if categoria_id else None,
        'busca': busca,
        'ordenacao': ordenacao,
        'quantidade_carrinho': quantidade_carrinho,
    }
    
    return render(request, 'loja/produtos.html', context)

@login_required
def detalhes_produto(request, produto_id):
    """Detalhes de um produto específico"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem acessar a loja.')
        return redirect('usuarios:home_redirect')
    
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    
    # Buscar produtos relacionados da mesma categoria
    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria, 
        ativo=True
    ).exclude(id=produto.id)[:4]
    
    # Buscar carrinho do cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        carrinho, _ = CarrinhoCompras.objects.get_or_create(cliente=cliente)
        quantidade_carrinho = carrinho.get_quantidade_total()
    except Cliente.DoesNotExist:
        quantidade_carrinho = 0
    
    context = {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
        'quantidade_carrinho': quantidade_carrinho,
    }
    
    return render(request, 'loja/produto_detalhes.html', context)

@login_required
@csrf_protect
def adicionar_carrinho(request, produto_id):
    """Adiciona produto ao carrinho"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    if request.user.tipo_usuario != 'cliente':
        return JsonResponse({'success': False, 'message': 'Apenas clientes podem comprar'})
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        produto = get_object_or_404(Produto, id=produto_id, ativo=True)
        quantidade = int(request.POST.get('quantidade', 1))
        
        if quantidade <= 0:
            return JsonResponse({'success': False, 'message': 'Quantidade deve ser maior que zero'})
        
        carrinho, _ = CarrinhoCompras.objects.get_or_create(cliente=cliente)
        
        # Verificar se produto já está no carrinho
        item_carrinho, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': quantidade}
        )
        
        if not created:
            item_carrinho.quantidade += quantidade
            item_carrinho.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Produto adicionado ao carrinho!',
            'quantidade_carrinho': carrinho.get_quantidade_total()
        })
        
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro interno'})

@login_required
def carrinho(request):
    """Visualizar carrinho de compras"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem acessar o carrinho.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        carrinho, _ = CarrinhoCompras.objects.get_or_create(cliente=cliente)
        itens = carrinho.itens.all()
        
        context = {
            'carrinho': carrinho,
            'itens': itens,
            'total': carrinho.get_total(),
            'cliente': cliente,
        }
        
        return render(request, 'loja/carrinho.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
@csrf_protect
def finalizar_compra(request):
    """Finalizar compra do carrinho"""
    if request.method != 'POST':
        return redirect('loja:carrinho')
    
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem finalizar compras.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        carrinho = CarrinhoCompras.objects.get(cliente=cliente)
        
        if not carrinho.itens.exists():
            messages.error(request, 'Carrinho está vazio.')
            return redirect('loja:carrinho')
        
        forma_pagamento = request.POST.get('forma_pagamento')
        parcelas = int(request.POST.get('parcelas', 1))
        
        # Calcular total baseado na forma de pagamento
        total = Decimal('0')
        for item in carrinho.itens.all():
            if forma_pagamento == 'saldo':
                total += item.quantidade * item.produto.preco_vista
            else:  # crédito
                total += item.quantidade * item.produto.preco_prazo
        
        # Validações
        if forma_pagamento == 'saldo':
            if cliente.saldo < total:
                messages.error(request, 'Saldo insuficiente.')
                return redirect('loja:carrinho')
        elif forma_pagamento == 'credito':
            if not cliente.limite_credito_aprovado:
                messages.error(request, 'Limite de crédito não aprovado.')
                return redirect('loja:carrinho')
            if cliente.limite_credito < total:
                messages.error(request, 'Limite de crédito insuficiente.')
                return redirect('loja:carrinho')
        
        # Processar compra
        with transaction.atomic():
            # Criar compra
            compra = Compra.objects.create(
                cliente=cliente,
                valor_total=total,
                forma_pagamento=forma_pagamento,
                parcelas=parcelas
            )
            
            # Criar itens da compra
            for item in carrinho.itens.all():
                preco = item.produto.preco_vista if forma_pagamento == 'saldo' else item.produto.preco_prazo
                ItemCompra.objects.create(
                    compra=compra,
                    produto=item.produto,
                    quantidade=item.quantidade,
                    preco_unitario=preco,
                    valor_total=item.quantidade * preco
                )
            
            # Processar pagamento
            if forma_pagamento == 'saldo':
                cliente.saldo -= total
                cliente.save()
            else:  # crédito
                cliente.limite_credito -= total
                cliente.save()
                
                # Processar parcelamento se necessário
                if parcelas > 1:
                    processar_compra_parcelada(compra, parcelas)
            
            # Limpar carrinho
            carrinho.itens.all().delete()
            
            messages.success(request, f'Compra realizada com sucesso! Número do pedido: {compra.id}')
            return redirect('loja:compras')
            
    except Exception as e:
        messages.error(request, 'Erro ao processar compra. Tente novamente.')
        return redirect('loja:carrinho')

@login_required
def compras(request):
    """Lista compras do cliente"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver compras.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        compras_cliente = cliente.compras.all()
        
        # Paginação
        paginator = Paginator(compras_cliente, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'cliente': cliente,
        }
        
        return render(request, 'loja/compras.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')
