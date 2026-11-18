from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Categoria, Conta, Transacao


class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Nome", max_length=150)

    class Meta:
        model = User
        fields = ["username", "first_name", "email"]


class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ["nome", "tipo", "saldo_inicial"]


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "tipo"]


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ["descricao", "valor", "data", "tipo", "conta", "categoria"]
        widgets = {"data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Só mostra contas e categorias do próprio usuário.
        self.fields["conta"].queryset = Conta.objects.filter(usuario=usuario)
        self.fields["categoria"].queryset = Categoria.objects.filter(usuario=usuario)

    def clean(self):
        dados = super().clean()
        categoria, tipo = dados.get("categoria"), dados.get("tipo")
        if categoria and tipo and categoria.tipo != tipo:
            self.add_error("categoria", "A categoria não corresponde ao tipo da transação.")
        return dados


class FiltroTransacaoForm(forms.Form):
    data_inicio = forms.DateField(
        label="De", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    data_fim = forms.DateField(
        label="Até", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(), required=False, empty_label="Todas"
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = Categoria.objects.filter(usuario=usuario)