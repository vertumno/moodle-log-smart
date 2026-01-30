# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o **MoodleLogSmart**! Este documento fornece diretrizes e instruções para colaboradores.

## 📋 Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Setup Local](#setup-local)
4. [Padrões de Código](#padrões-de-código)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Testes e Qualidade](#testes-e-qualidade)

---

## 📖 Código de Conduta

### Nossos Compromissos

Estamos comprometidos em proporcionar um ambiente acolhedor e inclusivo para todos.

**Esperamos de você:**
- Usar linguagem respeitosa e acolhedora
- Aceitar críticas construtivas
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros colaboradores

**Não toleramos:**
- Assédio de qualquer tipo
- Discriminação por raça, gênero, orientação sexual, religião
- Ataques pessoais ou insultos
- Spam ou conteúdo malicioso

Comportamentos inaceitáveis podem resultar em exclusão do projeto.

---

## 🎯 Como Contribuir

### Tipos de Contribuição

#### 1. **Bug Reports** 🐛
Se encontrar um bug:
- Verifique se já foi reportado em [Issues](https://github.com/vertumno/moodle-log-smart/issues)
- Se não, abra uma nova issue usando o template `bug_report.md`
- Inclua: descrição, passos para reproduzir, resultado esperado, resultado atual
- Indique seu environment (OS, Python/Node version, etc.)

#### 2. **Feature Requests** ✨
Quer sugerir uma nova feature?
- Use o template `feature_request.md` em Issues
- Explique o caso de uso e por quê seria útil
- Forneça exemplos de como funcionaria
- Aguarde feedback antes de começar o desenvolvimento

#### 3. **Documentação** 📚
Melhorias em documentação são sempre bem-vindas:
- Correções de typos
- Exemplos mais claros
- Tradução de docs
- Guias novos

#### 4. **Code** 💻
Quer contribuir com código?
- Comece com issues marcadas como `good-first-issue`
- Ou escolha uma issue em `help-wanted`
- Comunique sua intenção comentando na issue
- Siga as instruções de setup local abaixo

---

## 🛠️ Setup Local

### Pré-requisitos

```bash
# Verificar versões
python --version        # 3.11+
node --version         # 18+
docker --version       # 20.10+
git --version          # 2.30+
```

### Clonar o Repositório

```bash
# Fork no GitHub (botão Fork)
# Clone seu fork
git clone https://github.com/seu-usuario/moodle-log-smart.git
cd moodle-log-smart

# Adicione o upstream como remote
git remote add upstream https://github.com/vertumno/moodle-log-smart.git
```

### Backend Setup

```bash
cd backend

# Instale dependências via Poetry
poetry install

# Crie arquivo .env
cp .env.example .env

# Atualize .env com valores de desenvolvimento
# (geralmente defaults funcionam)

# Execute migrations (se aplicável)
# poetry run alembic upgrade head

# Inicie servidor de desenvolvimento
poetry run uvicorn src.moodlelogsmart.main:app --reload --host 0.0.0.0
```

**Verificar**: Acesse http://localhost:8000/docs para ver Swagger docs

### Frontend Setup

```bash
cd frontend

# Instale dependências
npm install
# ou
yarn install

# Crie arquivo .env
cp .env.example .env

# Atualize .env com API_URL apontando para backend local
# API_URL=http://localhost:8000

# Inicie servidor de desenvolvimento
npm run dev
```

**Verificar**: Acesse http://localhost:5173 (ou porta exibida)

### Com Docker Compose

```bash
# Da raiz do projeto
docker-compose up

# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

---

## 📝 Padrões de Código

### Python (Backend)

#### Style Guide
- Follow **PEP 8** standards
- Use **Black** para formatação automática
- Use **isort** para imports
- Máximo 100 caracteres por linha

```bash
# Formatação automática
poetry run black src/ tests/
poetry run isort src/ tests/

# Linting
poetry run flake8 src/ tests/
poetry run mypy src/
```

#### Exemplos de Código Bom

```python
# ✅ Bom: Claro, bem tipado, bem documentado
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

class LogEntry(BaseModel):
    """Modelo para entrada de log do Moodle."""
    user_id: int
    action: str
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "action": "view",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

def process_entry(entry: LogEntry) -> dict:
    """
    Processa uma entrada de log.

    Args:
        entry: Entrada de log a ser processada

    Returns:
        Dicionário com resultado do processamento

    Raises:
        ValueError: Se entrada for inválida
    """
    if not entry.user_id:
        raise ValueError("user_id é obrigatório")

    result = {
        "processed": True,
        "user_id": entry.user_id,
        "action": entry.action.lower()
    }
    return result
```

```python
# ❌ Ruim: Sem tipagem, sem documentação, magic numbers
def process(x):
    if x:
        return {"ok": True, "data": x.lower()}
    return {"ok": False, "err": "nope"}
```

### TypeScript/React (Frontend)

#### Style Guide
- Siga **ESLint** config do projeto
- Use **Prettier** para formatação
- Use **TypeScript** em vez de JavaScript
- Componentes como `PascalCase`, funções como `camelCase`

```bash
# Formatação automática
npm run format

# Linting
npm run lint

# Type checking
npm run typecheck
```

#### Exemplos de Código Bom

```typescript
// ✅ Bom: Tipado, bem documentado, componente limpo
import React, { useState, useCallback } from 'react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  maxSize?: number; // em bytes
}

/**
 * Componente para upload de arquivos via drag-and-drop
 * @param props - Propriedades do componente
 * @returns React component
 */
export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelect,
  disabled = false,
  maxSize = 50 * 1024 * 1024, // 50MB
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.size <= maxSize && file.name.endsWith('.csv')) {
      onFileSelect(file);
    }
  }, [maxSize, onFileSelect]);

  return (
    <div
      className={`upload-zone ${isDragging ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <p>Arraste arquivos aqui ou clique para selecionar</p>
    </div>
  );
};
```

```typescript
// ❌ Ruim: Sem tipagem clara, side effects, props magic
const UploadZone = (props) => {
  const [drag, setDrag] = useState(false);

  return (
    <div onDragOver={() => setDrag(true)} onDrop={() => {
      props.fn(event.dataTransfer.files[0]);
    }}>
      drag here
    </div>
  );
};
```

### Commits

Use **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Nova feature
- `fix`: Correção de bug
- `docs`: Mudanças em documentação
- `style`: Mudanças que não afetam lógica (formatação, whitespace)
- `refactor`: Refatoração sem mudança funcional
- `perf`: Melhoria de performance
- `test`: Adição ou atualização de testes
- `chore`: Mudanças de build, dependencies, etc.

**Exemplos:**
```bash
git commit -m "feat(api): adicione endpoint de status com WebSocket"
git commit -m "fix(auto-detect): corrija detecção de timestamp UTC"
git commit -m "docs(deployment): atualize guia de produção para Render"
git commit -m "test(bloom): adicione testes para nível 5 da taxonomia"
```

---

## 🔄 Processo de Pull Request

### Antes de Começar

1. **Abra uma issue** descrevendo o que vai fazer
2. **Aguarde feedback** antes de investir tempo
3. **Assign-se** à issue para indicar que você vai fazer
4. **Crie um branch** com nome descritivo:
   ```bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/descricao-do-bug
   ```

### Desenvolvendo

1. **Make commits** atômicos e bem descritos
2. **Teste frequentemente** (veja seção Testes)
3. **Atualize docs** se necessário
4. **Keep branch atualizado** com upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   # ou se preferir merge
   git merge upstream/main
   ```

### Enviando PR

1. **Push seu branch**:
   ```bash
   git push origin feature/nome-da-feature
   ```

2. **Abra Pull Request no GitHub**:
   - Use template fornecido
   - Link a issue relacionada: `Closes #123`
   - Descreva as mudanças claramente
   - Indique se há mudanças breaking

3. **Preencha a checklist de PR**:
   ```markdown
   - [ ] Testes adicionados/atualizados
   - [ ] Docs atualizadas
   - [ ] Sem warnings de linting
   - [ ] Commits bem descritos
   - [ ] Sem mudanças não relacionadas
   ```

4. **Responda a reviews**:
   - Agradeca pelo feedback
   - Discuta construtivamente
   - Faça mudanças conforme solicitado
   - Push novos commits (não faça rebase)

### Merge

- Rebase and merge é preferido para manter histórico linear
- Squash apenas se houver muitos commits pequenos
- Delete branch após merge

---

## 🧪 Testes e Qualidade

### Backend Tests

```bash
cd backend

# Executar todos os testes
poetry run pytest tests/

# Com cobertura
poetry run pytest tests/ --cov=src --cov-report=html

# Testes específicos
poetry run pytest tests/test_auto_detect.py
poetry run pytest tests/test_auto_detect.py::test_encoding_detection
```

### Frontend Tests

```bash
cd frontend

# Executar todos os testes
npm test

# Watch mode
npm test -- --watch

# Com cobertura
npm test -- --coverage
```

### Tipos e Linting

```bash
# Backend
cd backend
poetry run black src/ tests/ --check
poetry run isort src/ tests/ --check
poetry run flake8 src/ tests/
poetry run mypy src/

# Frontend
cd frontend
npm run lint
npm run typecheck
```

### Antes de Fazer Commit

Sempre rode:

```bash
# Backend
cd backend
poetry run pytest tests/ -v
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run flake8 src/ tests/
poetry run mypy src/

# Frontend
cd frontend
npm test
npm run lint
npm run typecheck
```

### Cobertura Mínima Esperada

- **Backend**: >85% (pull requests) / >95% (main)
- **Frontend**: >70% (pull requests) / >85% (main)

Se cobertura cair, será solicitado adicionar testes.

---

## 📚 Recursos Úteis

### Documentação do Projeto
- [README.md](./README.md) - Overview do projeto
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Guia de deployment
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Design do sistema
- [docs/API.md](./docs/API.md) - Documentação da API

### Tecnologias
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)

### Tools
- [Poetry](https://python-poetry.org/docs/)
- [Vite](https://vitejs.dev/)
- [Docker](https://docs.docker.com/)

---

## ❓ Dúvidas?

- 📖 Veja as [FAQs](./docs/FAQ.md)
- 💬 Abra uma [Discussion](https://github.com/vertumno/moodle-log-smart/discussions)
- 🐛 Reporte um [Issue](https://github.com/vertumno/moodle-log-smart/issues)
- 📧 Entre em contato: elton@example.com

---

## 🙏 Obrigado!

Cada contribuição, por menor que seja, é valiosa. Obrigado por ajudar a melhorar o MoodleLogSmart!

---

**Última Atualização**: 2026-01-30

**Junte-se a nós em construir ferramentas open-source para educação!** 🎓
