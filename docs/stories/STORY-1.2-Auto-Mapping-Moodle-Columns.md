# User Story 1.2: Auto-Mapeamento de Colunas Moodle

**Story ID**: STORY-1.2
**Epic**: EPIC-01 - Backend Core + Auto-Detection
**Product**: MoodleLogSmart
**Sprint**: Sprint 1 (Day 2)
**Priority**: P0 (Must-Have)
**Status**: Not Started
**Estimate**: 1 dia
**Assigned To**: @dev

---

## 📋 Story Overview

### User Story
```
As a usuário
I want que sistema identifique colunas automaticamente
So that não preciso mapear "Time" vs "Timestamp" manualmente
```

### Business Context
Diferentes versões e instalações do Moodle usam nomes de colunas variados. Por exemplo:
- "Time" vs "Timestamp" vs "Date/Time"
- "User full name" vs "Full name" vs "Name"
- "Event name" vs "Event" vs "Action"

O sistema deve usar **fuzzy matching** para mapear essas variações automaticamente para um schema interno padronizado.

### Value Proposition
- **Compatibilidade universal**: Funciona com Moodle 3.x, 4.x e custom installations
- **Zero configuração**: Usuário não precisa mapear colunas manualmente
- **Resiliente**: Tolera pequenas variações de nomenclatura

---

## ✅ Acceptance Criteria

### AC1: Mapeia Coluna de Timestamp
**Given** um CSV com coluna "Time", "Timestamp" ou "Date/Time"
**When** o sistema mapeia colunas
**Then** identifica corretamente como coluna de timestamp

**Validation**:
- "Time" → time
- "Timestamp" → time
- "Date/Time" → time
- "Event time" → time

### AC2: Mapeia Coluna de Nome de Usuário
**Given** um CSV com coluna de nome de usuário
**When** o sistema mapeia colunas
**Then** identifica corretamente como user_full_name

**Validation**:
- "User full name" → user_full_name
- "Full name" → user_full_name
- "Name" → user_full_name
- "User name" → user_full_name

### AC3: Mapeia Coluna de Nome de Evento
**Given** um CSV com coluna de evento
**When** o sistema mapeia colunas
**Then** identifica corretamente como event_name

**Validation**:
- "Event name" → event_name
- "Event" → event_name
- "Action" → event_name

### AC4: Mapeia Outras Colunas Essenciais
**Given** um CSV com colunas "Component", "Event context", "Description"
**When** o sistema mapeia todas as colunas
**Then** mapeia corretamente para schema interno

**Validation**:
- "Component" / "Module" → component
- "Event context" / "Context" → event_context
- "Description" / "Details" / "Info" → description

### AC5: Fuzzy Matching com Threshold
**Given** uma coluna com nome levemente diferente ("User Name" vs "User full name")
**When** o sistema aplica fuzzy matching
**Then** identifica match se similaridade >80%

**Validation**:
- "User Name" match com "User full name" (similaridade >80%)
- "Usre Name" (typo) match com "User full name"
- "Random Column" NÃO match (similaridade <80%)

---

## 🏗️ Technical Implementation

### Component: ColumnMapper

**File**: `backend/src/moodlelogsmart/core/auto_detect/column_mapper.py`

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from rapidfuzz import fuzz
import pandas as pd

@dataclass
class ColumnMapping:
    """Mapeamento de colunas CSV para schema interno"""
    time: str
    user_full_name: str
    event_name: str
    component: str
    event_context: str
    description: str
    # Campos opcionais
    affected_user: Optional[str] = None
    origin: Optional[str] = None
    ip_address: Optional[str] = None

