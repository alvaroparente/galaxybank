from django import forms
from .models import SolicitacaoCredito
from decimal import Decimal

class SolicitacaoCreditoForm(forms.ModelForm):
    """Formulário para solicitação de crédito"""
    
    class Meta:
        model = SolicitacaoCredito
        fields = ['valor_solicitado', 'justificativa', 'renda_mensal', 'profissao']
        labels = {
            'valor_solicitado': 'Valor do Limite Solicitado',
            'justificativa': 'Justificativa',
            'renda_mensal': 'Renda Mensal',
            'profissao': 'Profissão',
        }
        widgets = {
            'valor_solicitado': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '100'
            }),
            'justificativa': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explique o motivo da solicitação e como pretende usar o crédito',
                'rows': 4
            }),
            'renda_mensal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '0'
            }),
            'profissao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Analista de Sistemas, Professor, etc.',
                'maxlength': '100'
            }),
        }
    
    def clean_valor_solicitado(self):
        valor = self.cleaned_data['valor_solicitado']
        if valor < Decimal('100'):
            raise forms.ValidationError('Valor mínimo para solicitação é R$ 100,00')
        if valor > Decimal('50000'):
            raise forms.ValidationError('Valor máximo para solicitação é R$ 50.000,00')
        return valor
    
    def clean_renda_mensal(self):
        renda = self.cleaned_data['renda_mensal']
        if renda <= 0:
            raise forms.ValidationError('Renda mensal deve ser maior que zero')
        return renda
    
    def clean(self):
        cleaned_data = super().clean()
        valor_solicitado = cleaned_data.get('valor_solicitado')
        renda_mensal = cleaned_data.get('renda_mensal')
        
        if valor_solicitado and renda_mensal:
            # Verificar se o valor solicitado não excede 5x a renda mensal
            limite_max = renda_mensal * Decimal('5')
            if valor_solicitado > limite_max:
                raise forms.ValidationError(
                    f'O valor solicitado não pode exceder 5x sua renda mensal (R$ {limite_max:.2f})'
                )
        
        return cleaned_data