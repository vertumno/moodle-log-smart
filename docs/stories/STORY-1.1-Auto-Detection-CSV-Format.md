# User Story 1.1: Auto-Detection de Encoding e Delimiter

**Story ID**: STORY-1.1
**Epic**: EPIC-01 - Backend Core + Auto-Detection
**Product**: MoodleLogSmart
**Sprint**: Sprint 1 (Day 1)
**Priority**: P0 (Must-Have)
**Status**: Not Started
**Estimate**: 1 dia
**Assigned To**: @dev

---

## 📋 Story Overview

### User Story
```
As a usuário não-técnico
I want fazer upload de CSV sem saber encoding/delimiter
So that não preciso configurar detalhes técnicos
```

### Business Context
Logs do Moodle podem ser exportados em diferentes formatos dependendo da versão, locale e configuração do servidor. Usuários não devem precisar saber qual encoding (UTF-8, Latin-1, etc.) ou delimiter (, ; \t) está sendo usado. O sistema deve detectar automaticamente, eliminando fricção.

### Value Proposition
- **Elimina configuração manual**: Usuário não precisa abrir CSV para verificar formato
- **Suporta múltiplas versões Moodle**: Diferentes instalações usam diferentes formatos
- **Reduz erros**: Auto-detection previne erros de parsing

---

## ✅ Acceptance Criteria

### AC1: Detecta Encoding Automaticamente
**Given** um arquivo CSV com encoding UTF-8
**When** o sistema recebe o arquivo
**Then** detecta encoding como "utf-8" corretamente

**Validation**:
- Testa com arquivo UTF-8
- Testa com arquivo Latin-1 (ISO-8859-1)
- Testa com arquivo CP1252 (Windows)

### AC2: Detecta Delimiter Automaticamente
**Given** um arquivo CSV com delimiter ","
**When** o sistema analisa o arquivo
**Then** detecta delimiter como ","

**Validation**:
- Testa com delimiter "," (vírgula)
- Testa com delimiter ";" (ponto e vírgula)
- Testa com delimiter "\t" (tab)
- Testa com delimiter "|" (pipe)

### AC3: Valida Estrutura Básica do CSV
**Given** um arquivo CSV válido
**When** o sistema valida a estrutura
**Then** confirma presença de header row

**Validation**:
- CSV tem header row (primeira linha com nomes de colunas)
- CSV tem pelo menos 2 linhas (header + dados)
- CSV não está vazio

### AC4: Retorna Erro Claro se CSV Inválido
**Given** um arquivo inválido (não-CSV ou corrompido)
**When** o sistema tenta processar
**Then** retorna erro user-friendly

**Validation**:
- Arquivo vazio → "Arquivo CSV está vazio"
- Arquivo binário → "Arquivo não é um CSV válido"
- Encoding desconhecido → "Não foi possível detectar encoding do arquivo"

---

## 🏗️ Technical Implementation

### Component: CSVDetector

**File**: `backend/src/moodlelogsmart/core/auto_detect/csv_detector.py`

