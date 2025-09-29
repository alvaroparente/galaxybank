from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Cliente, Gerente
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários de demonstração para o sistema Galaxy Bank'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Criando usuários de demonstração...')
        )
        
        # Criar superusuário admin
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@galaxy.com',
                password='admin123',
                first_name='Administrator',
                last_name='Galaxy',
                tipo_usuario='gerente'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Superusuário criado: admin / admin123')
            )
        
        # Criar usuário Cliente
        if not User.objects.filter(username='cliente').exists():
            cliente_user = User.objects.create_user(
                username='cliente',
                email='cliente@galaxy.com',
                password='cliente123',
                first_name='Maria',
                last_name='Silva',
                tipo_usuario='cliente',
                telefone='11987654321'
            )
            
            # Criar perfil de cliente
            Cliente.objects.create(
                usuario=cliente_user,
                cpf='12345678901',
                score_pontos=1250
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cliente criado: cliente / cliente123')
            )
        
        # Criar usuário Gerente
        if not User.objects.filter(username='gerente').exists():
            gerente_user = User.objects.create_user(
                username='gerente',
                email='gerente@galaxy.com',
                password='gerente123',
                first_name='João',
                last_name='Santos',
                tipo_usuario='gerente',
                telefone='11987654322'
            )
            
            # Criar perfil de gerente
            Gerente.objects.create(
                usuario=gerente_user,
                codigo_gerente='GER001',
                data_admissao=date(2023, 1, 15),
                ativo=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Gerente criado: gerente / gerente123')
            )
        
        # Criar mais alguns usuários de exemplo
        usuarios_exemplo = [
            {
                'username': 'ana.costa',
                'email': 'ana.costa@email.com',
                'password': 'senha123',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'tipo_usuario': 'cliente',
                'cpf': '98765432109',
                'score_pontos': 850
            },
            {
                'username': 'carlos.oliveira',
                'email': 'carlos.oliveira@email.com',
                'password': 'senha123',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'tipo_usuario': 'cliente',
                'cpf': '45678912345',
                'score_pontos': 2100
            }
        ]
        
        for user_data in usuarios_exemplo:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    tipo_usuario=user_data['tipo_usuario']
                )
                
                if user_data['tipo_usuario'] == 'cliente':
                    Cliente.objects.create(
                        usuario=user,
                        cpf=user_data['cpf'],
                        score_pontos=user_data['score_pontos']
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuario {user_data["first_name"]} criado')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Todos os usuários de demonstração foram criados com sucesso!')
        )
        self.stdout.write(
            self.style.WARNING('\n📝 Credenciais de acesso:')
        )
        self.stdout.write('   • Admin: admin / admin123')
        self.stdout.write('   • Cliente: cliente / cliente123')
        self.stdout.write('   • Gerente: gerente / gerente123')
        self.stdout.write(
            self.style.HTTP_INFO('\n🚀 Execute: python manage.py runserver')
        )