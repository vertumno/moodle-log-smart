# Workflow: Brownfield Full Stack Development

**Type:** Workflow
**Status:** Active
**Version:** 1.0.0
**When to Use:** For developing complete features in an existing full-stack project (frontend + backend)

---

## Overview

Este workflow orquestra o desenvolvimento completo de features em um projeto fullstack brownfield (projeto existente). Coordena trabalho entre frontend, backend, testes e documentação.

## Prerequisitos

- Projeto existente configurado (backend + frontend)
- Ambiente de desenvolvimento funcional
- Repositório Git configurado
- Story/Task descrita em `docs/stories/`

## Fases

### 1️⃣ Planejamento & Setup

**Inputs:**
- Story ID e descrição
- Acceptance criteria
- Componentes afetados

**Tasks:**
- [ ] Ler story completa em `docs/stories/`
- [ ] Verificar acceptance criteria
- [ ] Identificar arquivos a modificar
- [ ] Criar branch feature (`git checkout -b feature/story-{id}`)

**Outputs:**
- Branch criado
- Contexto claro do trabalho

---

### 2️⃣ Desenvolvimento Backend

**Conditions:** Se há alterações de API/lógica

**Tasks:**
- [ ] Modificar/criar endpoints da API
- [ ] Atualizar modelos de dados
- [ ] Implementar lógica de negócio
- [ ] Adicionar validações
- [ ] Implementar error handling
- [ ] Atualizar tests de backend

**Commands:**
```bash
npm run dev              # Iniciar servidor
npm test               # Rodar testes
npm run typecheck     # Validar tipos
```

**Outputs:**
- Backend funcional
- Testes passando
- Tipos validados

---

### 3️⃣ Desenvolvimento Frontend

**Conditions:** Se há alterações de UI/componentes

**Tasks:**
- [ ] Criar/modificar componentes
- [ ] Integrar com API
- [ ] Implementar lógica de estado
- [ ] Adicionar validações UI
- [ ] Implementar error handling
- [ ] Adicionar testes de componentes

**Commands:**
```bash
npm run dev            # Dev server
npm test              # Testes
npm run typecheck    # Type checking
```

**Outputs:**
- Componentes funcionais
- Integração com API completa
- Testes cobrindo comportamento

---

### 4️⃣ Testes Integrados

**Tasks:**
- [ ] Testar fluxo completo (backend + frontend)
- [ ] Verificar validações end-to-end
- [ ] Testar error scenarios
- [ ] Validar performance
- [ ] Cross-browser testing (se applicable)

**Commands:**
```bash
npm run lint          # Code style
npm run typecheck    # Type safety
npm test             # Testes unitários
npm run e2e          # E2E tests (se configurado)
```

---

### 5️⃣ Documentação

**Tasks:**
- [ ] Atualizar README (se necessário)
- [ ] Documentar novos endpoints (em API docs)
- [ ] Adicionar exemplos de uso (se aplicável)
- [ ] Atualizar story com checklist completo

**Outputs:**
- Documentação sincronizada
- Story marcada como pronta

---

### 6️⃣ Review & Commit

**Tasks:**
- [ ] Revisar todas as mudanças
- [ ] Executar: `npm run lint && npm run typecheck && npm test`
- [ ] Garantir que todos os testes passam
- [ ] Criar commit(s) com conventional commits

**Commit Format:**
```
feat: [story-id] descrição da feature

Descrição detalhada do que foi implementado

Acceptance criteria:
- [x] Critério 1
- [x] Critério 2

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

### 7️⃣ Pull Request

**Tasks:**
- [ ] Push para remote: `git push origin feature/story-{id}`
- [ ] Criar PR via GitHub CLI: `gh pr create`
- [ ] Descrever mudanças de forma clara
- [ ] Referenciar story/issue

**PR Template:**
```markdown
## Summary
[Descrição breve do que foi implementado]

## Changes
- [x] Backend: [o que mudou]
- [x] Frontend: [o que mudou]
- [x] Tests: [testes adicionados]

## Acceptance Criteria
- [x] Critério 1
- [x] Critério 2

## Testing Done
[Descrever testes executados]

## Screenshots (if UI changes)
[Adicionar screenshots se houver mudanças visuais]
```

---

## Dicas

✅ **Fazer:**
- Commit frequente e atômico
- Escrever testes enquanto desenvolve
- Validar types durante o desenvolvimento
- Revisar antes de fazer commit

❌ **Evitar:**
- Commits gigantes com múltiplas features
- Código sem testes
- Ignorar erros de type
- Push direto sem PR

---

## Próximos Passos Após Conclusão

1. Aguardar review do PR
2. Fazer ajustes se solicitado
3. Merge após aprovação
4. Delete branch feature
5. Atualizar story com data de conclusão
6. Festejar! 🎉

---

**Para iniciar esta workflow:** `*workflow brownfield-fullstack`
**Para mais ajuda:** `*help` ou `*guide`
