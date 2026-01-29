# Stories 1.4-1.7: Completando Epic 01

Este documento consolida as 4 user stories restantes do Epic 01 para referência rápida.

---

## Story 1.4: Data Cleaning com Configuração Default

**ID**: STORY-1.4 | **Sprint**: Sprint 1 (Day 3) | **Estimate**: 1 dia

### User Story
```
As a sistema
I want aplicar filtros automáticos baseados em defaults
So that apenas eventos de estudantes sejam processados
```

### Acceptance Criteria
- ✅ AC1: Filtra por studentRoleID = "5" (padrão Moodle)
- ✅ AC2: Remove eventos em non_student_events list
- ✅ AC3: Valida timestamps (remove inválidos)
- ✅ AC4: Normaliza tipos de dados

### Implementation
**Files**:
- `role_filter.py`, `event_filter.py`, `timestamp_validator.py`, `normalizer.py`
- `defaults.py` (configuração hard-coded)

### Key Code
```python
DEFAULT_CONFIG = {
    "filter": {
        "student_role_id": "5",
        "non_student_events": [
            "Course section deleted",
            "Course backup created",
            "Course updated"
        ]
    }
}
```

### Tests
- RoleFilter: 4 test cases
- EventFilter: 3 test cases
- TimestampValidator: 3 test cases
- Integration: pipeline completo

**Blocked by**: Story 1.3 (timestamps)

---

## Story 1.5: Rule Engine + 13 Regras Bloom

**ID**: STORY-1.5 | **Sprint**: Sprint 1 (Day 4) | **Estimate**: 2 dias

### User Story
```
As a pesquisador educacional
I want eventos classificados segundo Taxonomia de Bloom
So that posso analisar níveis cognitivos
```

### Acceptance Criteria
- ✅ AC1: Rule Engine lê bloom_taxonomy.yaml
- ✅ AC2: Implementa 13 regras originais
- ✅ AC3: Suporta operators: equals, in, contains
- ✅ AC4: Executa regras em ordem de prioridade
- ✅ AC5: Fallback para "Others" se nenhuma match
- ✅ AC6: Adiciona colunas: activity_type, bloom_level, is_active

### Implementation
**Files**:
- `rule_engine.py` (motor)
- `bloom_classifier.py` (wrapper)
- `bloom_taxonomy.yaml` (13 regras)

### Key Code
```python
class RuleEngine:
    def evaluate(self, event: RawMoodleEvent) -> EnrichedActivity:
        for rule in self.rules:
            if self._matches_all_conditions(event, rule.conditions):
                return self._apply_action(event, rule)
        return self._apply_default(event)
```

### bloom_taxonomy.yaml (sample)
```yaml
rules:
  - id: "R01"
    name: "View Resource"
    priority: 1
    conditions:
      - field: "component"
        operator: "in"
        values: ["File", "Folder", "Page"]
      - field: "event_name"
        operator: "equals"
        value: "Course module viewed"
    action:
      activity_type: "Study_P"
      bloom_level: "Remember"
      is_active: false
```

### Tests
- 13+ test cases (1 por regra)
- Priority ordering
- Fallback logic
- Integration: full pipeline

**Blocked by**: Story 1.4 (clean data)
**Blocks**: Story 1.6 (export)

---

## Story 1.6: Export Multi-Formato (CSV + XES)

**ID**: STORY-1.6 | **Sprint**: Sprint 1 (Day 5) | **Estimate**: 1 dia

### User Story
```
As a usuário
I want baixar resultados em CSV e XES
So that posso usar em Excel e ProM/Disco
```

### Acceptance Criteria
- ✅ AC1: Exporta enriched_log.csv (todas atividades)
- ✅ AC2: Exporta enriched_log_bloom_only.csv (filtrado)
- ✅ AC3: Exporta enriched_log.xes (PM4Py format)
- ✅ AC4: Exporta enriched_log_bloom_only.xes
- ✅ AC5: XES válido (pode abrir em ProM/Disco)
- ✅ AC6: CSV tem colunas corretas

### Implementation
**Files**:
- `csv_exporter.py` (Pandas)
- `xes_exporter.py` (PM4Py)

### Key Code
```python
class XESExporter:
    def export(self, df: pd.DataFrame, output_path: str):
        # Convert DataFrame to PM4Py event log
        event_log = pm4py.format_dataframe(
            df,
            case_id='user_full_name',
            activity_key='activity_type',
            timestamp_key='time'
        )
        # Write XES
        pm4py.write_xes(event_log, output_path)
```

### XES Structure
```xml
<log>
  <trace>
    <string key="concept:name" value="UserID"/>
    <event>
      <string key="concept:name" value="Study_A"/>
      <date key="time:timestamp" value="2024-01-15T10:30:45"/>
      <string key="org:resource" value="File"/>
    </event>
  </trace>
</log>
```

### Tests
- CSVExporter: 3 test cases
- XESExporter: 4 test cases (validation com PM4Py)
- Bloom filter: 2 test cases
- Integration: validate outputs

**Blocked by**: Story 1.5 (enriched data)
**Blocks**: Story 1.7 (ZIP)

---

## Story 1.7: ZIP Packager

**ID**: STORY-1.7 | **Sprint**: Sprint 1 (Day 5) | **Estimate**: 0.5 dia

### User Story
```
As a usuário
I want baixar todos resultados em 1 arquivo ZIP
So that não preciso baixar 4 arquivos separados
```

