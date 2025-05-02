# Guia de Configuração e Fluxo de Trabalho para Agentes - Projeto BudgetApp

Este guia descreve os passos necessários para configurar o ambiente e o fluxo de trabalho atualizado para contribuir com o projeto BudgetApp.

## Pré-requisitos

*   Acesso a um ambiente Linux (como o sandbox fornecido) com Git instalado.
*   Python 3.11 instalado.

## 1. Configuração Inicial do Git

Configure seu nome de usuário e email globalmente no Git. Use um nome genérico.

```bash
git config --global user.name "BudgetApp Agent"
git config --global user.email "agent@budgetapp.example.com"
```

## 2. Obter Token de Acesso (PAT)

Para poder enviar (push) suas alterações, você precisa de um token de acesso pessoal (PAT) do GitHub. **Este token é sensível.**

*   **Solicite o token PAT atualizado ao gerente do projeto (Dione).**
*   **NÃO** inclua o token em nenhum arquivo versionado.

## 3. Clonar ou Atualizar o Repositório

Use a URL com o token para clonar ou atualizar o repositório. Substitua `<SEU_TOKEN_PAT>` pelo token fornecido por Dione.

**Usuário GitHub:** `lealflavio`

**Comando para Clonar (se for a primeira vez):**

```bash
cd /home/ubuntu
git clone https://lealflavio:<SEU_TOKEN_PAT>@github.com/lealflavio/BudgetApp.git
cd BudgetApp
```

**Comando para Atualizar URL Remota (se já clonou antes):**

```bash
cd /home/ubuntu/BudgetApp
git remote set-url origin https://lealflavio:<SEU_TOKEN_PAT>@github.com/lealflavio/BudgetApp.git
```

## 4. Configurar Ambiente Virtual (Recomendado)

```bash
# Dentro de /home/ubuntu/BudgetApp
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Para desativar: deactivate
```

## 5. Fluxo de Trabalho de Desenvolvimento e Conclusão de Tarefas

Siga estes passos para cada tarefa (Issue):

1.  **Identificar Tarefa:**
    *   Acesse as Issues: [https://github.com/lealflavio/BudgetApp/issues](https://github.com/lealflavio/BudgetApp/issues)
    *   Use a barra de busca para filtrar pelo seu nome (ex: `[Orfeu]`).
    *   Se não houver Issues abertas com seu nome, informe Dione.
2.  **Sincronizar e Criar Branch:**
    *   Certifique-se de estar no branch `develop` e que ele esteja atualizado:
        ```bash
        git checkout develop
        git pull origin develop
        ```
    *   Crie um branch para sua tarefa (substitua `X.Y` pelo número da Issue e `descricao-curta` por algo relevante):
        ```bash
        git checkout -b feature/issueX.Y-descricao-curta
        # Ex: git checkout -b feature/issue7-setup-lint-format
        ```
3.  **Desenvolver e Commitar:**
    *   Implemente a funcionalidade ou correção descrita na Issue.
    *   Faça commits pequenos e descritivos (`git add .`, `git commit -m "feat: Descrição da mudança"`). Consulte `CONTRIBUTING.md` para padrões de commit.
4.  **Enviar Alterações (Push):**
    *   Envie seu branch para o repositório remoto:
        ```bash
        git push origin feature/issueX.Y-descricao-curta
        ```
5.  **Notificar Conclusão a Dione (IMPORTANTE):**
    *   **Este é o passo crucial para "concluir a tarefa" no fluxo atual.**
    *   Envie uma mensagem para Dione informando:
        *   O número da Issue que você concluiu (ex: Issue #7).
        *   O nome exato do branch que você enviou (ex: `feature/issue7-setup-lint-format`).
    *   **Por quê?** Devido às limitações de autenticação nos ambientes dos agentes, vocês não conseguem interagir diretamente com a interface do GitHub para criar Pull Requests ou fechar Issues. Dione precisa ser notificado para realizar essas ações por vocês.
6.  **Ações de Dione (Gerente):**
    *   Após sua notificação, Dione irá:
        *   Criar o Pull Request do seu branch para o `develop`.
        *   Revisar o código (ou designar revisores).
        *   **Fechar a Issue correspondente no GitHub.**
        *   Fazer o merge do PR após aprovação.
7.  **Acompanhar Revisão:**
    *   Fique atento ao Pull Request criado por Dione para responder a possíveis comentários ou solicitações de alteração durante a revisão.

**Resumo da Mudança:** O desenvolvimento e push são feitos por vocês. A notificação a Dione é essencial. Dione cuida da criação do PR e fechamento da Issue no GitHub.

