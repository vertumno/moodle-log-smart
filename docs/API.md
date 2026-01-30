# 📚 Documentação da API

Documentação completa dos endpoints REST da API do MoodleLogSmart para processamento de logs do Moodle com enriquecimento semântico via Taxonomia de Bloom.

## 🔗 Informações Gerais

**Base URL**:
- Desenvolvimento: `http://localhost:8000`
- Staging: `https://moodle-log-smart-backend.onrender.com`
- Produção: `https://moodle-log-smart-backend.onrender.com`

**Versão API**: 1.0.0

**Documentação Interativa**: `{BASE_URL}/docs` (Swagger UI)

**OpenAPI Schema**: `{BASE_URL}/openapi.json`

---

## 🔐 Autenticação

Todos os endpoints (exceto `/health`) requerem autenticação via **API Key**.

### Header Obrigatório

```
X-API-Key: sua-chave-api-secreta
```

### Gerar Chave API

```bash
# Gerar chave segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Adicionar em .env
API_KEYS=chave-gerada-aqui
```

### Exemplo de Requisição

```bash
curl -X GET http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: sua-chave-api-secreta"
```

---

## ✅ Health Check

Verificar disponibilidade da API (sem autenticação).

### Requisição

```http
GET /health
```

### cURL

```bash
curl http://localhost:8000/health
```

### Resposta (200)

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

### Códigos de Resposta

| Código | Descrição |
|--------|-----------|
| 200 | API está saudável e operacional |
| 503 | API indisponível (maintenance ou error) |

---

## 📤 Upload de Arquivo

Fazer upload de arquivo CSV do Moodle para processamento.

### Requisição

```http
POST /api/upload
Content-Type: multipart/form-data

file: <arquivo.csv>
```

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `file` | File | Sim | Arquivo CSV do Moodle (máximo 50MB) |

### Limitações

- **Tamanho máximo**: 50MB
- **Formatos aceitos**: `.csv`
- **Encoding**: Detectado automaticamente (UTF-8, ISO-8859-1, etc.)

### cURL

```bash
curl -X POST http://localhost:8000/api/upload \
  -H "X-API-Key: sua-chave-api" \
  -F "file=@logs/moodle_log.csv"
```

### Exemplo Python

```python
import requests

url = "http://localhost:8000/api/upload"
headers = {"X-API-Key": "sua-chave-api"}
files = {"file": open("moodle_log.csv", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### Exemplo JavaScript

```javascript
const uploadFile = async (file, apiKey) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/api/upload", {
    method: "POST",
    headers: {
      "X-API-Key": apiKey
    },
    body: formData
  });

  return await response.json();
};
```

### Resposta (200 - Sucesso)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Arquivo enviado e processamento iniciado",
  "created_at": "2024-01-15T10:30:45.123456Z"
}
```

### Resposta (400 - Validação Falhou)

```json
{
  "detail": "Apenas arquivos .csv são permitidos"
}
```

Possíveis erros:
- `"Only .csv files are allowed"` - Extensão inválida
- `"File size exceeds 50MB limit"` - Arquivo muito grande
- `"Invalid file format"` - Formato CSV inválido
- `"No file provided"` - Campo file vazio

### Resposta (401 - Não Autenticado)

```json
{
  "detail": "Invalid or missing API key"
}
```

### Resposta (500 - Erro Interno)

```json
{
  "detail": "Internal server error",
  "error_id": "err-12345"
}
```

---

## 📊 Consultar Status

Verificar status e progresso de um job em processamento.

### Requisição

```http
GET /api/status/{job_id}
```

### Parâmetros de Caminho

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `job_id` | UUID | ID do job (retornado no upload) |

### cURL

```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: sua-chave-api"
```

### Exemplo Python

```python
import requests

job_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:8000/api/status/{job_id}"
headers = {"X-API-Key": "sua-chave-api"}

response = requests.get(url, headers=headers)
print(response.json())
```

