# Tarefas Iniciais por Componente - BudgetApp
teste
Este documento descreve as tarefas iniciais sugeridas para cada componente do projeto BudgetApp, visando o desenvolvimento colaborativo por múltiplos agentes.

**Observação:** Estas são tarefas iniciais. Novas tarefas serão definidas e atribuídas através das Issues do GitHub conforme o projeto avança.

## 1. Backend - Núcleo e Autenticação (Orfeu)

*   **Tarefa 1.1:** Revisar e refatorar o código existente em `src/main.py`, `src/extensions.py`, `src/models/user.py`, `src/routes/auth.py` para garantir clareza, conformidade com PEP 8 e boas práticas.
*   **Tarefa 1.2:** Implementar testes unitários básicos para as funcionalidades de autenticação (registro, login, logout).
*   **Tarefa 1.3:** Configurar um linter (ex: Flake8) e um formatador (ex: Black) para o projeto e garantir que o código base esteja em conformidade.
*   **Tarefa 1.4:** (Concluído por Dione) Criar o branch `develop` a partir do `main` no repositório GitHub.

## 2. Backend - API de Contas e Categorias (Nyx)

*   **Tarefa 2.1:** Revisar e refatorar o código existente em `src/models/account.py`, `src/routes/accounts.py`, `src/models/category.py`, `src/routes/categories.py`.
*   **Tarefa 2.2:** Garantir que as rotas da API para CRUD de Contas estejam completas, retornando JSON consistente e tratando erros adequadamente.
*   **Tarefa 2.3:** Garantir que as rotas da API para CRUD de Categorias (incluindo distinção entre padrão e customizada) estejam completas, retornando JSON consistente e tratando erros.
*   **Tarefa 2.4:** Implementar testes unitários para as APIs de Contas e Categorias.

## 3. Backend - API de Transações e Resumos (Selene)

*   **Tarefa 3.1:** Revisar e refatorar o código existente em `src/models/transaction.py`, `src/routes/transactions.py`, `src/routes/summary.py`.
*   **Tarefa 3.2:** Garantir que as rotas da API para CRUD de Transações estejam completas, retornando JSON consistente, tratando erros e validando dados de entrada.
*   **Tarefa 3.3:** Implementar/Refinar as rotas da API para Resumos (`/summary`), garantindo que os cálculos estejam corretos e os dados retornados sejam úteis para o frontend.
*   **Tarefa 3.4:** Implementar testes unitários para as APIs de Transações e Resumos.

## 4. Frontend - Interface Principal e Dashboard (Symbol)

*   **Tarefa 4.1:** Configurar um framework CSS moderno (ex: Tailwind CSS) no projeto Flask para ser usado nos templates.
*   **Tarefa 4.2:** Redesenhar os templates `layout.html`, `login.html`, `register.html` para se aproximarem do design das imagens de referência, utilizando o framework CSS configurado.
*   **Tarefa 4.3:** Implementar o template inicial do Dashboard (`index.html`), buscando dados básicos (ex: nome do usuário) do backend (pode ser via contexto do Jinja2 inicialmente).
*   **Tarefa 4.4:** Criar a estrutura básica de navegação (menu inferior ou lateral, conforme imagens) no `layout.html`.

## 5. Frontend - Interface de Operações CRUD (Zaun)

*   **Tarefa 5.1:** Projetar e implementar o template HTML para a listagem de Contas, buscando dados da API `/accounts`.
*   **Tarefa 5.2:** Projetar e implementar o formulário/modal para adicionar/editar Contas, enviando dados para a API `/accounts`.
*   **Tarefa 5.3:** Projetar e implementar o template HTML para a listagem de Categorias, buscando dados da API `/categories`.
*   **Tarefa 5.4:** Projetar e implementar o formulário/modal para adicionar/editar Categorias, enviando dados para a API `/categories`.

## 6. Gerenciamento e Coordenação (Dione)

*   **Tarefa 6.1:** Monitorar a configuração de Integração Contínua (GitHub Actions) e refinar os workflows conforme necessário.
*   **Tarefa 6.2:** Criar as Issues iniciais no GitHub com base neste documento e atribuí-las aos respectivos agentes (Nyx, Orfeu, Selene, Symbol, Zaun).
*   **Tarefa 6.3:** Revisar Pull Requests (PRs) enviados pelos outros agentes para o branch `develop`, garantindo a qualidade e conformidade com as diretrizes.
*   **Tarefa 6.4:** Facilitar a comunicação entre os agentes e auxiliar na resolução de bloqueios ou dúvidas.

## Próximas Fases (Exemplos)

*   **Frontend:** Implementação do CRUD de Transações, gráficos no Dashboard, funcionalidade de filtros/busca.
*   **Backend:** Validações mais robustas, tratamento de anexos, notificações, relatórios avançados.
*   **Geral:** Testes de integração, CI/CD, implantação.

