# User Story 1.3: Auto-Detection de Formato de Timestamp

**Story ID**: STORY-1.3
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
I want que sistema detecte formato de data automaticamente
So that não preciso especificar "%d/%m/%y, %H:%M:%S"
```

### Business Context
Moodle exporta timestamps em diferentes formatos dependendo de:
- **Locale do servidor** (BR: dd/mm/yy vs US: mm/dd/yy)
- **Versão do Moodle** (formatos mudaram entre versões)
- **Configuração do site** (24h vs AM/PM)

Usuários não devem precisar descobrir qual formato está sendo usado. O sistema deve testar formatos comuns e detectar automaticamente.

### Value Proposition
- **Funciona globalmente**: Suporta formatos BR, US, EU, ISO
- **Zero configuração**: Não precisa especificar strptime format
- **Robusto**: Fallback para pandas se formato desconhecido

---

## ✅ Acceptance Criteria

### AC1: Detecta Formato BR (dd/mm/yy, HH:MM:SS)
**Given** timestamps no formato "22/08/24, 13:43:23"
**When** o sistema detecta formato
**Then** identifica como "%d/%m/%y, %H:%M:%S"

**Validation**:
- Parse sucesso para "22/08/24, 13:43:23"
- Parse sucesso para "01/12/23, 09:15:00"
- Retorna datetime objects válidos

### AC2: Detecta Formato ISO (yyyy-mm-dd HH:MM:SS)
**Given** timestamps no formato "2024-08-22 13:43:23"
**When** o sistema detecta formato
**Then** identifica como "%Y-%m-%d %H:%M:%S"

**Validation**:
- Parse "2024-08-22 13:43:23"
- Parse "2023-12-01 09:15:00"

### AC3: Detecta Formato US com AM/PM
**Given** timestamps no formato "08/22/2024 01:43:23 PM"
**When** o sistema detecta formato
**Then** identifica como "%m/%d/%Y %I:%M:%S %p"

**Validation**:
- Parse "08/22/2024 01:43:23 PM"
- Parse "12/01/2023 09:15:00 AM"
- Converte corretamente PM/AM

### AC4: Detecta Outros Formatos Comuns
**Given** timestamps em formatos variados
**When** o sistema testa 10+ formatos
**Then** identifica o formato correto

**Formatos suportados**:
- "%d/%m/%y, %H:%M:%S" (BR short year)
- "%d/%m/%Y %H:%M:%S" (BR full year)
- "%Y-%m-%d %H:%M:%S" (ISO)
- "%m/%d/%Y %I:%M:%S %p" (US 12h)
- "%m/%d/%Y %H:%M:%S" (US 24h)
- "%d-%m-%Y %H:%M:%S" (EU)
- "%Y/%m/%d %H:%M:%S" (Asia)
- Mais...

### AC5: Fallback para Pandas Auto-Inference
**Given** formato desconhecido não está na lista
**When** nenhum formato manual match
**Then** usa pandas.to_datetime() inference

**Validation**:
- Pandas consegue parsear formatos não mapeados
- Retorna datetime objects válidos
- Log warning sobre formato desconhecido

---

## 🏗️ Technical Implementation

### Component: TimestampDetector

**File**: `backend/src/moodlelogsmart/core/auto_detect/timestamp_detector.py`

```python
from datetime import datetime
from typing import Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TimestampDetector:
    """Detecta formato de timestamp automaticamente"""

    # Formatos comuns ordenados por probabilidade (Moodle típico primeiro)
    COMMON_FORMATS = [
        "%d/%m/%y, %H:%M:%S",       # BR: 22/08/24, 13:43:23 (MAIS COMUM)
        "%d/%m/%Y %H:%M:%S",        # BR: 22/08/2024 13:43:23
        "%Y-%m-%d %H:%M:%S",        # ISO: 2024-08-22 13:43:23
        "%d-%m-%Y %H:%M:%S",        # EU: 22-08-2024 13:43:23
        "%m/%d/%Y %I:%M:%S %p",     # US 12h: 08/22/2024 01:43:23 PM
        "%m/%d/%Y %H:%M:%S",        # US 24h: 08/22/2024 13:43:23
        "%m/%d/%y %H:%M:%S",        # US short: 08/22/24 13:43:23
        "%Y/%m/%d %H:%M:%S",        # Asia: 2024/08/22 13:43:23
        "%d.%m.%Y %H:%M:%S",        # DE: 22.08.2024 13:43:23
        "%Y-%m-%dT%H:%M:%S",        # ISO-8601: 2024-08-22T13:43:23
        "%Y-%m-%dT%H:%M:%S.%f",     # ISO with ms: 2024-08-22T13:43:23.000
        "%d %b %Y %H:%M:%S",        # UK: 22 Aug 2024 13:43:23
    ]

    def detect_format(self, timestamps: pd.Series) -> Optional[str]:
        """
        Detecta formato de timestamp testando formatos comuns

        Args:
            timestamps: Pandas Series com timestamps como strings

        Returns:
            String de formato (strptime) ou None (usa pandas inference)

        Raises:
            ValueError: Se timestamps estão vazios ou inválidos
        """
        if len(timestamps) == 0:
            raise ValueError("Series de timestamps está vazia")

        # Remove valores nulos
        timestamps_clean = timestamps.dropna()

        if len(timestamps_clean) == 0:
            raise ValueError("Todos os timestamps são nulos")

        # Pega sample (primeiros 100 para performance)
        sample = timestamps_clean.head(100)

        # Testa cada formato comum
        for fmt in self.COMMON_FORMATS:
            if self._test_format(sample, fmt):
                logger.info(f"Formato detectado: {fmt}")
                return fmt

        # Fallback: deixa pandas decidir
        logger.warning(
            "Formato de timestamp não reconhecido. "
            "Usando pandas auto-inference."
        )
        return None

    def _test_format(self, timestamps: pd.Series, fmt: str) -> bool:
        """
        Testa se um formato funciona para os timestamps

        Args:
            timestamps: Sample de timestamps
            fmt: Formato strptime para testar

        Returns:
            True se formato funciona para >90% do sample
        """
        successful_parses = 0
        total = len(timestamps)

        for ts_str in timestamps:
            try:
                # Tenta parsear com formato
                datetime.strptime(str(ts_str), fmt)
                successful_parses += 1
            except (ValueError, TypeError):
                # Formato não match
                continue

        # Formato aceito se >90% dos timestamps parseiam
        success_rate = successful_parses / total
        return success_rate > 0.9

    def parse_timestamps(
        self,
        timestamps: pd.Series,
        fmt: Optional[str] = None
    ) -> pd.Series:
        """
        Parseia timestamps para datetime objects

        Args:
            timestamps: Series com timestamps como strings
            fmt: Formato strptime (None = auto-detect)

        Returns:
            Series com datetime objects
        """
        if fmt is None:
            # Auto-detect formato
            fmt = self.detect_format(timestamps)

        if fmt is not None:
            # Usa formato detectado
            try:
                return pd.to_datetime(timestamps, format=fmt, errors='coerce')
            except Exception as e:
                logger.warning(
                    f"Erro ao parsear com formato {fmt}: {e}. "
                    "Usando pandas inference."
                )
                # Fallback para inference
                return pd.to_datetime(timestamps, errors='coerce')
        else:
            # Usa pandas auto-inference
            return pd.to_datetime(timestamps, errors='coerce')

    def validate_datetime_range(self, timestamps: pd.Series) -> None:
        """
        Valida que timestamps estão em range razoável

        Args:
            timestamps: Series com datetime objects

        Raises:
            ValueError: Se timestamps estão fora de range esperado
        """
        min_date = timestamps.min()
        max_date = timestamps.max()

        # Valida range (Moodle existe desde ~2002)
        if min_date.year < 2000:
            raise ValueError(
                f"Timestamps inválidos: data mínima é {min_date.year}. "
                "Esperado >= 2000 (Moodle não existia antes)."
            )

        if max_date.year > datetime.now().year + 1:
            raise ValueError(
                f"Timestamps inválidos: data máxima é {max_date.year}. "
                f"Esperado <= {datetime.now().year + 1}."
            )
