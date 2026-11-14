# Guía de trabajo del repositorio

## Objetivo y posicionamiento

Consumidor RAG es una demostración de portfolio de ingeniería RAG y trabajo agéntico sobre la Ley 24.240 de Defensa del Consumidor de Argentina. El repositorio es público: no incluir secretos, datos personales, conversaciones privadas ni credenciales en código, informes, capturas o historial.

El proyecto se considera apto para portfolio por su implementación reproducible y la evidencia de validación registrada en `docs/validation.md`. No describirlo como un servicio jurídico de producción ni como un producto comercial listo para clientes.

Para Agensi, el posicionamiento acordado es una **demo funcional de asistentes documentales con IA**, útil para mostrar capacidades y ofrecer implementación, adaptación y mantenimiento por cliente. La comercialización efectiva aún requiere trabajo adicional; no implica que ya exista un lanzamiento o una oferta publicada.

## Leer antes de continuar

- `BITACORA.md`: decisiones, avances, correcciones y estado comercial.
- `README.md` y `README.en.md`: instrucciones públicas en español e inglés; mantenerlas coherentes.
- `docs/validation.md`: resultados reales, comandos y límites de las pruebas.
- `docs/architecture.md`, `docs/roadmap.md` y `SECURITY.md`: arquitectura, trabajo pendiente y amenazas.

## Invariantes técnicos

- Fuente oficial con fecha, procedencia y hashes. Revisar el diff de una nueva ingesta antes de versionarla.
- Conservar ambos artículos 66 y distinguir el artículo de cierre, tal como documenta la fuente oficial.
- Mantener una demo extractiva sin claves. El baseline predeterminado combina BM25 y TF-IDF de caracteres: ambos son léxicos; no llamarlos embeddings semánticos.
- El modo neural usa el encoder multilingüe con revisión fijada, ventanas solapadas y recuperación del artículo padre. Usar `uv run --extra semantic` para conservar sus dependencias opcionales.
- El modelo selecciona IDs de pasajes permitidos; el servidor resuelve las citas originales. No aceptar citas inventadas o IDs ajenos a la evidencia recuperada.
- Mantener presupuestos acotados de búsquedas, llamadas LLM, tamaño de entrada y concurrencia, y fallback extractivo observable.
- Proveedores remotos por HTTPS. HTTP únicamente con opt-in explícito e IP literal de loopback para Ollama; no ampliar esa excepción a hosts arbitrarios.
- No renderizar contenido del usuario o del modelo como HTML ejecutable.
- La procedencia exacta de una cita no prueba la corrección de una explicación. No afirmar validación jurídica independiente ni cobertura completa de normativa argentina.

## Verificación proporcional a los cambios

Para cambios funcionales, ejecutar los checks relevantes y actualizar la evidencia si cambia el comportamiento:

```bash
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run bandit -r src -q
uv run pip-audit
npm ci
npm run test:e2e
```

Instalar Chromium con `npx playwright install chromium` cuando corresponda. El CI también ejecuta auditoría npm, el encoder real y el contenedor con usuario no privilegiado y raíz de solo lectura. Mantener una espera de arranque acotada que tolere conexiones reiniciadas mientras inicia Uvicorn; no ocultar errores posteriores de la API.

Para cambios del modo LLM, usar `scripts/validate_llm.py` con un modelo real disponible y revisar los informes. Un fallback no cuenta como prueba exitosa de generación real. Para cambios del índice neural, ejecutar `scripts/validate_semantic.py`. No usar APIs pagas sin autorización de costos y credenciales disponibles para ese fin.

No ejecutar modelos ni suites completas por cambios exclusivamente documentales: comprobar exactitud, enlaces y `git diff --check` suele ser suficiente. No presentar un resultado anterior como una nueva ejecución.

Los conjuntos de evaluación fueron usados durante desarrollo: no son benchmarks independientes. Mantener visibles los fallos, los tamaños de muestra y la comparación entre backends; no prometer precisión jurídica a partir de Hit@5.

## Colaboración y publicación

- El usuario autorizó en esta colaboración commits y pushes a `main` del repositorio público. Mantener cambios revisables y no hacer force-push ni reescribir el historial sin indicación expresa.
- Avisar de avances relevantes y confirmar un push solo después de verificarlo.
- Se pidió aviso por correo desde la cuenta personal hacia la misma cuenta al terminar el trabajo o ante bloqueos que requieran intervención. Usar la conexión autorizada y confirmar el envío; no publicar la dirección personal en el repositorio. Si hace falta una nueva aprobación que puede detener el trabajo, enviar el aviso antes de quedar esperando cuando sea posible.
- No volver a pedir permisos ya concedidos; respetar siempre las restricciones efectivas del entorno.
- Registrar decisiones importantes y nuevas limitaciones en `BITACORA.md`. Diferenciar tareas completadas, recomendaciones y trabajo futuro.

## Antes de vender como servicio operativo

Quedan pendientes autenticación/autorización, aislamiento de datos por cliente, hosting con HTTPS, cuotas distribuidas y presupuestos de uso, monitoreo, política de privacidad/retención, soporte y mantenimiento. Para una oferta jurídica específica, agregar revisión profesional, proceso de actualización normativa y alcance contractual definido. No presentar estos puntos como implementados.
