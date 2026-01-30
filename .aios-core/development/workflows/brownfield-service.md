# Workflow: Brownfield Service Development

**Type:** Workflow
**Status:** Active
**Version:** 1.0.0
**When to Use:** For developing backend services/APIs in an existing project

---

## Overview

Orquestra desenvolvimento de novos serviços, APIs ou camadas de backend em um projeto existente.

## Fases

### 1️⃣ Planejamento

- [ ] Ler story e acceptance criteria
- [ ] Desenhar arquitetura do serviço
- [ ] Identificar dependências
- [ ] Criar branch: `git checkout -b service/story-{id}`

### 2️⃣ Implementação

- [ ] Criar estrutura de pastas
- [ ] Implementar handlers/controllers
- [ ] Implementar lógica de negócio
- [ ] Adicionar validações
- [ ] Implementar tratamento de erros
- [ ] Adicionar logging

### 3️⃣ Testes

- [ ] Escrever testes unitários
- [ ] Escrever testes de integração
- [ ] Testar edge cases
- [ ] Validar tipos com `npm run typecheck`
- [ ] Rodar linter: `npm run lint`

### 4️⃣ Documentação

- [ ] Documentar endpoints da API
- [ ] Adicionar exemplos de uso
- [ ] Documentar modelos de dados
- [ ] Atualizar README se necessário

### 5️⃣ Commit & PR

- [ ] Commit com conventional commits
- [ ] Push e criar PR
- [ ] Descrever mudanças claramente

---

**Próximos:** Review → Merge → Deploy (se aplicável)
