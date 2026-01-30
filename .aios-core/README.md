# AIOS Framework - moodle-log-smart

Bem-vindo à estrutura AIOS (AI-Orchestrated System) para o projeto moodle-log-smart.

## Estrutura de Diretórios

```
.aios-core/
├── development/
│   ├── agents/          # Definições de agentes especializados
│   ├── tasks/           # Tasks executáveis para desenvolvimento
│   ├── templates/       # Templates para documentos e código
│   ├── workflows/       # Workflows multi-step (brownfield/greenfield)
│   ├── checklists/      # Checklists de validação
│   ├── data/            # Data files e knowledge bases
│   ├── utils/           # Utilities e scripts
│   └── scripts/         # Scripts auxiliares
├── logs/                # Logs de execução do framework
└── README.md           # Este arquivo
```

## Workflows Disponíveis

### Brownfield (Projeto Existente)
- **brownfield-fullstack** - Desenvolvimento full-stack (backend + frontend)
- **brownfield-service** - Desenvolvimento de novos serviços/APIs
- **brownfield-ui** - Desenvolvimento de componentes e páginas UI

### Greenfield (Novo Projeto)
- **greenfield-fullstack** - Novo projeto full-stack do zero
- **greenfield-service** - Novo serviço backend
- **greenfield-ui** - Nova aplicação frontend

## Como Usar

### Iniciar um Workflow

```bash
# CLI Claude Code
*workflow brownfield-fullstack
*workflow brownfield-service
*workflow brownfield-ui
```

### Executar uma Task

```bash
*task {task-name}
```

### Criar Novo Componente

```bash
*create agent {name}      # Novo agente
*create task {name}       # Nova task
*create workflow {name}   # Novo workflow
*create-doc {template}    # Novo documento
```

## Agentes Disponíveis

- **@aios-master** - Master orchestrator (framework operations)
- **@dev** - Developer especializado
- **@qa** - QA e testes
- **@architect** - Arquitetura e design
- **@pm** - Product manager
- **@po** - Product owner
- **@sm** - Scrum master
- **@analyst** - Análise e pesquisa
- **@data-engineer** - Dados
- **@ux-design-expert** - UX/UI design
- **@github-devops** - DevOps e Git

## Comandos Principais

```bash
*help                     # Ver todos os comandos
*guide                    # Guia completo
*kb                       # Toggle knowledge base mode
*status                   # Status atual do projeto
*task {name}              # Executar task
*workflow {name}          # Iniciar workflow
*create {type}            # Criar componente
*exit                     # Sair do modo agente
```

## Boas Práticas

1. **Work from Stories** - Sempre comece com uma story em `docs/stories/`
2. **Update Progress** - Mantenha o checklist atualizado
3. **Follow Standards** - Use conventional commits e padrões do projeto
4. **Test Everything** - Execute testes antes de marcar como completo
5. **Document Changes** - Atualize documentação relevante

## Proximos Passos

1. Instale o AIOS CLI (se não tiver): `npm install -g @aios/cli`
2. Comece com `*status` para ver o contexto atual
3. Inicie um workflow: `*workflow brownfield-fullstack`
4. Ou execute uma task: `*task {name}`

---

**AIOS Framework v1.0** | moodle-log-smart | 2025