```python
from dataclasses import dataclass
import chardet
import csv
from pathlib import Path
from typing import Optional

@dataclass
class CSVFormat:
    """Formato detectado do CSV"""
    encoding: str
    delimiter: str
    has_header: bool
    line_count: int

class CSVDetector:
    """Detecta formato de arquivo CSV automaticamente"""

    COMMON_DELIMITERS = [',', ';', '\t', '|']

    def detect(self, file_path: str) -> CSVFormat:
        """
        Detecta encoding, delimiter e estrutura do CSV

        Args:
            file_path: Caminho para arquivo CSV

        Returns:
            CSVFormat com informações detectadas

        Raises:
            ValueError: Se arquivo for inválido
        """
        path = Path(file_path)

        # Valida arquivo existe
        if not path.exists():
            raise ValueError(f"Arquivo não encontrado: {file_path}")

        # Valida não está vazio
        if path.stat().st_size == 0:
            raise ValueError("Arquivo CSV está vazio")

        # Detecta encoding
        encoding = self._detect_encoding(file_path)

        # Detecta delimiter
        delimiter = self._detect_delimiter(file_path, encoding)

        # Valida estrutura
        has_header, line_count = self._validate_structure(
            file_path, encoding, delimiter
        )

        return CSVFormat(
            encoding=encoding,
            delimiter=delimiter,
            has_header=has_header,
            line_count=line_count
        )

    def _detect_encoding(self, file_path: str) -> str:
        """Detecta encoding usando chardet"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Lê primeiros 10KB
            result = chardet.detect(raw_data)

            if result['confidence'] < 0.7:
                raise ValueError(
                    "Não foi possível detectar encoding do arquivo. "
                    f"Confiança: {result['confidence']:.2f}"
                )

            return result['encoding'].lower()

    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detecta delimiter testando formatos comuns"""
        with open(file_path, 'r', encoding=encoding) as f:
            sample = f.read(1024)  # Amostra das primeiras linhas

            # Testa cada delimiter comum
            delimiter_counts = {}
            for delim in self.COMMON_DELIMITERS:
                count = sample.count(delim)
                delimiter_counts[delim] = count

            # Retorna delimiter mais frequente
            best_delim = max(delimiter_counts, key=delimiter_counts.get)

            if delimiter_counts[best_delim] == 0:
                raise ValueError(
                    "Não foi possível detectar delimiter. "
                    f"Testados: {self.COMMON_DELIMITERS}"
                )

            return best_delim

    def _validate_structure(
        self,
        file_path: str,
        encoding: str,
        delimiter: str
    ) -> tuple[bool, int]:
        """Valida estrutura básica do CSV"""
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)

            try:
                # Lê header
                header = next(reader)
                has_header = len(header) > 0

                # Conta linhas
                line_count = 1 + sum(1 for _ in reader)

                if line_count < 2:
                    raise ValueError(
                        "CSV deve ter pelo menos 2 linhas (header + dados)"
                    )

                return has_header, line_count

            except StopIteration:
                raise ValueError("CSV não contém dados")
```

### Dependencies
- **chardet**: Detecção de encoding
- **csv**: Standard library (parsing CSV)
- **pathlib**: Manipulação de paths

### Error Handling
```python
# Exemplo de uso com error handling
try:
    detector = CSVDetector()
    csv_format = detector.detect("moodle_log.csv")
    print(f"Detectado: {csv_format.encoding}, delimiter={csv_format.delimiter}")
except ValueError as e:
    # Mensagem user-friendly
    print(f"Erro ao processar CSV: {e}")
```

---

## 🧪 Testing Requirements

### Unit Tests

**File**: `backend/tests/unit/test_csv_detector.py`

```python
import pytest
from pathlib import Path
from moodlelogsmart.core.auto_detect.csv_detector import CSVDetector, CSVFormat

class TestCSVDetector:

    @pytest.fixture
    def detector(self):
        return CSVDetector()

    def test_detect_utf8_comma(self, detector, tmp_path):
        """Test UTF-8 encoding with comma delimiter"""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age,City\nJohn,30,NYC\n", encoding='utf-8')

        # Act
        result = detector.detect(str(csv_file))

        # Assert
        assert result.encoding == 'utf-8'
        assert result.delimiter == ','
        assert result.has_header is True
        assert result.line_count == 2

    def test_detect_latin1_semicolon(self, detector, tmp_path):
        """Test Latin-1 encoding with semicolon delimiter"""
        # Arrange
        csv_file = tmp_path / "test.csv"
        content = "Nome;Idade;Cidade\nJoão;30;São Paulo\n"
        csv_file.write_bytes(content.encode('latin-1'))

        # Act
        result = detector.detect(str(csv_file))

        # Assert
        assert result.encoding == 'iso-8859-1'  # chardet retorna iso-8859-1
        assert result.delimiter == ';'
        assert result.has_header is True

    def test_detect_tab_delimiter(self, detector, tmp_path):
        """Test tab delimiter"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name\tAge\tCity\nJohn\t30\tNYC\n", encoding='utf-8')

        result = detector.detect(str(csv_file))

        assert result.delimiter == '\t'

    def test_empty_file_raises_error(self, detector, tmp_path):
        """Test empty file raises ValueError"""
        csv_file = tmp_path / "empty.csv"
        csv_file.touch()

        with pytest.raises(ValueError, match="está vazio"):
            detector.detect(str(csv_file))

    def test_file_not_found_raises_error(self, detector):
        """Test non-existent file raises ValueError"""
        with pytest.raises(ValueError, match="não encontrado"):
            detector.detect("nonexistent.csv")

    def test_invalid_csv_raises_error(self, detector, tmp_path):
        """Test file with no valid delimiter raises error"""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text("NoDelimitersHere\nJustText\n", encoding='utf-8')

        with pytest.raises(ValueError, match="Não foi possível detectar delimiter"):
            detector.detect(str(csv_file))
```