class ColumnMapper:
    """Mapeia colunas do Moodle para schema interno padronizado"""

    # Dicionário de aliases conhecidos para cada coluna
    COLUMN_ALIASES = {
        'time': [
            'Time',
            'Timestamp',
            'Date/Time',
            'Event time',
            'DateTime',
            'Date and time'
        ],
        'user_full_name': [
            'User full name',
            'Full name',
            'User name',
            'Name',
            'Username',
            'User'
        ],
        'event_name': [
            'Event name',
            'Event',
            'Action',
            'Event type',
            'Activity'
        ],
        'component': [
            'Component',
            'Event component',
            'Module',
            'Component name'
        ],
        'event_context': [
            'Event context',
            'Context',
            'Course',
            'Resource',
            'Activity context'
        ],
        'description': [
            'Description',
            'Details',
            'Info',
            'Information',
            'Event description'
        ],
        'affected_user': [
            'Affected user',
            'Related user',
            'Target user'
        ],
        'origin': [
            'Origin',
            'Source',
            'Event origin'
        ],
        'ip_address': [
            'IP address',
            'IP',
            'User IP',
            'Client IP'
        ]
    }

    FUZZY_THRESHOLD = 80  # Similaridade mínima para match

    def map_columns(self, df: pd.DataFrame) -> ColumnMapping:
        """
        Mapeia colunas do DataFrame para schema interno

        Args:
            df: DataFrame com colunas do Moodle

        Returns:
            ColumnMapping com nomes das colunas mapeadas

        Raises:
            ValueError: Se colunas essenciais não forem encontradas
        """
        csv_columns = df.columns.tolist()
        mapping = {}

        # Mapeia cada coluna do schema interno
        for internal_name, aliases in self.COLUMN_ALIASES.items():
            matched_column = self._find_best_match(csv_columns, aliases)

            # Colunas obrigatórias
            if internal_name in ['time', 'user_full_name', 'event_name',
                                  'component', 'event_context', 'description']:
                if matched_column is None:
                    raise ValueError(
                        f"Coluna obrigatória não encontrada: {internal_name}. "
                        f"Esperado um dos: {', '.join(aliases)}"
                    )

            mapping[internal_name] = matched_column

        return ColumnMapping(**mapping)

    def _find_best_match(
        self,
        csv_columns: List[str],
        aliases: List[str]
    ) -> Optional[str]:
        """
        Encontra melhor match entre colunas CSV e aliases conhecidos

        Args:
            csv_columns: Lista de colunas do CSV
            aliases: Lista de aliases conhecidos para uma coluna

        Returns:
            Nome da coluna CSV que melhor match, ou None
        """
        # Primeiro tenta match exato (case-insensitive)
        for alias in aliases:
            for csv_col in csv_columns:
                if csv_col.lower() == alias.lower():
                    return csv_col

        # Se não encontrou match exato, usa fuzzy matching
        best_match = None
        best_score = 0

        for alias in aliases:
            for csv_col in csv_columns:
                # Calcula similaridade (0-100)
                score = fuzz.ratio(csv_col.lower(), alias.lower())

                if score > best_score and score >= self.FUZZY_THRESHOLD:
                    best_score = score
                    best_match = csv_col

        return best_match

    def rename_dataframe(
        self,
        df: pd.DataFrame,
        mapping: ColumnMapping
    ) -> pd.DataFrame:
        """
        Renomeia colunas do DataFrame para schema interno

        Args:
            df: DataFrame original
            mapping: Mapeamento de colunas

        Returns:
            DataFrame com colunas renomeadas
        """
        rename_dict = {}

        for internal_name, csv_column in mapping.__dict__.items():
            if csv_column is not None:
                rename_dict[csv_column] = internal_name

        return df.rename(columns=rename_dict)
```

### Dependencies
- **pandas**: DataFrame manipulation
- **rapidfuzz**: Fuzzy string matching (mais rápido que fuzzywuzzy)

### Example Usage
```python
# Exemplo de uso
mapper = ColumnMapper()

# CSV tem colunas: "Time", "User full name", "Event name", etc.
df = pd.read_csv("moodle_log.csv")

# Mapeia colunas
mapping = mapper.map_columns(df)
print(f"Timestamp column: {mapping.time}")  # "Time"
print(f"User column: {mapping.user_full_name}")  # "User full name"

# Renomeia DataFrame
df_renamed = mapper.rename_dataframe(df, mapping)
# Agora tem colunas: "time", "user_full_name", "event_name", etc.
```

---

## 🧪 Testing Requirements

### Unit Tests

**File**: `backend/tests/unit/test_column_mapper.py`

```python
import pytest
import pandas as pd
from moodlelogsmart.core.auto_detect.column_mapper import (
    ColumnMapper,
    ColumnMapping
)

