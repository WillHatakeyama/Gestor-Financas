from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Conta, TipoMovimento, Transacao


class BaseTeste(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="senha-forte-123")
        self.client.login(username="ana", password="senha-forte-123")
        self.conta = Conta.objects.create(usuario=self.usuario, nome="Nubank", saldo_inicial=100)
        self.cat_despesa = Categoria.objects.create(
            usuario=self.usuario, nome="Mercado", tipo=TipoMovimento.DESPESA
        )
        self.cat_receita = Categoria.objects.create(
            usuario=self.usuario, nome="Salário", tipo=TipoMovimento.RECEITA
        )


class CadastroTeste(TestCase):
    def test_cadastro_cria_usuario_com_categorias_padrao(self):
        resposta = self.client.post(
            reverse("cadastro"),
            {
                "username": "joao",
                "first_name": "João",
                "email": "joao@exemplo.com",
                "password1": "UmaSenhaBoa#2026",
                "password2": "UmaSenhaBoa#2026",
            },
        )
        self.assertRedirects(resposta, reverse("dashboard"))
        self.assertTrue(Categoria.objects.filter(usuario__username="joao").exists())

    def test_paginas_exigem_login(self):
        resposta = self.client.get(reverse("conta_list"))
        self.assertEqual(resposta.status_code, 302)


class ContaTeste(BaseTeste):
    def test_crud_conta(self):
        self.client.post(reverse("conta_create"), {"nome": "Carteira", "tipo": "CA", "saldo_inicial": "50"})
        conta = Conta.objects.get(nome="Carteira")
        self.assertEqual(conta.usuario, self.usuario)

        self.client.post(
            reverse("conta_update", args=[conta.pk]), {"nome": "Bolso", "tipo": "CA", "saldo_inicial": "50"}
        )
        conta.refresh_from_db()
        self.assertEqual(conta.nome, "Bolso")

        self.client.post(reverse("conta_delete", args=[conta.pk]))
        self.assertFalse(Conta.objects.filter(pk=conta.pk).exists())

    def test_saldo_atual(self):
        Transacao.objects.create(conta=self.conta, categoria=self.cat_receita, descricao="Salário",
                                 valor=1000, data=date.today(), tipo=TipoMovimento.RECEITA)
        Transacao.objects.create(conta=self.conta, categoria=self.cat_despesa, descricao="Compras",
                                 valor=300, data=date.today(), tipo=TipoMovimento.DESPESA)
        self.assertEqual(self.conta.saldo_atual, Decimal("800"))

    def test_nao_acessa_conta_de_outro_usuario(self):
        outro = User.objects.create_user("bia", password="x")
        conta_outro = Conta.objects.create(usuario=outro, nome="Itaú")
        resposta = self.client.get(reverse("conta_update", args=[conta_outro.pk]))
        self.assertEqual(resposta.status_code, 404)


class CategoriaTeste(BaseTeste):
    def test_nao_exclui_categoria_com_transacoes(self):
        Transacao.objects.create(conta=self.conta, categoria=self.cat_despesa, descricao="Pão",
                                 valor=10, data=date.today(), tipo=TipoMovimento.DESPESA)
        self.client.post(reverse("categoria_delete", args=[self.cat_despesa.pk]))
        self.assertTrue(Categoria.objects.filter(pk=self.cat_despesa.pk).exists())


class TransacaoTeste(BaseTeste):
    def dados(self, **extra):
        base = {"descricao": "Almoço", "valor": "25.50", "data": "2026-11-10", "tipo": "D",
                "conta": self.conta.pk, "categoria": self.cat_despesa.pk}
        base.update(extra)
        return base

    def test_cria_transacao(self):
        self.client.post(reverse("transacao_create"), self.dados())
        self.assertEqual(Transacao.objects.count(), 1)

    def test_categoria_deve_bater_com_tipo(self):
        resposta = self.client.post(reverse("transacao_create"), self.dados(tipo="R"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Transacao.objects.count(), 0)

    def test_valor_deve_ser_positivo(self):
        self.client.post(reverse("transacao_create"), self.dados(valor="-5"))
        self.assertEqual(Transacao.objects.count(), 0)

    def test_filtro_por_categoria(self):
        self.client.post(reverse("transacao_create"), self.dados())
        resposta = self.client.get(reverse("transacao_list"), {"categoria": self.cat_receita.pk})
        self.assertEqual(len(resposta.context["object_list"]), 0)

    def test_dashboard(self):
        resposta = self.client.get(reverse("dashboard"))
        self.assertEqual(resposta.status_code, 200)