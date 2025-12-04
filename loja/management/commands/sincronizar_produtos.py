from django.core.management.base import BaseCommand
from loja.models import sincronizar_produtos_api

class Command(BaseCommand):
    help = 'Sincroniza produtos da FakeStore API'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando sincronização de produtos...')
        
        if sincronizar_produtos_api():
            self.stdout.write(
                self.style.SUCCESS('Produtos sincronizados com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Erro ao sincronizar produtos.')
            )