### Integration Tests

**File**: `backend/tests/integration/test_csv_detector_integration.py`

```python
def test_real_moodle_csv_sample(detector):
    """Test with real Moodle CSV sample"""
    # Use fixture with real Moodle export
    csv_path = "tests/fixtures/moodle_log_sample.csv"

    result = detector.detect(csv_path)

    # Moodle geralmente usa UTF-8 e vírgula
    assert result.encoding in ['utf-8', 'utf-8-sig']
    assert result.delimiter == ','
    assert result.has_header is True
    assert result.line_count > 10  # Sample tem vários eventos
```

### Test Coverage Target
- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical Paths**: 100% coverage (error handling)

---

## 📊 Definition of Done

### Code Complete
- ✅ `CSVDetector` class implementada
- ✅ Todos os métodos implementados (_detect_encoding, _detect_delimiter, _validate_structure)
- ✅ Error handling robusto
- ✅ Type hints completos

### Testing Complete
- ✅ Unit tests escritos (6+ test cases)
- ✅ Integration test com CSV real do Moodle
- ✅ Todos os testes passando
- ✅ Coverage >80%

### Documentation Complete
- ✅ Docstrings em todos os métodos
- ✅ Type hints documentados
- ✅ Exemplos de uso no código

### Quality Gates
- ✅ Code review aprovado
- ✅ No linting errors (ruff)
- ✅ Type checking passa (mypy)
- ✅ Tests passam em CI

---

## 🔗 Dependencies

### Blocked By
- None (primeira story do sprint)

### Blocks
- Story 1.2: Auto-Mapeamento de Colunas (precisa do CSV parser)
- Story 1.3: Auto-Detection de Timestamp (precisa do CSV parser)

### Related Stories
- Story 1.4: Data Cleaning (usará CSVDetector)

---

## 📝 Notes & Clarifications

### Design Decisions
1. **chardet vs manual detection**: Usamos chardet para encoding pois é mais robusto que heurísticas manuais
2. **Delimiter detection**: Testamos delimiters comuns ao invés de usar csv.Sniffer (mais confiável)
3. **Sample size**: Lemos apenas 10KB para encoding detection (performance vs acurácia)

### Edge Cases Handled
- Arquivos muito pequenos (<2 linhas)
- Arquivos vazios
- Encodings mistos (fallback para UTF-8)
- Delimiters raros (fallback para vírgula)

### Future Enhancements (Out of Scope)
- Suporte para Excel (.xlsx) - Fase 2
- Auto-detect de quote character
- Detection de encoding baseado em BOM (Byte Order Mark)

---

## 🚀 Handoff to Developer

### Getting Started
```bash
# 1. Criar branch
git checkout -b feature/1.1-csv-detector

# 2. Criar arquivo
touch backend/src/moodlelogsmart/core/auto_detect/csv_detector.py

# 3. Instalar dependência
poetry add chardet

# 4. Rodar tests
poetry run pytest tests/unit/test_csv_detector.py -v
```

### Key Files to Modify
- `backend/src/moodlelogsmart/core/auto_detect/csv_detector.py` (novo)
- `backend/tests/unit/test_csv_detector.py` (novo)
- `backend/tests/integration/test_csv_detector_integration.py` (novo)
- `backend/pyproject.toml` (adicionar chardet dependency)

### Success Criteria Summary
✅ Detecta UTF-8, Latin-1, CP1252
✅ Detecta delimiters: , ; \t |
✅ Valida estrutura (header + dados)
✅ Retorna erros user-friendly
✅ Tests >80% coverage

---

**Story Owner**: @sm (River)
**Developer**: @dev
**Reviewer**: @architect (code review)
**QA**: @qa (test validation)

*Created by River (Scrum Master)*
*Last Updated: 2026-01-28*

— River, removendo obstáculos 🌊