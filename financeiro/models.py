"""
Entidades do sistema (base para o DER e o Diagrama de Classes).

Usuario   1 ── N  Conta
Usuario   1 ── N  Categoria
Conta     1 ── N  Transacao
Categoria 1 ── N  Transacao

O Usuario é o model padrão do Django (django.contrib.auth.models.User).
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class TipoMovimento(models.TextChoices):
    RECEITA = "R", "Receita"
    DESPESA = "D", "Despesa"


class Conta(models.Model):
    class TipoConta(models.TextChoices):
        CORRENTE = "CC", "Conta corrente"
        POUPANCA = "PO", "Poupança"
        CARTEIRA = "CA", "Carteira"
        INVESTIMENTO = "IN", "Investimento"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contas"
    )
    nome = models.CharField(max_length=60)
    tipo = models.CharField(max_length=2, choices=TipoConta.choices, default=TipoConta.CORRENTE)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "nome"], name="conta_nome_unico_por_usuario")
        ]

    def __str__(self):
        return self.nome

    @property
    def saldo_atual(self) -> Decimal:
        """Saldo inicial + receitas - despesas."""
        totais = self.transacoes.values("tipo").annotate(total=Sum("valor"))
        mapa = {t["tipo"]: t["total"] for t in totais}
        receitas = mapa.get(TipoMovimento.RECEITA, Decimal("0"))
        despesas = mapa.get(TipoMovimento.DESPESA, Decimal("0"))
        return self.saldo_inicial + receitas - despesas


class Categoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categorias"
    )
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1, choices=TipoMovimento.choices)

    class Meta:
        ordering = ["tipo", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "nome", "tipo"], name="categoria_unica_por_usuario"
            )
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Transacao(models.Model):
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name="transacoes")
    # PROTECT: não deixa excluir uma categoria que ainda tem transações.
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="transacoes")
    descricao = models.CharField(max_length=120)
    valor = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    data = models.DateField()
    tipo = models.CharField(max_length=1, choices=TipoMovimento.choices)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "transação"
        verbose_name_plural = "transações"

    def __str__(self):
        return f"{self.data:%d/%m/%Y} - {self.descricao} - R$ {self.valor}"