### Acceptance Criteria
- ✅ AC1: Cria ZIP contendo 4 arquivos
- ✅ AC2: Nome: results_YYYYMMDD_HHMMSS.zip
- ✅ AC3: ZIP pode ser extraído normalmente
- ✅ AC4: Arquivos dentro do ZIP têm nomes corretos

### Implementation
**File**: `zip_packager.py`

### Key Code
```python
import zipfile
from datetime import datetime
from pathlib import Path

class ZIPPackager:
    def package(self, files: dict[str, str], output_dir: str) -> str:
        """
        Empacota arquivos em ZIP

        Args:
            files: {filename: filepath}
            output_dir: Diretório de saída

        Returns:
            Path do ZIP criado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = Path(output_dir) / f"results_{timestamp}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in files.items():
                zipf.write(filepath, arcname=filename)

        return str(zip_path)
```

### Usage
```python
packager = ZIPPackager()

files = {
    "enriched_log.csv": "/tmp/enriched_log.csv",
    "enriched_log_bloom_only.csv": "/tmp/enriched_log_bloom_only.csv",
    "enriched_log.xes": "/tmp/enriched_log.xes",
    "enriched_log_bloom_only.xes": "/tmp/enriched_log_bloom_only.xes"
}

zip_path = packager.package(files, "/tmp/output")
# /tmp/output/results_20260128_153045.zip
```

### Tests
- ZIP creation: 2 test cases
- ZIP extraction: 2 test cases
- Filename validation: 1 test case

**Blocked by**: Story 1.6 (exports)

---

## Definition of Done (All Stories)

### Epic-Level Completion
- ✅ Todas as 7 stories completadas
- ✅ Pipeline processa CSV → ZIP válido
- ✅ Auto-detection funciona (encoding, columns, timestamps)
- ✅ 13 regras Bloom implementadas
- ✅ Tests >50% coverage (target: 60%)
- ✅ Integration test end-to-end passa
- ✅ Code review aprovado
- ✅ Documentation atualizada

### Integration Test (End-to-End)
```python
def test_full_pipeline_epic01():
    """Test complete pipeline: CSV → ZIP"""
    # 1. Auto-detect CSV format
    detector = CSVDetector()
    csv_format = detector.detect("sample.csv")

    # 2. Map columns
    mapper = ColumnMapper()
    df = pd.read_csv("sample.csv", encoding=csv_format.encoding)
    mapping = mapper.map_columns(df)
    df = mapper.rename_dataframe(df, mapping)

    # 3. Detect timestamp format
    ts_detector = TimestampDetector()
    fmt = ts_detector.detect_format(df['time'])
    df['time'] = ts_detector.parse_timestamps(df['time'], fmt)

    # 4. Clean data
    role_filter = RoleFilter()
    df = role_filter.filter(df)

    # 5. Enrich with Bloom
    engine = RuleEngine("bloom_taxonomy.yaml")
    enriched = []
    for _, row in df.iterrows():
        event = RawMoodleEvent(**row.to_dict())
        enriched.append(engine.evaluate(event))
    df_enriched = pd.DataFrame([e.dict() for e in enriched])

    # 6. Export CSV + XES
    csv_exporter = CSVExporter()
    xes_exporter = XESExporter()

    csv_path = csv_exporter.export(df_enriched, "/tmp/enriched.csv")
    xes_path = xes_exporter.export(df_enriched, "/tmp/enriched.xes")

    # 7. Package ZIP
    packager = ZIPPackager()
    zip_path = packager.package({
        "enriched_log.csv": csv_path,
        "enriched_log.xes": xes_path
    }, "/tmp")

    # Assertions
    assert Path(zip_path).exists()
    assert Path(zip_path).stat().st_size > 0

    # Extract and validate
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        assert len(zipf.namelist()) == 4
        assert "enriched_log.csv" in zipf.namelist()
        assert "enriched_log.xes" in zipf.namelist()
```

---

## Sprint 1 Completion Checklist

### Day 1
- ✅ Story 1.1: CSVDetector complete

### Day 2
- ✅ Story 1.2: ColumnMapper complete
- ✅ Story 1.3: TimestampDetector complete

### Day 3
- ✅ Story 1.4: Data Cleaning complete

### Day 4
- ✅ Story 1.5: Rule Engine + 13 regras complete

### Day 5
- ✅ Story 1.6: Export CSV + XES complete
- ✅ Story 1.7: ZIP Packager complete
- ✅ Integration test passa
- ✅ Epic 01 DONE!

---

## Handoff to Sprint 2

### Deliverables para Sprint 2 (API Layer)
1. **Pipeline funcional**: Método `process(csv_path) -> zip_path`
2. **Classes prontas**: Todas disponíveis para import
3. **Tests passando**: >50% coverage confirmado
4. **Documentation**: Docstrings completos

### Next Epic: EPIC-02 (API Layer)
- Story 2.1: Endpoint de Upload
- Story 2.2: Endpoint de Status
- Story 2.3: Endpoint de Download
- Story 2.4: Job Management

---

**Epic Owner**: @sm (River)
**Sprint**: Sprint 1 (Week 1)
**Total Estimate**: 7 story points (7 dias)

*Created by River (Scrum Master)*
*Last Updated: 2026-01-28*

— River, removendo obstáculos 🌊