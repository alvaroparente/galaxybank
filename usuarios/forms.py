from django import forms
from django.contrib.auth import get_user_model
from .models import Cliente
import re

User = get_user_model()

class RegistroUsuarioForm(forms.Form):
    """Primeira etapa: dados básicos do usuário"""
    first_name = forms.CharField(
        max_length=30,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite seu nome',
            'required': True
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite seu sobrenome',
            'required': True
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'seuemail@exemplo.com',
            'required': True
        })
    )
    telefone = forms.CharField(
        max_length=15,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '(11) 99999-9999',
            'required': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email
    
    def clean_telefone(self):
        telefone = self.cleaned_data['telefone']
        # Remove formatação
        telefone_numbers = re.sub(r'\D', '', telefone)
        if len(telefone_numbers) < 10 or len(telefone_numbers) > 11:
            raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        return telefone


class RegistroClienteForm(forms.Form):
    """Segunda etapa: dados específicos do cliente"""
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '000.000.000-00',
            'required': True
        })
    )
    
    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        # Remove formatação
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        # Validação básica de CPF
        if len(cpf_numbers) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')
        
        # Verifica se todos os dígitos são iguais
        if cpf_numbers == cpf_numbers[0] * 11:
            raise forms.ValidationError('CPF inválido.')
        
        # Verifica se CPF já existe
        if Cliente.objects.filter(cpf=cpf_numbers).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
        
        return cpf_numbers


class RegistroSenhaForm(forms.Form):
    """Terceira etapa: criação de username e senha"""
    username = forms.CharField(
        max_length=150,
        label='Nome de usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Escolha um nome de usuário',
            'required': True
        }),
        help_text='Apenas letras, números e os caracteres @/./+/-/_ permitidos.'
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite sua senha',
            'required': True
        }),
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirme sua senha',
            'required': True
        })
    )
    aceitar_termos = forms.BooleanField(
        label='Aceito os termos de uso e política de privacidade',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': True
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já existe.')
        return username
    
    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if len(password1) < 8:
            raise forms.ValidationError('A senha deve ter pelo menos 8 caracteres.')
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data