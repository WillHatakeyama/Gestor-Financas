# 💰 Controle Financeiro

Projeto da disciplina **Desenvolvimento de Projetos II** (UniFil).

**Autor:** William Eizo Hatakeyama (projeto individual)

Sistema web para controle de finanças pessoais. O usuário cadastra suas contas
(corrente, poupança, carteira...), organiza categorias de receitas e despesas,
registra transações e acompanha um resumo mensal com gráfico de gastos por categoria.

## Stack

- **Linguagem:** Python 3.10+
- **Framework:** Django 5.2
- **Banco de dados:** SQLite (via ORM do Django)
- **Front-end:** templates do Django, Bootstrap 5 e Chart.js

## Funcionalidades (casos de uso)

| Caso de uso | Descrição |
|---|---|
| UC01 · Autenticar usuário | Cadastro, login e logout |
| UC02 · Gerenciar contas | CRUD de contas, com saldo atual calculado |
| UC03 · Gerenciar categorias | CRUD de categorias de receita/despesa |
| UC04 · Gerenciar transações | CRUD de transações com filtro por período e categoria |
| UC05 · Visualizar resumo | Saldo total, receitas/despesas do mês e gráfico por categoria |

## Como executar

```bash
git clone <url-do-repositorio>
cd financas

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # opcional, para acessar /admin
python manage.py runserver
```

Acesse http://127.0.0.1:8000 e crie uma conta.

## Testes

```bash
python manage.py test
```

## Estrutura

```
financas/
├── config/                 # Configurações do projeto
│   ├── settings.py
│   └── url.py              # Rotas principais (ROOT_URLCONF = "config.url")
├── financeiro/             # App principal
│   ├── models.py           # Entidades: Conta, Categoria, Transacao
│   ├── forms.py            # Formulários e validações
│   ├── views.py            # Regras de negócio por caso de uso
│   ├── urls.py             # Rotas do app
│   ├── admin.py            # Painel administrativo
│   ├── tests.py            # Testes automatizados
│   ├── migracoes/          # Migrações (configurado via MIGRATION_MODULES)
│   └── templates/          # Telas: dashboard, conta, categoria, transacao,
│                           #        form e confirmar_exclusao
├── templates/              # Templates compartilhados
│   ├── base.html           # Layout base
│   ├── campos.html         # Renderização dos campos de formulário
│   └── registro/           # Login e cadastro
├── css/estilo.css          # Estilos (servido em /static/css/estilo.css)
├── manage.py
└── requirements.txt
```