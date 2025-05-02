# Guia de Configuração do Ambiente para Agentes - Projeto BudgetApp

Este guia descreve os passos necessários para que um novo agente configure seu ambiente de desenvolvimento para contribuir com o projeto BudgetApp.

## Pré-requisitos

*   Acesso a um ambiente Linux (como o sandbox fornecido) com Git instalado.
*   Python 3.11 instalado.

## 1. Configuração Inicial do Git

Antes de clonar o repositório, configure seu nome de usuário e email globalmente no Git. Use um nome genérico para o agente.

```bash
git config --global user.name "BudgetApp Agent"
git config --global user.email "agent@budgetapp.example.com"
```

## 2. Obter Token de Acesso (PAT)

Para poder enviar (push) suas alterações de código, você precisa de um token de acesso pessoal (PAT) do GitHub. **Este token é sensível e não deve ser compartilhado publicamente ou incluído em commits.**

*   **Solicite o token de acesso pessoal (PAT) atualizado ao gerente do projeto (Dione).**
*   **NÃO** inclua o token diretamente em nenhum arquivo versionado.

## 3. Clonar o Repositório

Clone o repositório do projeto usando a URL que inclui o token de acesso pessoal (PAT) para autenticação. Substitua `<SEU_TOKEN_PAT>` pelo token fornecido por Dione.

**Credenciais:**
*   **Usuário GitHub:** `lealflavio`

**Comando para Clonar:**

```bash
# Navegue para o diretório onde deseja clonar o projeto (ex: /home/ubuntu)
cd /home/ubuntu

# Clone usando a URL com o token (substitua <SEU_TOKEN_PAT> pelo token fornecido por Dione)
git clone https://lealflavio:<SEU_TOKEN_PAT>@github.com/lealflavio/BudgetApp.git

# Entre no diretório do projeto
cd BudgetApp
```

**Alternativa (Configuração Remota):** Se você já clonou o repositório anteriormente, pode atualizar a URL remota para usar o novo token:

```bash
cd /home/ubuntu/BudgetApp
# Substitua <SEU_TOKEN_PAT> pelo token fornecido por Dione
git remote set-url origin https://lealflavio:<SEU_TOKEN_PAT>@github.com/lealflavio/BudgetApp.git
```

**Importante:** Trate o token de acesso (PAT) como uma senha.

## 4. Configurar Ambiente Virtual (Opcional, mas Recomendado)

```bash
# Dentro do diretório /home/ubuntu/BudgetApp
python3.11 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Para desativar o ambiente virtual quando terminar:
# deactivate
```

## 5. Verificar Configuração

Verifique se você consegue se comunicar com o repositório remoto:

```bash
git status
git remote -v
# Deve mostrar o 'origin' apontando para a URL do GitHub com seu token
```

## 6. Próximos Passos: Pegando sua Primeira Tarefa e Fluxo de Trabalho Atualizado

Seu ambiente está configurado! Agora, siga estes passos para obter sua tarefa e contribuir:

1.  **Verifique as Issues Atribuídas:** Acesse a seção de Issues do repositório no GitHub: [https://github.com/lealflavio/BudgetApp/issues](https://github.com/lealflavio/BudgetApp/issues).
2.  **Consulte as Tarefas Iniciais:** Se nenhuma Issue estiver atribuída, consulte `INITIAL_TASKS.md`.
3.  **Comunique-se para Atribuição:** Peça a Dione (Gerente) para atribuir uma Issue a você.
4.  **Siga o Fluxo de Trabalho Modificado:**
    *   Sincronize e crie seu branch `feature/...` ou `bugfix/...` a partir do `develop`.
    *   Desenvolva e faça commits regulares.
    *   Faça push do seu branch (`git push origin feature/...`).
    *   **Notifique Dione:** Informe que concluiu e fez push do branch.
    *   **Dione Criará o Pull Request:** Dione criará o PR para o `develop`.
    *   **Acompanhe a Revisão:** Acompanhe o PR criado por Dione.

Consulte `CONTRIBUTING.md` para detalhes sobre branches e commits. A principal mudança é que **Dione criará os Pull Requests**.

