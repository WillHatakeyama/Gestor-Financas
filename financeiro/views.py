"""
Views organizadas pelos casos de uso:

UC01 - Autenticar usuário ........ CadastroView (+ LoginView/LogoutView do Django)
UC02 - Gerenciar contas .......... Conta*View
UC03 - Gerenciar categorias ...... Categoria*View
UC04 - Gerenciar transações ...... Transacao*View
UC05 - Visualizar resumo ......... DashboardView
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import CadastroForm, CategoriaForm, ContaForm, FiltroTransacaoForm, TransacaoForm
from .models import Categoria, Conta, TipoMovimento, Transacao

CATEGORIAS_PADRAO = [
    ("Salário", TipoMovimento.RECEITA),
    ("Outras receitas", TipoMovimento.RECEITA),
    ("Alimentação", TipoMovimento.DESPESA),
    ("Moradia", TipoMovimento.DESPESA),
    ("Transporte", TipoMovimento.DESPESA),
    ("Lazer", TipoMovimento.DESPESA),
    ("Saúde", TipoMovimento.DESPESA),
]


# ---------------------------------------------------------------- Mixins
class DoUsuarioMixin(LoginRequiredMixin):
    """Garante que o usuário só veja e altere os próprios registros."""

    campo_usuario = "usuario"

    def get_queryset(self):
        return super().get_queryset().filter(**{self.campo_usuario: self.request.user})


class FormGenericoMixin:
    """Usa um template de formulário único para todos os cadastros."""

    template_name = "form.html"
    titulo = ""
    mensagem_sucesso = "Registro salvo com sucesso."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = self.titulo
        ctx["voltar_url"] = self.success_url
        return ctx

    def form_valid(self, form):
        messages.success(self.request, self.mensagem_sucesso)
        return super().form_valid(form)


class ExclusaoGenericaMixin:
    template_name = "confirmar_exclusao.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["voltar_url"] = self.success_url
        return ctx

    def form_valid(self, form):
        try:
            resposta = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: existem transações vinculadas a este registro.",
            )
            return HttpResponseRedirect(self.success_url)
        messages.success(self.request, "Registro excluído com sucesso.")
        return resposta


# ---------------------------------------------------------------- UC01 Autenticação
class CadastroView(CreateView):
    form_class = CadastroForm
    template_name = "registro/cadastro.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        resposta = super().form_valid(form)
        usuario = self.object
        Categoria.objects.bulk_create(
            [Categoria(usuario=usuario, nome=n, tipo=t) for n, t in CATEGORIAS_PADRAO]
        )
        login(self.request, usuario)
        messages.success(self.request, "Conta criada! Cadastre sua primeira conta bancária.")
        return resposta


# ---------------------------------------------------------------- UC02 Contas
class ContaListView(DoUsuarioMixin, ListView):
    model = Conta
    template_name = "conta.html"


class ContaCreateView(LoginRequiredMixin, FormGenericoMixin, CreateView):
    model = Conta
    form_class = ContaForm
    success_url = reverse_lazy("conta_list")
    titulo = "Nova conta"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class ContaUpdateView(DoUsuarioMixin, FormGenericoMixin, UpdateView):
    model = Conta
    form_class = ContaForm
    success_url = reverse_lazy("conta_list")
    titulo = "Editar conta"


class ContaDeleteView(DoUsuarioMixin, ExclusaoGenericaMixin, DeleteView):
    model = Conta
    success_url = reverse_lazy("conta_list")


# ---------------------------------------------------------------- UC03 Categorias
class CategoriaListView(DoUsuarioMixin, ListView):
    model = Categoria
    template_name = "categoria.html"


class CategoriaCreateView(LoginRequiredMixin, FormGenericoMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("categoria_list")
    titulo = "Nova categoria"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CategoriaUpdateView(DoUsuarioMixin, FormGenericoMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("categoria_list")
    titulo = "Editar categoria"


class CategoriaDeleteView(DoUsuarioMixin, ExclusaoGenericaMixin, DeleteView):
    model = Categoria
    success_url = reverse_lazy("categoria_list")


# ---------------------------------------------------------------- UC04 Transações
class TransacaoFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs


class TransacaoListView(DoUsuarioMixin, ListView):
    model = Transacao
    template_name = "transacao.html"
    campo_usuario = "conta__usuario"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("conta", "categoria")
        self.filtro = FiltroTransacaoForm(self.request.GET or None, usuario=self.request.user)
        if self.filtro.is_valid():
            f = self.filtro.cleaned_data
            if f["data_inicio"]:
                qs = qs.filter(data__gte=f["data_inicio"])
            if f["data_fim"]:
                qs = qs.filter(data__lte=f["data_fim"])
            if f["categoria"]:
                qs = qs.filter(categoria=f["categoria"])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filtro"] = self.filtro
        ctx["parametros"] = self.request.GET.copy()
        ctx["parametros"].pop("page", None)
        return ctx


class TransacaoCreateView(LoginRequiredMixin, TransacaoFormMixin, FormGenericoMixin, CreateView):
    model = Transacao
    form_class = TransacaoForm
    success_url = reverse_lazy("transacao_list")
    titulo = "Nova transação"

    def get_initial(self):
        return {"data": timezone.localdate(), "tipo": TipoMovimento.DESPESA}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.contas.exists():
            messages.warning(request, "Cadastre uma conta antes de lançar transações.")
            return HttpResponseRedirect(reverse_lazy("conta_create"))
        return super().dispatch(request, *args, **kwargs)


class TransacaoUpdateView(DoUsuarioMixin, TransacaoFormMixin, FormGenericoMixin, UpdateView):
    model = Transacao
    form_class = TransacaoForm
    success_url = reverse_lazy("transacao_list")
    campo_usuario = "conta__usuario"
    titulo = "Editar transação"


class TransacaoDeleteView(DoUsuarioMixin, ExclusaoGenericaMixin, DeleteView):
    model = Transacao
    success_url = reverse_lazy("transacao_list")
    campo_usuario = "conta__usuario"


# ---------------------------------------------------------------- UC05 Resumo
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        hoje = timezone.localdate()

        contas = list(Conta.objects.filter(usuario=usuario))
        transacoes_mes = Transacao.objects.filter(
            conta__usuario=usuario, data__year=hoje.year, data__month=hoje.month
        )

        def total(tipo):
            return transacoes_mes.filter(tipo=tipo).aggregate(s=Sum("valor"))["s"] or Decimal("0")

        receitas = total(TipoMovimento.RECEITA)
        despesas = total(TipoMovimento.DESPESA)

        por_categoria = (
            transacoes_mes.filter(tipo=TipoMovimento.DESPESA)
            .values("categoria__nome")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

        ctx.update(
            {
                "mes_referencia": hoje,
                "contas": contas,
                "saldo_total": sum((c.saldo_atual for c in contas), Decimal("0")),
                "receitas_mes": receitas,
                "despesas_mes": despesas,
                "resultado_mes": receitas - despesas,
                "ultimas": Transacao.objects.filter(conta__usuario=usuario)
                .select_related("categoria", "conta")[:5],
                "grafico": {
                    "labels": [c["categoria__nome"] for c in por_categoria],
                    "valores": [float(c["total"]) for c in por_categoria],
                },
            }
        )
        return ctx