### Resposta (200 - Processando)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Limpando dados... (etapa 2 de 5)",
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:31:15.123456Z",
  "completed_at": null,
  "error": null,
  "estimated_time_remaining_seconds": 60
}
```

### Resposta (200 - Completo)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Processamento concluído com sucesso",
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:32:45.123456Z",
  "completed_at": "2024-01-15T10:32:45.123456Z",
  "error": null,
  "processing_time_seconds": 120,
  "statistics": {
    "total_events": 5000,
    "student_events": 4800,
    "bloom_classified_events": 3500,
    "invalid_events": 200
  }
}
```

### Resposta (200 - Erro no Processamento)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "message": "Processamento falhou",
  "error": "CSV format not recognized. Column names must match Moodle standard or PT-BR format",
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:30:50.123456Z",
  "completed_at": "2024-01-15T10:30:50.123456Z"
}
```

### Status Valores

| Status | Descrição |
|--------|-----------|
| `queued` | Job está na fila aguardando processamento |
| `processing` | Job está sendo processado |
| `completed` | Job concluído com sucesso |
| `failed` | Job falhou com erro |
| `timeout` | Job excedeu limite de tempo (10 minutos) |

### Resposta (404 - Job Não Encontrado)

```json
{
  "detail": "Job not found or access denied"
}
```

### Resposta (401 - Não Autenticado)

```json
{
  "detail": "Invalid or missing API key"
}
```

---

## 📥 Download de Resultados

Fazer download do arquivo ZIP com resultados do processamento.

### Requisição

```http
GET /api/download/{job_id}
```

### Parâmetros de Caminho

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `job_id` | UUID | ID do job |

### Pré-requisitos

- Job deve estar com status `completed`
- Não pode ter status `processing`, `failed`, ou `timeout`

### cURL

```bash
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: sua-chave-api" \
  -o resultado.zip
```

### Exemplo Python

```python
import requests

job_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:8000/api/download/{job_id}"
headers = {"X-API-Key": "sua-chave-api"}

response = requests.get(url, headers=headers, stream=True)
with open("resultado.zip", "wb") as f:
    for chunk in response.iter_content():
        f.write(chunk)
```

### Exemplo JavaScript

```javascript
const downloadResults = async (jobId, apiKey) => {
  const response = await fetch(
    `http://localhost:8000/api/download/${jobId}`,
    {
      headers: { "X-API-Key": apiKey }
    }
  );

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `resultado-${jobId}.zip`;
  a.click();
};
```

### Resposta (200 - Sucesso)

```
Content-Type: application/zip
Content-Disposition: attachment; filename="moodle_log_enriched.zip"

