from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # UC01 - Autenticação
    path("login/", auth_views.LoginView.as_view(template_name="registro/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cadastro/", views.CadastroView.as_view(), name="cadastro"),
    # UC05 - Resumo
    path("", views.DashboardView.as_view(), name="dashboard"),
    # UC02 - Contas
    path("contas/", views.ContaListView.as_view(), name="conta_list"),
    path("contas/nova/", views.ContaCreateView.as_view(), name="conta_create"),
    path("contas/<int:pk>/editar/", views.ContaUpdateView.as_view(), name="conta_update"),
    path("contas/<int:pk>/excluir/", views.ContaDeleteView.as_view(), name="conta_delete"),
    # UC03 - Categorias
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nova/", views.CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria_update"),
    path("categorias/<int:pk>/excluir/", views.CategoriaDeleteView.as_view(), name="categoria_delete"),
    # UC04 - Transações
    path("transacoes/", views.TransacaoListView.as_view(), name="transacao_list"),
    path("transacoes/nova/", views.TransacaoCreateView.as_view(), name="transacao_create"),
    path("transacoes/<int:pk>/editar/", views.TransacaoUpdateView.as_view(), name="transacao_update"),
    path("transacoes/<int:pk>/excluir/", views.TransacaoDeleteView.as_view(), name="transacao_delete"),
]