# MoodleLogSmart - User Stories

Este diretório contém todas as **user stories** detalhadas do projeto, organizadas por Epic.

---

## 📊 Stories Overview

### Epic 01: Backend Core + Auto-Detection (Sprint 1)

| Story ID | Nome | Estimate | Status | File |
|----------|------|----------|--------|------|
| **STORY-1.1** | Auto-Detection de Encoding e Delimiter | 1 dia | ✅ Completed | [📄](./STORY-1.1-Auto-Detection-CSV-Format.md) |
| **STORY-1.2** | Auto-Mapeamento de Colunas Moodle | 1 dia | ✅ Completed | [📄](./STORY-1.2-Auto-Mapping-Moodle-Columns.md) |
| **STORY-1.3** | Auto-Detection de Formato de Timestamp | 1 dia | ✅ Completed | [📄](./STORY-1.3-Auto-Detection-Timestamp-Format.md) |
| **STORY-1.4** | Data Cleaning com Configuração Default | 1 dia | ✅ Completed | [📄](./STORY-1.4-to-1.7-Remaining-Epic01.md#story-14) |
| **STORY-1.5** | Rule Engine + 13 Regras Bloom | 2 dias | ✅ Completed | [📄](./STORY-1.4-to-1.7-Remaining-Epic01.md#story-15) |
| **STORY-1.6** | Export Multi-Formato (CSV + XES) | 1 dia | ✅ Completed | [📄](./STORY-1.4-to-1.7-Remaining-Epic01.md#story-16) |
| **STORY-1.7** | ZIP Packager | 0.5 dia | ✅ Completed | [📄](./STORY-1.4-to-1.7-Remaining-Epic01.md#story-17) |

**Total Sprint 1**: 7.5 dias → **7 story points** (arredondado)

---

## 📋 Story Structure

Cada user story detalhada contém:

### Seções Principais
1. **Story Overview**
   - User story (As a / I want / So that)
   - Business context
   - Value proposition

2. **Acceptance Criteria**
   - 4-6 AC detalhados (Given/When/Then)
   - Validation checklist

3. **Technical Implementation**
   - Component architecture
   - Code implementation completo
   - Dependencies listadas

4. **Testing Requirements**
   - Unit tests (6-13 test cases)
   - Integration tests
   - Coverage targets (>80%)

5. **Definition of Done**
   - Code complete checklist
   - Testing complete checklist
   - Quality gates

6. **Dependencies**
   - Blocked by
   - Blocks
   - Related stories

7. **Handoff to Developer**
   - Getting started commands
   - Key files to modify
   - Success criteria summary

---

## 🎯 Sprint 1 Schedule

### Week 1: Epic 01 - Backend Core

```
┌─────────────────────────────────────────────────────┐
│  Day 1: Story 1.1 (CSVDetector)                     │
├─────────────────────────────────────────────────────┤
│  Day 2: Story 1.2 (ColumnMapper)                    │
│         Story 1.3 (TimestampDetector)                │
├─────────────────────────────────────────────────────┤
│  Day 3: Story 1.4 (Data Cleaning)                   │
├─────────────────────────────────────────────────────┤
│  Day 4: Story 1.5 (Rule Engine + Bloom Rules)       │
├─────────────────────────────────────────────────────┤
│  Day 5: Story 1.6 (Export CSV/XES)                  │
│         Story 1.7 (ZIP Packager)                     │
│         Integration Testing                          │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Story Checklist Template

Use esta checklist para validar cada story antes de marcar como "Done":

### Code Complete
- [ ] Componente implementado
- [ ] Error handling robusto
- [ ] Type hints completos
- [ ] Docstrings em todos os métodos

### Testing Complete
- [ ] Unit tests escritos (>80% coverage)
- [ ] Integration tests escritos
- [ ] Todos os testes passando
- [ ] Coverage target atingido

### Documentation Complete
- [ ] Docstrings atualizados
- [ ] Examples no código
- [ ] README atualizado (se aplicável)

### Quality Gates
- [ ] Code review aprovado
- [ ] No linting errors (ruff)
- [ ] Type checking passa (mypy)
- [ ] Tests passam em CI
- [ ] No security issues

---

## 🚀 How to Use This Documentation

### Para Desenvolvedores (@dev)
1. Leia a story completa antes de começar
2. Siga as instruções de "Handoff to Developer"
3. Use o código de implementação como referência
4. Implemente todos os testes listados
5. Valide contra os Acceptance Criteria
6. Use Definition of Done como checklist final

### Para Scrum Master (@sm)
1. Use stories para daily standup tracking
2. Monitore blockers (Dependencies section)
3. Valide completion com DoD checklist
4. Coordene handoffs entre stories

### Para QA (@qa)
1. Use Acceptance Criteria para test cases
2. Valide contra Testing Requirements
3. Execute integration tests
4. Confirme coverage targets

### Para Product Manager (@pm)
1. Valide business value está claro
2. Confirme AC estão completos
3. Aprove story antes de iniciar sprint

---

## 📈 Progress Tracking

### Sprint 1 Progress

```
Story 1.1: [██████████] 100% (✅ Completed)
Story 1.2: [██████████] 100% (✅ Completed)
Story 1.3: [██████████] 100% (✅ Completed)
Story 1.4: [██████████] 100% (✅ Completed)
Story 1.5: [██████████] 100% (✅ Completed)
Story 1.6: [██████████] 100% (✅ Completed)
Story 1.7: [██████████] 100% (✅ Completed)
────────────────────────────────────────
Total: 7/7 stories (100%) | 7.5/7.5 days
```

### Velocity Metrics
- **Target velocity**: 1.4 stories/day (7 stories / 5 days)
- **Story points**: 7.5 days total
- **Coverage target**: >50% (goal: 60%)

---

## 🔗 Related Documents

- **PRD**: `../PRD-MoodleLogSmart.md`
- **Epics**: `../epics/`
- **Plan**: `../../.claude/plans/indexed-wibbling-sky.md`
- **Architecture**: (To be created by @architect)

---

## 📝 Story Creation Guidelines

### Story Naming Convention
```
STORY-{Epic}.{Sequence}-{Brief-Description}.md
```
Examples:
- `STORY-1.1-Auto-Detection-CSV-Format.md`
- `STORY-2.3-Endpoint-Download.md`

### Story Size Guidelines
- **Small**: 0.5-1 dia (simples, bem definida)
- **Medium**: 1-2 dias (complexidade média)
- **Large**: 2-3 dias (complexa, múltiplos componentes)
- **XL**: >3 dias (quebrar em stories menores!)

### Acceptance Criteria Quality
- Use formato Given/When/Then
- Seja específico e testável
- Inclua validation checklist
- 4-6 AC por story (ideal)

---

**Document Owner**: @sm (River)
**Last Updated**: 2026-01-28
**Version**: 1.0

*"Removendo obstáculos 🌊"*