[arquivo ZIP com conteúdo binário]
```

### Conteúdo do ZIP

O arquivo ZIP contém:

```
resultado.zip/
├── enriched_log.csv              # Todos eventos com classificação Bloom
├── enriched_log_bloom_only.csv   # Apenas eventos pedagógicos
├── enriched_log.xes              # Formato ProM/Disco
├── enriched_log_bloom_only.xes   # ProM format, apenas pedagógico
└── metadata.json                 # Metadados do processamento
```

### Formato dos Arquivos CSV

**enriched_log.csv** (colunas):
```
timestamp,userid,action,component,description,bloom_level,bloom_category,bloom_score,is_pedagogical
2024-01-15T10:30:45Z,123,view,course,Visualizou página,2,understand,0.85,true
2024-01-15T10:31:00Z,124,submit,quiz,Submeteu teste,4,analyze,0.92,true
...
```

**Bloom Levels** (1-6):
- 1: Remember (Lembrar)
- 2: Understand (Entender)
- 3: Apply (Aplicar)
- 4: Analyze (Analisar)
- 5: Evaluate (Avaliar)
- 6: Create (Criar)

### Resposta (202 - Processando)

```json
{
  "detail": "Job still processing, try again in a few seconds"
}
```

### Resposta (404 - Job Não Encontrado)

```json
{
  "detail": "Job not found or access denied"
}
```

### Resposta (410 - Resultados Expirados)

```json
{
  "detail": "Results have expired and were automatically deleted"
}
```

Resultados são mantidos por **7 dias** após conclusão.

### Resposta (401 - Não Autenticado)

```json
{
  "detail": "Invalid or missing API key"
}
```

---

## 🗑️ Deletar Job

Deletar um job e liberar espaço em disco.

### Requisição

```http
DELETE /api/jobs/{job_id}
```

### cURL

```bash
curl -X DELETE http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: sua-chave-api"
```

### Resposta (200 - Deletado)

```json
{
  "message": "Job deleted successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Resposta (404 - Não Encontrado)

```json
{
  "detail": "Job not found"
}
```

---

## 🔄 Listar Jobs

Listar todos os jobs do usuário.

### Requisição

```http
GET /api/jobs
```

### Query Parameters

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `status` | string | - | Filtrar por status (processing, completed, failed) |
| `limit` | int | 10 | Máximo de resultados |
| `offset` | int | 0 | Pagination offset |

### cURL

```bash
curl "http://localhost:8000/api/jobs?status=completed&limit=10" \
  -H "X-API-Key: sua-chave-api"
```

### Resposta (200)

```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2024-01-15T10:30:45.123456Z",
      "completed_at": "2024-01-15T10:32:45.123456Z",
      "filename": "moodle_log.csv"
    },
    {
      "job_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "processing",
      "created_at": "2024-01-15T11:00:00.123456Z",
      "completed_at": null,
      "filename": "moodle_log_2.csv"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

---

## ⚠️ Tratamento de Erros

### Códigos HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Requisição bem-sucedida |
| 202 | Aceita (job ainda processando) |
| 400 | Erro de validação / dados inválidos |
| 401 | Não autenticado (API key inválida/ausente) |
| 403 | Acesso negado (job não pertence ao usuário) |
| 404 | Recurso não encontrado (job não existe) |
| 410 | Gone (recursos expirados e deletados) |
| 413 | Entidade muito grande (arquivo > 50MB) |
| 429 | Muitas requisições (rate limit excedido) |
| 500 | Erro interno do servidor |
| 503 | Serviço indisponível |
| 504 | Timeout do gateway |

### Formato de Erro Padrão

```json
{
  "detail": "Descrição do erro",
  "error_id": "ERR_TYPE_123",
  "timestamp": "2024-01-15T10:30:45.123456Z"
}
```

---

## 🔄 Fluxo Completo

### Exemplo: Upload → Status → Download

```python
import requests
import time

BASE_URL = "http://localhost:8000"
API_KEY = "sua-chave-api"

# 1. Upload
print("1. Uploading file...")
with open("moodle.csv", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/upload",
        headers={"X-API-Key": API_KEY},
        files={"file": f}
    )
    job_id = response.json()["job_id"]
    print(f"   Job ID: {job_id}")

# 2. Poll Status
print("2. Polling status...")
while True:
    response = requests.get(
        f"{BASE_URL}/api/status/{job_id}",
        headers={"X-API-Key": API_KEY}
    )
    status_data = response.json()
    progress = status_data.get("progress", 0)
    status = status_data["status"]

    print(f"   Status: {status}, Progress: {progress}%")

    if status in ["completed", "failed"]:
        break

    time.sleep(2)

# 3. Download
if status == "completed":
    print("3. Downloading results...")
    response = requests.get(
        f"{BASE_URL}/api/download/{job_id}",
        headers={"X-API-Key": API_KEY}
    )

    with open(f"resultado-{job_id}.zip", "wb") as f:
        f.write(response.content)

    print("   Download complete!")
else:
    print(f"   Processing failed: {status_data.get('error')}")
```

---

## 📊 Rate Limiting

**Limite atual**: 100 requests por minuto por API key

**Headers de resposta**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642250700
```

Quando atingir o limite:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60
}
```

---

## 📝 Changelog da API

### v1.0.0 (2026-01-29)

- ✅ Endpoints iniciais (upload, status, download)
- ✅ Autenticação via API Key
- ✅ Auto-detecção de CSV
- ✅ Classificação Bloom
- ✅ Exportação multi-formato
- ✅ Job management

---

## 🆘 Suporte

- 📖 [Documentação Completa](./README.md)
- 🐛 [Issues](https://github.com/vertumno/moodle-log-smart/issues)
- 💬 [Discussions](https://github.com/vertumno/moodle-log-smart/discussions)
- 🔗 [Swagger Interativo](http://localhost:8000/docs)

---

**Última Atualização**: 2026-01-30

**Versão**: 1.0.0
