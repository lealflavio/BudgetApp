# Diretrizes de Contribuição para o Projeto BudgetApp

Este documento descreve as diretrizes e o fluxo de trabalho para contribuir com o desenvolvimento do projeto BudgetApp, especialmente em um ambiente com múltiplos agentes colaborando simultaneamente.

## 1. Estratégia de Branches (Git Flow Adaptado)

Utilizaremos um modelo de branches baseado no Git Flow para gerenciar o desenvolvimento:

*   **`main`:**
    *   Representa o código de produção estável e pronto para implantação.
    *   **Ninguém deve fazer commit diretamente neste branch.**
    *   Merges para `main` virão apenas do branch `develop` (para releases) ou `hotfix` (para correções urgentes).
*   **`develop`:**
    *   Branch principal de desenvolvimento e integração.
    *   Contém o código mais recente com as funcionalidades concluídas e testadas.
    *   Novos branches `feature` e `bugfix` são criados a partir daqui.
    *   Merges para `develop` virão dos branches `feature` e `bugfix` através de Pull Requests.
*   **`feature/<nome-descritivo>`:**
    *   Criados a partir do `develop` para desenvolver novas funcionalidades.
    *   Exemplo: `feature/implementar-dashboard`, `feature/crud-contas-frontend`.
    *   Cada agente deve trabalhar em seu próprio branch `feature`.
    *   Ao concluir, um Pull Request (PR) deve ser aberto para mesclar de volta no `develop`.
*   **`bugfix/<nome-descritivo>`:**
    *   Criados a partir do `develop` para corrigir bugs não críticos encontrados no `develop`.
    *   Exemplo: `bugfix/corrigir-calculo-saldo`.
    *   Ao concluir, um Pull Request (PR) deve ser aberto para mesclar de volta no `develop`.
*   **`hotfix/<nome-descritivo>`:**
    *   Criados a partir do `main` para corrigir bugs críticos encontrados em produção.
    *   Exemplo: `hotfix/corrigir-falha-login`.
    *   Ao concluir, devem ser mesclados tanto no `main` quanto no `develop` através de Pull Requests.

## 2. Fluxo de Trabalho do Agente

1.  **Sincronizar:** Antes de iniciar qualquer trabalho, atualize seu branch `develop` local:
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Criar Branch:** Crie um novo branch `feature` ou `bugfix` a partir do `develop`:
    ```bash
    git checkout -b feature/minha-nova-funcionalidade develop
    # ou
    git checkout -b bugfix/meu-bug-fix develop
    ```
3.  **Desenvolver:** Implemente a funcionalidade ou corrija o bug no seu branch. Faça commits pequenos e descritivos.
    ```bash
    # Faça suas alterações...
    git add .
    git commit -m "feat: Adiciona funcionalidade X" 
    # ou
    git commit -m "fix: Corrige bug Y"
    ```
    *Use prefixos como `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:` nos seus commits (Convenção de Commits Convencionais).* 
4.  **Enviar:** Envie seu branch para o repositório remoto:
    ```bash
    git push origin feature/minha-nova-funcionalidade
    ```
5.  **Abrir Pull Request (PR):** No GitHub, abra um Pull Request do seu branch (`feature/...` ou `bugfix/...`) para o branch `develop`.
    *   Descreva claramente as alterações feitas no PR.
    *   Marque outros agentes ou o gerente de projeto para revisão, se necessário.
6.  **Revisão e Merge:** Após a aprovação do PR, ele será mesclado no `develop`.
7.  **Limpeza:** Após o merge, você pode deletar seu branch local e remoto (opcional, mas recomendado):
    ```bash
    git checkout develop
    git branch -d feature/minha-nova-funcionalidade
    git push origin --delete feature/minha-nova-funcionalidade
    ```

## 3. Comunicação e Coordenação

*   **Issues:** Utilize as Issues do GitHub para reportar bugs, solicitar novas funcionalidades e discutir tarefas.
*   **Tarefas:** O gerente de projeto (Dione) atribuirá tarefas específicas (vinculadas a Issues) aos agentes.
*   **Milestones:** Agruparemos Issues e PRs em Milestones para acompanhar o progresso de objetivos maiores (ex: "Implementação do Frontend v1", "API de Relatórios").
*   **Revisão de Código:** Todos os Pull Requests devem ser revisados por pelo menos um outro agente (ou pelo gerente) antes do merge para garantir a qualidade e consistência do código.

## 4. Padrões de Código

*   Siga os padrões de estilo definidos (ex: PEP 8 para Python).
*   Escreva código claro, comentado e, quando aplicável, com testes unitários.

## 5. Gerenciamento de Dependências

*   Todas as dependências Python devem ser adicionadas ao arquivo `requirements.txt`.
*   Execute `pip freeze > requirements.txt` antes de finalizar um branch `feature` ou `bugfix` se você adicionou novas dependências.

Ao seguir estas diretrizes, podemos garantir um desenvolvimento colaborativo eficiente e organizado para o projeto BudgetApp.
