# Divisão de Componentes e Módulos - BudgetApp

Este documento descreve a divisão inicial do projeto BudgetApp em componentes lógicos para facilitar o desenvolvimento colaborativo por múltiplos agentes.

## Visão Geral

O projeto é uma aplicação web Flask com funcionalidades de backend (API) e uma interface de usuário (frontend) que precisa ser desenvolvida para corresponder às imagens de referência (estilo aplicativo móvel).

## Componentes Principais

Propomos a seguinte divisão inicial em componentes/áreas de foco:

1.  **Backend - Núcleo e Autenticação:**
    *   **Foco:** Estrutura base do Flask, autenticação de usuários, gerenciamento de sessão, configuração inicial do banco de dados e migrações.
    *   **Arquivos Principais:** `src/main.py`, `src/extensions.py`, `src/models/user.py`, `src/routes/auth.py`, `migrations/`.

2.  **Backend - API de Contas e Categorias:**
    *   **Foco:** Desenvolvimento e manutenção das rotas da API (CRUD) para gerenciamento de Contas e Categorias financeiras.
    *   **Arquivos Principais:** `src/models/account.py`, `src/routes/accounts.py`, `src/models/category.py`, `src/routes/categories.py`.

3.  **Backend - API de Transações e Resumos:**
    *   **Foco:** Desenvolvimento e manutenção das rotas da API (CRUD) para gerenciamento de Transações (receitas/despesas) e endpoints para geração de resumos financeiros.
    *   **Arquivos Principais:** `src/models/transaction.py`, `src/routes/transactions.py`, `src/routes/summary.py`.

4.  **Frontend - Interface Principal e Dashboard:**
    *   **Foco:** Implementação da estrutura principal da interface do usuário (layout, navegação), telas de Login/Registro e o Dashboard principal, buscando dados das APIs do backend.
    *   **Arquivos Principais:** `src/static/` (HTML, CSS, JS), `src/forms.py` (se aplicável para renderização de formulários no servidor).
    *   **Tecnologia:** Inicialmente usando templates Flask (Jinja2) com CSS moderno (ex: Tailwind CSS a ser adicionado) para simular a aparência das imagens de referência, ou transição para um framework SPA (React/Vue) se decidido posteriormente.

5.  **Frontend - Interface de Operações CRUD:**
    *   **Foco:** Implementação das telas e fluxos de usuário para criar, visualizar, editar e excluir Contas, Categorias e Transações, integrando com as respectivas APIs do backend.
    *   **Arquivos Principais:** `src/static/` (HTML, CSS, JS), `src/forms.py` (se aplicável).

## Considerações

*   Esta é uma divisão inicial e pode ser ajustada conforme o projeto evolui.
*   A comunicação entre os agentes responsáveis pelo frontend e backend será crucial, especialmente na definição e consumo das APIs.
*   Um sexto componente (ou responsabilidade distribuída) seria a **Infraestrutura/DevOps**, incluindo configuração de CI/CD e implantação, que pode ser gerenciado pelo gerente de projeto (Dione) ou atribuído a um agente específico posteriormente.

Esta divisão permite que até 5 agentes trabalhem em paralelo nas diferentes partes do aplicativo.