```

### Dependencies
- **pandas**: Datetime parsing e inference
- **logging**: Log de warnings
- **datetime**: Manual parsing

### Example Usage
```python
# Exemplo de uso
detector = TimestampDetector()

# CSV tem timestamps como strings
df = pd.read_csv("moodle_log.csv")
time_column = df['Time']

# Detecta formato
fmt = detector.detect_format(time_column)
print(f"Formato: {fmt}")  # "%d/%m/%y, %H:%M:%S"

# Parseia timestamps
df['time_parsed'] = detector.parse_timestamps(time_column, fmt)

# Valida range
detector.validate_datetime_range(df['time_parsed'])
```

---

## 🧪 Testing Requirements

### Unit Tests

**File**: `backend/tests/unit/test_timestamp_detector.py`

```python
import pytest
import pandas as pd
from datetime import datetime
from moodlelogsmart.core.auto_detect.timestamp_detector import TimestampDetector

class TestTimestampDetector:

    @pytest.fixture
    def detector(self):
        return TimestampDetector()

    def test_detect_br_format(self, detector):
        """Test Brazilian format: dd/mm/yy, HH:MM:SS"""
        timestamps = pd.Series([
            "22/08/24, 13:43:23",
            "01/12/23, 09:15:00",
            "15/03/24, 18:30:45"
        ])

        fmt = detector.detect_format(timestamps)

        assert fmt == "%d/%m/%y, %H:%M:%S"

    def test_detect_iso_format(self, detector):
        """Test ISO format: YYYY-MM-DD HH:MM:SS"""
        timestamps = pd.Series([
            "2024-08-22 13:43:23",
            "2023-12-01 09:15:00",
            "2024-03-15 18:30:45"
        ])

        fmt = detector.detect_format(timestamps)

        assert fmt == "%Y-%m-%d %H:%M:%S"

    def test_detect_us_12h_format(self, detector):
        """Test US 12h format with AM/PM"""
        timestamps = pd.Series([
            "08/22/2024 01:43:23 PM",
            "12/01/2023 09:15:00 AM",
            "03/15/2024 06:30:45 PM"
        ])

        fmt = detector.detect_format(timestamps)

        assert fmt == "%m/%d/%Y %I:%M:%S %p"

    def test_parse_timestamps_with_format(self, detector):
        """Test parsing timestamps with detected format"""
        timestamps = pd.Series([
            "22/08/24, 13:43:23",
            "01/12/23, 09:15:00"
        ])

        fmt = "%d/%m/%y, %H:%M:%S"
        parsed = detector.parse_timestamps(timestamps, fmt)

        # Verifica tipo
        assert parsed.dtype == 'datetime64[ns]'

        # Verifica valores
        assert parsed[0].day == 22
        assert parsed[0].month == 8
        assert parsed[0].year == 2024
        assert parsed[0].hour == 13
        assert parsed[0].minute == 43

    def test_parse_timestamps_auto_detect(self, detector):
        """Test parsing with auto-detection"""
        timestamps = pd.Series([
            "2024-08-22 13:43:23",
            "2023-12-01 09:15:00"
        ])

        # Sem passar formato (auto-detect)
        parsed = detector.parse_timestamps(timestamps)

        assert parsed.dtype == 'datetime64[ns]'
        assert parsed[0].year == 2024

    def test_empty_timestamps_raises_error(self, detector):
        """Test empty series raises ValueError"""
        timestamps = pd.Series([])

        with pytest.raises(ValueError, match="vazia"):
            detector.detect_format(timestamps)

    def test_all_null_timestamps_raises_error(self, detector):
        """Test all null values raises ValueError"""
        timestamps = pd.Series([None, None, None])

        with pytest.raises(ValueError, match="nulos"):
            detector.detect_format(timestamps)

    def test_fallback_to_pandas_inference(self, detector):
        """Test fallback when format is unknown"""
        # Formato não comum, mas pandas consegue inferir
        timestamps = pd.Series([
            "2024-08-22",  # Só data, sem hora
            "2023-12-01"
        ])

        fmt = detector.detect_format(timestamps)

        # Deve retornar None (fallback)
        assert fmt is None

        # Mas parsing deve funcionar
        parsed = detector.parse_timestamps(timestamps)
        assert parsed.dtype == 'datetime64[ns]'

    def test_validate_datetime_range_valid(self, detector):
        """Test validation passes for valid date range"""
        timestamps = pd.Series([
            pd.Timestamp("2020-01-01"),
            pd.Timestamp("2024-12-31")
        ])

        # Não deve levantar erro
        detector.validate_datetime_range(timestamps)

    def test_validate_datetime_range_too_old(self, detector):
        """Test validation fails for dates before 2000"""
        timestamps = pd.Series([
            pd.Timestamp("1999-01-01"),  # Antes do Moodle existir
            pd.Timestamp("2024-12-31")
        ])

        with pytest.raises(ValueError, match="inválidos"):
            detector.validate_datetime_range(timestamps)

    def test_validate_datetime_range_future(self, detector):
        """Test validation fails for far future dates"""
        timestamps = pd.Series([
            pd.Timestamp("2020-01-01"),
            pd.Timestamp("2050-12-31")  # Muito no futuro
        ])

        with pytest.raises(ValueError, match="inválidos"):
            detector.validate_datetime_range(timestamps)
