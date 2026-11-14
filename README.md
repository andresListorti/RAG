# Consumidor RAG · Argentina

**Búsqueda auditable sobre la Ley 24.240, con citas textuales, recuperación híbrida y un flujo agéntico acotado.**

Proyecto de portfolio para mostrar decisiones de ingeniería de RAG: ingesta reproducible, recuperación evaluable, orquestación con herramientas, generación con evidencia y controles de seguridad. Interfaz y respuestas en español argentino; código en Python.

> Demo educativa, no asesoramiento jurídico. La Ley 24.240 es parte de un sistema normativo más amplio. El corpus no incluye jurisprudencia, códigos, reglamentación ni procedimientos provinciales. Verificá siempre la fuente oficial y su vigencia.

## Ejecutar en dos minutos

Requisitos: Python 3.13 y [uv](https://docs.astral.sh/uv/). No hace falta clave ni descargar modelos para la demo predeterminada.

```bash
git clone https://github.com/andresListorti/RAG.git
cd RAG
uv sync --frozen
uv run uvicorn consumidor.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Abrí **http://127.0.0.1:8000**. El snapshot del corpus ya está versionado. La primera instalación necesita internet; la demo extractiva luego funciona sin APIs externas.

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Qué garantía legal tiene un producto nuevo?"}'
```

En PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ask -Method Post -ContentType 'application/json; charset=utf-8' -Body '{"question":"¿Qué garantía legal tiene un producto nuevo?"}'
```

## Qué demuestra

| Capacidad | Implementación |
|---|---|
| Ingesta trazable | Fuente oficial allowlisted, fecha UTC, SHA-256 del HTML y del corpus, validación estructural |
| Chunking legal | Un bloque por artículo, conservando bis/ter/quáter y notas de modificaciones |
| Recuperación híbrida | BM25 + TF-IDF de caracteres; opción BM25 + embeddings multilingües |
| Ranking | Reciprocal Rank Fusion, búsqueda explícita por artículo y fusión de consultas |
| Flujo agéntico | Planificador → herramienta de búsqueda → recuperación correctiva limitada → composición → validación |
| Grounding | ID de evidencia existente y cita textual exacta; fallback extractivo ante error |
| Observabilidad | Pasos y consultas ejecutadas, IDs recuperados, modo, backend, latencia y versión del corpus |
| Evaluación | Dataset versionado, Hit@5, MRR@5, abstención y tests automatizados |
| Seguridad | Sin herramientas de ejecución, sin navegación libre, secretos por entorno, límites y salida DOM segura |

## Arquitectura

```mermaid
flowchart LR
    A[Fuente oficial] --> B[Ingesta por artículo]
    B --> C[Snapshot + manifiesto SHA-256]
    U[Consulta] --> S[Control de alcance]
    S --> P[Planificador: reglas o LLM]
    P --> R[Herramienta search: BM25 + segundo ranking]
    C --> R
    R --> F[Fusión RRF]
    F --> D{Evidencia escasa?}
    D -->|Sí: una búsqueda extra| R2[Recuperación correctiva]
    D -->|No| G[Composición]
    R2 --> G
    G --> V[Validación de citas]
    V -->|Error o timeout| E[Respuesta extractiva]
    V -->|Válida| O[Respuesta + evidencia + traza]
    E --> O
```

La demo sin claves utiliza planificación por reglas y fragmentos textuales. **Ese modo es un baseline de recuperación y composición extractiva, no una demostración de razonamiento de un LLM.** En modo LLM, el modelo selecciona consultas y redacta explicaciones; el código controla las herramientas y los presupuestos. No se usa un framework de agentes: el grafo pequeño es explícito y testeable.

Límites por consulta: hasta 3 búsquedas planificadas, una búsqueda correctiva, 5 artículos, 2 llamadas LLM de hasta 1.500 tokens de salida y timeout de 25 segundos por llamada. Las trazas son registros de acciones, no cadenas privadas de razonamiento.

## Modos de ejecución

### 1. Baseline sin claves (predeterminado)

BM25 + TF-IDF de caracteres con n-gramas 3–5 y RRF. Ambos componentes son **léxicos**: no se presentan como embeddings semánticos. La respuesta contiene pasajes recuperados, no una opinión jurídica generada.

### 2. Embeddings multilingües opcionales

```bash
uv sync --frozen --extra semantic
# Linux/macOS:
export EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# PowerShell:
$env:EMBEDDING_MODEL='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
```

Ejecutá el servidor con la misma variable. Este modo reemplaza TF-IDF por similitud coseno entre embeddings normalizados y conserva BM25 + RRF. La primera ejecución descarga el modelo; puede consumir varios cientos de MB. `trust_remote_code=False`. Revisá licencia y procedencia antes de cambiarlo. Los embeddings se generan en memoria al arrancar, sin base vectorial externa: para 75 bloques es una elección deliberada. Artículos largos pueden superar la ventana del encoder; BM25 sigue viendo el artículo completo. Para un corpus mayor conviene dividir por incisos y persistir el índice.

### 3. Planificación y generación con LLM

Configurá un proveedor compatible con Chat Completions y `response_format=json_object`:

```powershell
$env:GENERATION_BACKEND='llm'
$env:LLM_BASE_URL='https://api.openai.com/v1'
$env:LLM_MODEL='<modelo-disponible-en-tu-proveedor>'
$env:LLM_API_KEY='<tu-clave>'
uv run uvicorn consumidor.api:app --app-dir src --host 127.0.0.1 --port 8000
```

En bash usá `export NOMBRE=valor`. `.env.example` es una referencia; **no se carga automáticamente**. Nunca pegues claves en archivos versionados. El frontend no recibe la clave. Este modo envía pregunta y evidencia al proveedor configurado y puede generar costos. No ingreses información personal.

Si el plan es inválido, hay timeout o la cita no existe literalmente, se retorna evidencia extractiva con `fallback=true`. La validación comprueba **procedencia textual**, no que la explicación del modelo sea lógicamente implicada por la cita. Se requiere revisión humana. El modo LLM se prueba con dobles controlados; no se ha validado contra un proveedor pago en esta versión.

## Corpus y actualización

Fuente: [texto actualizado oficial de la Ley 24.240](https://www.argentina.gob.ar/normativa/nacional/ley-24240-638/actualizacion). Snapshot del **14 de noviembre de 2026**, 75 bloques; [manifiesto](data/manifest.json).

El sitio oficial contiene dos artículos numerados 66 y una nota que lo explica: se conservan como `66` y `66 cierre`, con IDs distintos. Se excluyen navegación y antecedentes normativos históricos de la recuperación. Se conservan notas de modificaciones presentes dentro del texto; no se reinterpretan como un historial normativo completo.

Para los módulos CLI, agregá `src` a `PYTHONPATH`:

```powershell
$env:PYTHONPATH='src'
uv run python -m consumidor.ingest
uv run python -m consumidor.evaluate --output evals/latest.json
```

```bash
PYTHONPATH=src uv run python -m consumidor.ingest
PYTHONPATH=src uv run python -m consumidor.evaluate --output evals/latest.json
```

Revisá el diff del corpus y el resultado de evaluación antes de versionar una actualización. La descarga falla si cambia la estructura o hay duplicados inesperados. `data/raw/` se excluye de Git; se publica el corpus normalizado y sus hashes. SHA-256 detecta modificaciones accidentales respecto del manifiesto; no es una firma de autenticidad frente a un atacante que cambie ambos archivos.

## Tests y evaluación

```bash
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
PYTHONPATH=src uv run python -m consumidor.evaluate --output evals/latest.json
uv run bandit -r src -q
uv run pip-audit
```

En PowerShell configurá `$env:PYTHONPATH='src'` antes del evaluador. La suite cubre integridad del corpus, búsqueda por artículo, grounding de citas, inyección básica, timeouts del proveedor, validación HTTP y rate limiting. Los fallos bloquean CI.

Baseline reproducible en [evals/baseline.json](evals/baseline.json):

| Métrica | Resultado | Muestra |
|---|---:|---:|
| Hit@5 | 1,0000 | 15 consultas con artículo esperado |
| MRR@5 | 0,7222 | Las mismas 15 consultas |
| Abstención fuera de alcance | 1,0000 | 3 consultas negativas |

Dataset pequeño, escrito para este proyecto y usado durante desarrollo: **no es un conjunto de prueba independiente ni permite afirmar calidad jurídica o precisión de producción**. Hit@5 mide si aparece al menos un artículo anotado; no mide exhaustividad ni calidad de la explicación. Los resultados publicados corresponden al baseline léxico y extractivo; no al encoder ni a un LLM real. La latencia depende del hardware y excluye el arranque del índice.

## Seguridad y despliegue

Leé [SECURITY.md](SECURITY.md) para el modelo de amenazas y las limitaciones. El servidor arranca en localhost; esta versión no tiene autenticación y **no está preparada para exponer una API paga directamente a internet**. Para un despliegue público agregá HTTPS, autenticación, límites distribuidos, presupuesto del proveedor y monitoreo sin datos sensibles. No se publica ni despliega automáticamente desde este repositorio.

El contenedor ejecuta el baseline como usuario sin privilegios:

```bash
docker build -t consumidor-rag .
docker run --rm -p 127.0.0.1:8000:8000 consumidor-rag
```

## Recorrido para entrevistas

1. Ejecutar la demo y consultar garantía de un producto.
2. Abrir evidencia y mostrar la fecha del corpus y el texto del artículo 11.
3. Inspeccionar la traza: plan, consultas y rankings fusionados.
4. Consultar algo fuera de alcance y explicar la abstención heurística.
5. Correr tests y evaluación; discutir la diferencia entre recuperar evidencia y validar una afirmación.
6. Leer [decisiones de arquitectura](docs/architecture.md) y [próximas mejoras](docs/roadmap.md).

## Estructura

```text
src/consumidor/    ingesta, recuperación, agente, API y evaluación
web/              interfaz sin frameworks ni scripts de terceros
data/             snapshot oficial normalizado y manifiesto
evals/            dataset y baseline medido
tests/            pruebas funcionales y de seguridad
docs/             decisiones, limitaciones y roadmap
.github/          CI, revisión de dependencias y plantillas
```

## Licencia

Código bajo [MIT](LICENSE). El texto normativo se atribuye a la fuente oficial y no se presenta como contenido propio; ver [data/README.md](data/README.md). Sin afiliación con organismos públicos.