class TestColumnMapper:

    @pytest.fixture
    def mapper(self):
        return ColumnMapper()

    def test_exact_match_standard_columns(self, mapper):
        """Test exact match with standard Moodle column names"""
        # Arrange
        df = pd.DataFrame(columns=[
            'Time',
            'User full name',
            'Event name',
            'Component',
            'Event context',
            'Description'
        ])

        # Act
        mapping = mapper.map_columns(df)

        # Assert
        assert mapping.time == 'Time'
        assert mapping.user_full_name == 'User full name'
        assert mapping.event_name == 'Event name'
        assert mapping.component == 'Component'
        assert mapping.event_context == 'Event context'
        assert mapping.description == 'Description'

    def test_alias_variations(self, mapper):
        """Test mapping with column name variations"""
        df = pd.DataFrame(columns=[
            'Timestamp',           # alias de Time
            'Full name',           # alias de User full name
            'Action',              # alias de Event name
            'Module',              # alias de Component
            'Context',             # alias de Event context
            'Details'              # alias de Description
        ])

        mapping = mapper.map_columns(df)

        assert mapping.time == 'Timestamp'
        assert mapping.user_full_name == 'Full name'
        assert mapping.event_name == 'Action'
        assert mapping.component == 'Module'
        assert mapping.event_context == 'Context'
        assert mapping.description == 'Details'

    def test_fuzzy_matching(self, mapper):
        """Test fuzzy matching with slight variations"""
        df = pd.DataFrame(columns=[
            'Time',
            'User Name',           # fuzzy match "User full name"
            'Event name',
            'Component',
            'Event context',
            'Description'
        ])

        mapping = mapper.map_columns(df)

        # "User Name" deve match com "User full name" via fuzzy
        assert mapping.user_full_name in ['User Name', 'User name']

    def test_case_insensitive_matching(self, mapper):
        """Test case-insensitive exact matching"""
        df = pd.DataFrame(columns=[
            'time',                # lowercase
            'USER FULL NAME',      # uppercase
            'Event Name',          # mixed case
            'component',
            'event context',
            'description'
        ])

        mapping = mapper.map_columns(df)

        assert mapping.time == 'time'
        assert mapping.user_full_name == 'USER FULL NAME'
        assert mapping.event_name == 'Event Name'

    def test_missing_required_column_raises_error(self, mapper):
        """Test missing required column raises ValueError"""
        df = pd.DataFrame(columns=[
            'Time',
            'User full name',
            # MISSING: Event name
            'Component',
            'Event context',
            'Description'
        ])

        with pytest.raises(ValueError, match="Event name"):
            mapper.map_columns(df)

    def test_optional_columns(self, mapper):
        """Test optional columns are None if not present"""
        df = pd.DataFrame(columns=[
            'Time',
            'User full name',
            'Event name',
            'Component',
            'Event context',
            'Description'
            # NO optional columns
        ])

        mapping = mapper.map_columns(df)

        assert mapping.affected_user is None
        assert mapping.origin is None
        assert mapping.ip_address is None

    def test_rename_dataframe(self, mapper):
        """Test renaming DataFrame columns"""
        df = pd.DataFrame({
            'Time': ['2024-01-01'],
            'User full name': ['John Doe'],
            'Event name': ['Login'],
            'Component': ['System'],
            'Event context': ['Course 1'],
            'Description': ['User logged in']
        })

        mapping = mapper.map_columns(df)
        df_renamed = mapper.rename_dataframe(df, mapping)

        # Verifica colunas foram renomeadas
        assert 'time' in df_renamed.columns
        assert 'user_full_name' in df_renamed.columns
        assert 'event_name' in df_renamed.columns
        # Colunas antigas removidas
        assert 'Time' not in df_renamed.columns
        assert 'User full name' not in df_renamed.columns

    def test_fuzzy_threshold(self, mapper):
        """Test fuzzy matching respects threshold"""
        df = pd.DataFrame(columns=[
            'Time',
            'UserName',            # Sem espaço, <80% similaridade?
            'Event name',
            'Component',
            'Event context',
            'Description'
        ])

        # Deve ainda fazer match devido a fuzzy
        mapping = mapper.map_columns(df)
        assert mapping.user_full_name is not None