```

### Integration Tests

**File**: `backend/tests/integration/test_timestamp_detector_integration.py`

```python
def test_real_moodle_timestamps(detector):
    """Test with real Moodle CSV sample"""
    df = pd.read_csv("tests/fixtures/moodle_log_sample.csv")

    # Assumindo coluna já mapeada
    timestamps = df['Time']

    # Detecta e parseia
    fmt = detector.detect_format(timestamps)
    assert fmt is not None

    parsed = detector.parse_timestamps(timestamps, fmt)

    # Valida range
    detector.validate_datetime_range(parsed)

    # Verifica todos foram parseados
    assert parsed.notna().all()
```

### Test Coverage Target
- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical Paths**: 100% (fallback logic)

---

## 📊 Definition of Done

### Code Complete
- ✅ `TimestampDetector` class implementada
- ✅ 12+ formatos comuns suportados
- ✅ Fallback para pandas inference
- ✅ Validation de datetime range
- ✅ Logging apropriado

### Testing Complete
- ✅ Unit tests (10+ test cases)
- ✅ Integration test com CSV real
- ✅ Tests passando
- ✅ Coverage >80%

### Documentation Complete
- ✅ Docstrings completos
- ✅ COMMON_FORMATS documentado
- ✅ Examples de uso

### Quality Gates
- ✅ Code review aprovado
- ✅ No linting errors
- ✅ Type checking passa
- ✅ Tests passam em CI

---

## 🔗 Dependencies

### Blocked By
- **Story 1.2**: Precisa de coluna `time` mapeada

### Blocks
- **Story 1.4**: Data Cleaning precisa de timestamps parseados

### Related Stories
- **Story 1.5**: Rule Engine usará timestamps

---

## 🚀 Handoff to Developer

### Getting Started
```bash
# 1. Branch (se não existe)
git checkout -b feature/1.3-timestamp-detector

# 2. Criar arquivo
touch backend/src/moodlelogsmart/core/auto_detect/timestamp_detector.py

# 3. Rodar tests
poetry run pytest tests/unit/test_timestamp_detector.py -v
```

### Success Criteria Summary
✅ Detecta 12+ formatos comuns
✅ Fallback para pandas inference
✅ Valida datetime range (2000 - now+1)
✅ Error handling robusto
✅ Tests >80% coverage

---

**Story Owner**: @sm (River)
**Developer**: @dev

*Created by River (Scrum Master)*

— River, removendo obstáculos 🌊