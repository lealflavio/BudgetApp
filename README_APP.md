# Aplicação Web de Orçamento Familiar (Flask)

Este documento descreve a estrutura e a lógica da aplicação web de orçamento familiar desenvolvida em Flask.

## Visão Geral

A aplicação permite que usuários se registrem, façam login e gerenciem suas finanças pessoais, incluindo:

*   **Contas:** Cadastro de diferentes tipos de contas (corrente, poupança, cartão, etc.).
*   **Categorias:** Definição de categorias de receitas e despesas (com categorias padrão e personalizadas).
*   **Transações:** Registro de receitas e despesas, associando-as a contas e categorias.
*   **Resumos:** Visualização de totais mensais de receitas, despesas e saldos.

## Estrutura do Projeto (`budget_app`)

```
budget_app/
├── migrations/         # Arquivos de migração do banco de dados (Flask-Migrate/Alembic)
├── src/
│   ├── extensions.py   # Inicialização das extensões Flask (db, login, migrate)
│   ├── forms.py        # Definição dos formulários WTForms
│   ├── main.py         # Ponto de entrada principal, criação da app Flask, registro de blueprints
│   ├── models/         # Modelos de dados SQLAlchemy (User, Account, Category, Transaction)
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── routes/         # Blueprints com as rotas da aplicação
│   │   ├── __init__.py
│   │   ├── accounts.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── summary.py
│   │   └── transactions.py
│   └── static/         # Arquivos estáticos (CSS, JS, HTML templates)
│       ├── css/
│       │   └── style.css
│       ├── 404.html
│       ├── 500.html
│       ├── index.html
│       ├── layout.html
│       ├── login.html
│       └── register.html
├── venv/               # Ambiente virtual Python (não incluído no zip)
├── requirements.txt    # Dependências Python do projeto
└── README_APP.md       # Este arquivo
```

## Configuração e Execução

1.  **Dependências:** Instale as dependências listadas em `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Banco de Dados:**
    *   A aplicação está configurada para usar MySQL (`mysql+pymysql`).
    *   Certifique-se de ter um servidor MySQL rodando.
    *   **Variáveis de Ambiente:** Configure as seguintes variáveis de ambiente (ou ajuste os valores padrão em `src/main.py`):
        *   `DB_USERNAME`: Usuário do banco de dados (padrão: `root`)
        *   `DB_PASSWORD`: Senha do banco de dados (padrão: `password`)
        *   `DB_HOST`: Host do banco de dados (padrão: `localhost`)
        *   `DB_PORT`: Porta do banco de dados (padrão: `3306`)
        *   `DB_NAME`: Nome do banco de dados (padrão: `mydb`) - **Crie este banco de dados no MySQL antes de continuar.**
    *   **Migrações:** Aplique as migrações para criar as tabelas:
        ```bash
        export FLASK_APP=src/main.py
        flask db upgrade
        ```
3.  **Chave Secreta:** Defina a variável de ambiente `FLASK_SECRET_KEY` para segurança em produção. Um valor padrão é usado para desenvolvimento.
4.  **Execução (Desenvolvimento):**
    ```bash
    export FLASK_APP=src/main.py
    flask run --host=0.0.0.0 --port=5000
    ```
    Ou diretamente:
    ```bash
    python src/main.py
    ```

## Lógica Implementada

*   **Autenticação (`routes/auth.py`, `models/user.py`, `forms.py`):**
    *   Registro de novos usuários com hash de senha.
    *   Login e logout de usuários usando Flask-Login.
    *   Proteção de rotas com `@login_required`.
*   **Gerenciamento (CRUD - Create, Read, Update, Delete):**
    *   **Contas (`routes/accounts.py`, `models/account.py`):** Rotas para adicionar, listar, editar e excluir contas associadas ao usuário logado.
    *   **Categorias (`routes/categories.py`, `models/category.py`):** Rotas para adicionar, listar, editar e excluir categorias personalizadas. Categorias padrão (sem `user_id`) também são consideradas.
    *   **Transações (`routes/transactions.py`, `models/transaction.py`):** Rotas para adicionar, listar, editar e excluir transações (receitas/despesas), associadas a contas e categorias do usuário.
*   **Resumos (`routes/summary.py`):**
    *   Endpoint para calcular e retornar totais mensais de receitas, despesas e saldo.
    *   Endpoint para resumir transações pendentes (não pagas/recebidas).
*   **Estrutura (`main.py`, `extensions.py`):**
    *   Uso do padrão `create_app` para configuração da aplicação.
    *   Inicialização centralizada de extensões em `extensions.py` para evitar importações circulares.
    *   Registro de Blueprints para organizar as rotas.

## Observações

*   **Interface Frontend:** Os templates HTML (`src/static/*.html`) são básicos e foram criados principalmente para testar a autenticação. As rotas de CRUD atualmente retornam JSON e precisam ser integradas aos templates para uma interface funcional.
*   **Testes:** A fase de testes interativos foi interrompida. O código pode conter bugs ou problemas não identificados.
*   **Mockups:** A implementação seguiu a lógica geral dos mockups fornecidos, mas a interface visual detalhada não foi totalmente implementada nos templates HTML.

Este código fornece a base funcional para a aplicação web de orçamento familiar.
