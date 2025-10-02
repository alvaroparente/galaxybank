# Script para resetar o banco de dados e criar usuários de teste
# Galaxy Bank - Reset Database Script

Write-Host "=== Galaxy Bank - Reset Database Script ===" -ForegroundColor Cyan
Write-Host ""

# 1. Remover arquivo de banco de dados
Write-Host "1. Removendo banco de dados existente..." -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    try {
        Remove-Item "db.sqlite3" -Force
        Write-Host "   OK Banco de dados removido" -ForegroundColor Green
    } catch {
        Write-Host "   ERRO ao remover banco de dados. Feche todas as conexoes." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   OK Nenhum banco de dados encontrado" -ForegroundColor Green
}

# 2. Realizar migrações
Write-Host "2. Criando e aplicando migracoes..." -ForegroundColor Yellow
python manage.py makemigrations
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Migracoes criadas com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ERRO ao criar migracoes" -ForegroundColor Red
    exit 1
}

python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Migracoes aplicadas com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ERRO ao aplicar migracoes" -ForegroundColor Red
    exit 1
}

# 3. Criar superusuário
Write-Host "3. Criando superusuario..." -ForegroundColor Yellow
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "admin@admin.com"
$env:DJANGO_SUPERUSER_PASSWORD = "admin"
python manage.py createsuperuser --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Superusuario 'admin' criado" -ForegroundColor Green
} else {
    Write-Host "   ERRO ao criar superusuario" -ForegroundColor Red
    exit 1
}

# 4. Criar cliente
Write-Host "4. Criando usuario cliente..." -ForegroundColor Yellow
$createClientScript = @"
from django.contrib.auth import get_user_model
from usuarios.models import Cliente
User = get_user_model()

user = User.objects.create_user(
    username='cliente',
    email='cliente@galaxybank.com',
    password='Mesp@2025',
    first_name='Joao',
    last_name='Silva',
    tipo_usuario='cliente',
    telefone='(11) 99999-1234'
)

cliente = Cliente.objects.create(
    usuario=user,
    cpf='12345678901',
    score_pontos=100
)

print('Cliente criado com sucesso!')
"@

$createClientScript | python manage.py shell
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Cliente criado com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ERRO ao criar cliente" -ForegroundColor Red
    exit 1
}

# 5. Criar gerente
Write-Host "5. Criando usuario gerente..." -ForegroundColor Yellow
$createManagerScript = @"
from django.contrib.auth import get_user_model
from usuarios.models import Gerente
from datetime import date
User = get_user_model()

user = User.objects.create_user(
    username='gerente',
    email='gerente@galaxybank.com',
    password='Mesp@2025',
    first_name='Maria',
    last_name='Santos',
    tipo_usuario='gerente',
    telefone='(11) 99999-5678'
)

gerente = Gerente.objects.create(
    usuario=user,
    codigo_gerente='GER001',
    data_admissao=date.today(),
    ativo=True
)

print('Gerente criado com sucesso!')
"@

$createManagerScript | python manage.py shell
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Gerente criado com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ERRO ao criar gerente" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setup Concluido com Sucesso! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Usuarios criados:" -ForegroundColor White
Write-Host "+--------------+-------------------------+------------+" -ForegroundColor Gray
Write-Host "| Tipo         | Email                   | Senha      |" -ForegroundColor Gray
Write-Host "+--------------+-------------------------+------------+" -ForegroundColor Gray
Write-Host "| Superusuario | admin@admin.com         | admin      |" -ForegroundColor White
Write-Host "| Cliente      | cliente@galaxybank.com  | Mesp@2025  |" -ForegroundColor White
Write-Host "| Gerente      | gerente@galaxybank.com  | Mesp@2025  |" -ForegroundColor White
Write-Host "+--------------+-------------------------+------------+" -ForegroundColor Gray
Write-Host ""

# 6. Iniciar servidor
Write-Host "6. Iniciando servidor Django..." -ForegroundColor Yellow
Write-Host "   Servidor sera iniciado em: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "   Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

python manage.py runserver