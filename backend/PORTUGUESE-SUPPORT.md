# Suporte para Colunas em Português

## Visão Geral

O MoodleLogSmart agora oferece suporte completo para arquivos CSV do Moodle com headers em **português (PT-BR)**, além do suporte existente para inglês.

## Colunas Suportadas

### Mapeamento Português → Inglês

| Campo Interno | Português (PT-BR) | Inglês |
|--------------|-------------------|--------|
| **time** | Hora, Horário, Data/Hora, Data e hora | Time, Timestamp, Date/Time, DateTime |
| **user_full_name** | Nome completo, Nome, Usuário, Nome do usuário | User full name, Full name, Name, Username |
| **event_name** | Nome do evento, Evento, Ação, Tipo de evento | Event name, Event, Action, Event type |
| **component** | Componente, Módulo, Nome do componente | Component, Module, Component name |
| **event_context** | Contexto do Evento, Contexto, Curso | Event context, Context, Course |
| **description** | Descrição, Detalhes, Informação, Informações | Description, Details, Info, Information |
| **affected_user** | Usuário afetado, Usuário relacionado | Affected user, Related user |
| **origin** | Origem, Fonte | Origin, Source |
| **ip_address** | endereço IP, Endereço IP, IP do usuário, IP | IP address, IP, User IP |

## Exemplo de CSV Português

```csv
Hora,"Nome completo","Usuário afetado","Contexto do Evento",Componente,"Nome do evento",Descrição,Origem,"endereço IP"
"22/01/26, 23:26:24","João Silva",-,"Curso: Matemática",Logs,"Relatório de log visto","Usuário visualizou o relatório",web,192.168.1.100
```

Este CSV será automaticamente mapeado para o schema interno do sistema.

## Características

### ✅ Case Insensitive
- `Hora`, `hora`, `HORA` são todos reconhecidos

### ✅ Fuzzy Matching
- Pequenas variações são toleradas (threshold de 80% similaridade)
- Exemplo: "Nome Completo" vs "Nome completo"

### ✅ Múltiplos Aliases
- Cada campo aceita várias variações
- Exemplo: "Hora", "Horário", "Data/Hora" → todos mapeiam para `time`

### ✅ Suporte Misto
- Pode misturar colunas em português e inglês no mesmo CSV
- Exemplo: CSV com "Time" (inglês) e "Nome completo" (português)

## Como Funciona

O sistema usa o módulo `ColumnMapper` para:

1. **Detecção automática**: Identifica colunas por nome (exato ou fuzzy match)
2. **Validação**: Verifica se todas as colunas obrigatórias foram encontradas
3. **Mapeamento**: Cria dicionário de renomeação para padronização interna

## Implementação

### Código
```python
from moodlelogsmart.core.auto_detect.column_mapper import ColumnMapper

# Colunas do CSV em português
csv_columns = ['Hora', 'Nome completo', 'Nome do evento', ...]

mapper = ColumnMapper()
mapping = mapper.map_columns(csv_columns)

# mapping.time = 'Hora'
# mapping.user_full_name = 'Nome completo'
# mapping.event_name = 'Nome do evento'
```

### Testes
Execute os testes para validar o suporte:

```bash
pytest backend/tests/test_portuguese_columns.py -v
```

## Erros Comuns

### Coluna não encontrada
```
ValueError: Coluna obrigatória não encontrada: time.
Esperado um dos: Time, Timestamp, Hora, Horário, ...
```

**Solução**: Verifique se o CSV possui a coluna de timestamp com um dos nomes suportados.

### Encoding incorreto
Se caracteres acentuados aparecem incorretos, use a detecção automática de encoding:

```python
from moodlelogsmart.core.auto_detect.csv_detector import CSVDetector

detector = CSVDetector()
result = detector.detect_encoding('arquivo.csv')
# result.encoding será 'UTF-8', 'Latin-1', etc.
```

## Referências

- **STORY-1.2**: Auto-Mapeamento de Colunas Moodle
- **Arquivo**: `backend/src/moodlelogsmart/core/auto_detect/column_mapper.py`
- **Testes**: `backend/tests/test_portuguese_columns.py`

## Histórico

- **2026-01-30**: Implementado suporte completo para PT-BR (fix de bug)
- **2026-01-28**: Versão inicial com suporte apenas para inglês
