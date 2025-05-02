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

## 2. Clonar o Repositório

Clone o repositório do projeto usando a URL que inclui o token de acesso pessoal (PAT) para autenticação. Isso permite que você faça push das suas alterações.

**Credenciais:**
*   **Usuário GitHub:** `lealflavio`
*   **Token de Acesso (PAT):** `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`

**Comando para Clonar:**

```bash
# Navegue para o diretório onde deseja clonar o projeto (ex: /home/ubuntu)
cd /home/ubuntu

# Clone usando a URL com token
git clone https://lealflavio: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@github.com/lealflavio/BudgetApp.git

# Entre no diretório do projeto
cd BudgetApp
```

**Importante:** O token de acesso (PAT) é sensível. Trate-o como uma senha.

## 3. Configurar Ambiente Virtual (Opcional, mas Recomendado)

Embora o ambiente sandbox possa ter as dependências, é uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Dentro do diretório /home/ubuntu/BudgetApp
python3.11 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Para desativar o ambiente virtual quando terminar:
# deactivate
```

## 4. Verificar Configuração

Verifique se você consegue se comunicar com o repositório remoto:

```bash
git status
git remote -v
# Deve mostrar o 'origin' apontando para a URL do GitHub
```

## 5. Próximos Passos: Pegando sua Primeira Tarefa

Seu ambiente está configurado! Agora, antes de começar a codificar, siga estes passos para obter sua primeira tarefa:

1.  **Verifique as Issues Atribuídas:** Acesse a seção de Issues do repositório no GitHub: [https://github.com/lealflavio/BudgetApp/issues](https://github.com/lealflavio/BudgetApp/issues). Verifique se já existe alguma Issue atribuída a você.
2.  **Consulte as Tarefas Iniciais:** Se nenhuma Issue estiver atribuída a você, consulte o arquivo `INITIAL_TASKS.md` no repositório. Ele lista as tarefas iniciais sugeridas por componente.
3.  **Comunique-se para Atribuição:** Escolha uma tarefa do `INITIAL_TASKS.md` que você gostaria de realizar ou, se tiver dúvidas, entre em contato com o gerente do projeto (Dione ou o administrador do repositório). **É crucial que uma Issue seja criada (ou existente) e formalmente atribuída a você no GitHub antes de você começar a trabalhar nela.**
4.  **Siga o Fluxo de Trabalho:** Uma vez que uma Issue esteja atribuída a você, siga o fluxo de trabalho descrito no arquivo `CONTRIBUTING.md`:
    *   Sincronize seu branch `develop` local com o remoto (`git pull origin develop`).
    *   Crie seu branch `feature/<nome-da-feature>` ou `bugfix/<nome-do-bug>` a partir do `develop`.
    *   Desenvolva sua tarefa, fazendo commits regulares.
    *   Faça push do seu branch para o GitHub (`git push origin feature/<nome-da-feature>`).
    *   Abra um Pull Request (PR) do seu branch para o `develop` no GitHub, referenciando a Issue que você está resolvendo.

Consulte o `CONTRIBUTING.md` para detalhes completos sobre o fluxo de trabalho e a estratégia de branches.