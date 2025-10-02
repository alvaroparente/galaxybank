from django.core.management.base import BaseCommand
from usuarios.models import Usuario, Cliente, Gerente
from datetime import date

class Command(BaseCommand):
    help = 'Cria usuários de teste (gerente e cliente)'

    def handle(self, *args, **options):
        # Criar usuário gerente
        try:
            gerente_user = Usuario.objects.create_user(
                username='gerente',
                password='Mesp@2025',
                email='gerente@galaxybank.com',
                first_name='João',
                last_name='Silva',
                tipo_usuario='gerente',
                telefone='(11) 99999-0001'
            )
            
            gerente = Gerente.objects.create(
                usuario=gerente_user,
                codigo_gerente='GER001',
                data_admissao=date.today(),
                ativo=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuário gerente criado: gerente / Mesp@2025'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao criar gerente: {e}'))

        # Criar usuário cliente
        try:
            cliente_user = Usuario.objects.create_user(
                username='cliente',
                password='Mesp@2025',
                email='cliente@galaxybank.com',
                first_name='Maria',
                last_name='Santos',
                tipo_usuario='cliente',
                telefone='(11) 99999-0002'
            )
            
            cliente = Cliente.objects.create(
                usuario=cliente_user,
                cpf='12345678901',
                score_pontos=100
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuário cliente criado: cliente / Mesp@2025'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao criar cliente: {e}'))

        self.stdout.write(self.style.SUCCESS('\n=== Usuários de teste criados com sucesso! ==='))
        self.stdout.write('Usuários disponíveis:')
        self.stdout.write('  • Superusuário: admin / admin')
        self.stdout.write('  • Gerente: gerente / Mesp@2025')
        self.stdout.write('  • Cliente: cliente / Mesp@2025')