```

### Integration Tests

**File**: `backend/tests/integration/test_column_mapper_integration.py`

```python
def test_real_moodle_csv_columns(mapper):
    """Test with real Moodle CSV export"""
    df = pd.read_csv("tests/fixtures/moodle_log_sample.csv")

    mapping = mapper.map_columns(df)

    # Verifica todas as colunas obrigatórias foram mapeadas
    assert mapping.time is not None
    assert mapping.user_full_name is not None
    assert mapping.event_name is not None
    assert mapping.component is not None
    assert mapping.event_context is not None
    assert mapping.description is not None

    # Renomeia e valida
    df_renamed = mapper.rename_dataframe(df, mapping)
    assert 'time' in df_renamed.columns
    assert 'user_full_name' in df_renamed.columns
```

### Test Coverage Target
- **Minimum**: 85% line coverage
- **Target**: 95% line coverage
- **Critical Paths**: 100% coverage (missing columns error handling)

---

## 📊 Definition of Done

### Code Complete
- ✅ `ColumnMapper` class implementada
- ✅ Fuzzy matching implementado (rapidfuzz)
- ✅ Rename DataFrame method
- ✅ Error handling para colunas faltando
- ✅ Type hints completos

### Testing Complete
- ✅ Unit tests escritos (8+ test cases)
- ✅ Integration test com CSV real
- ✅ Todos os testes passando
- ✅ Coverage >85%

### Documentation Complete
- ✅ Docstrings em todos os métodos
- ✅ Examples no código
- ✅ COLUMN_ALIASES documentado

### Quality Gates
- ✅ Code review aprovado
- ✅ No linting errors (ruff)
- ✅ Type checking passa (mypy)
- ✅ Tests passam em CI

---

## 🔗 Dependencies

### Blocked By
- **Story 1.1**: Precisa do CSV detectado e parseado

### Blocks
- **Story 1.4**: Data Cleaning precisa de colunas mapeadas
- **Story 1.5**: Rule Engine precisa de colunas padronizadas

### Related Stories
- **Story 1.3**: Timestamp detection usará coluna mapeada `time`

---

## 📝 Notes & Clarifications

### Design Decisions
1. **rapidfuzz vs fuzzywuzzy**: rapidfuzz é 5-10x mais rápido
2. **Threshold 80%**: Balanceamento entre flexibilidade e precisão
3. **Case-insensitive**: Moodle pode exportar com diferentes cases
4. **Exact match first**: Prioriza exact match antes de fuzzy (performance)

### Edge Cases Handled
- Colunas com case diferente ("time" vs "Time")
- Typos leves ("Usre Name")
- Variações de nomenclatura (timestamps: "Time", "Timestamp", "Date/Time")
- Colunas opcionais ausentes (affected_user, origin, ip_address)

### Known Limitations
- Não detecta colunas customizadas (não-Moodle)
- Fuzzy matching pode dar false positive em edge cases raros
- Assume pelo menos 6 colunas obrigatórias

### Future Enhancements (Out of Scope)
- Machine learning para aprender novos aliases
- Sugestão de mapeamento manual para colunas não reconhecidas
- Support para CSV com colunas extras (custom Moodle fields)

---

## 🚀 Handoff to Developer

### Getting Started
```bash
# 1. Criar branch (se não existe)
git checkout -b feature/1.2-column-mapper

# 2. Criar arquivo
touch backend/src/moodlelogsmart/core/auto_detect/column_mapper.py

# 3. Instalar dependência
poetry add rapidfuzz

# 4. Rodar tests
poetry run pytest tests/unit/test_column_mapper.py -v
```

### Key Files to Modify
- `backend/src/moodlelogsmart/core/auto_detect/column_mapper.py` (novo)
- `backend/tests/unit/test_column_mapper.py` (novo)
- `backend/tests/integration/test_column_mapper_integration.py` (novo)
- `backend/pyproject.toml` (adicionar rapidfuzz)

### Success Criteria Summary
✅ Mapeia 6 colunas obrigatórias
✅ Suporta 3+ aliases por coluna
✅ Fuzzy matching >80% threshold
✅ Error claro se coluna obrigatória faltando
✅ Tests >85% coverage

---

**Story Owner**: @sm (River)
**Developer**: @dev
**Reviewer**: @architect (code review)
**QA**: @qa (test validation)

*Created by River (Scrum Master)*
*Last Updated: 2026-01-28*

— River, removendo obstáculos 🌊