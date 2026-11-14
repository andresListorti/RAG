# Bitácora de Consumidor RAG

## 2026-11-14 — Objetivo y alcance inicial

Se creó el proyecto para un repositorio público llamado `RAG`, como muestra de portfolio para búsquedas laborales que requieran RAG y trabajo agéntico. El usuario autorizó trabajar sobre la Ley de Defensa del Consumidor de Argentina y commitear/pushear a `main`.

Se eligió un alcance controlado: texto actualizado oficial de la Ley 24.240, API FastAPI, interfaz web, búsqueda con evidencia y un flujo de planificación, recuperación, composición y validación. No se incluyeron jurisprudencia, reglamentaciones ni procedimientos provinciales. El producto es educativo y no brinda asesoramiento jurídico.

## 2026-11-14 — Primera implementación publicada

- `f8c0faf`: primera versión ejecutable, corpus, documentación, seguridad, tests y CI.
- `e30e3be`: README completo en inglés y ampliación de las comprobaciones.
- Se conservaron 75 bloques normativos, fecha UTC y hashes del HTML y del corpus. La fuente tiene dos artículos numerados 66: se distinguen `66` y `66 cierre`.
- Se implementó un baseline sin claves con BM25 + TF-IDF de caracteres y RRF, y modos opcionales de embeddings multilingües y generación con LLM.
- Se agregó `README.md` en español y `README.en.md` en inglés, enlazados entre sí.

La revisión inicial distinguió una versión de portfolio básica de una validación completa: faltaban ejecución neural real, inferencia con un LLM real, pruebas de navegador/accesibilidad y arranque efectivo del contenedor. El usuario pidió cerrar esas verificaciones antes de considerar terminado el portfolio.

## 2026-11-14 — Validación real y correcciones

`979d804` incorporó modelos reales, pruebas de navegador, capturas, evaluación ampliada y comprobación de Docker en ejecución.

Resultados comprobados:

- 24 tests Python de integridad, recuperación, alcance, artículos inexistentes, citas, fallos de proveedor, límites HTTP y seguridad.
- 12 pruebas Chromium en escritorio y emulación Pixel 7: consultas, fuentes, artículos completos, trazas, abstención, recuperación ante 429, teclado, ausencia de overflow y salida HTML inerte.
- Auditorías axe antes y después de buscar sin infracciones automáticas en los casos probados. No equivalen a certificación WCAG ni a pruebas en dispositivos físicos o lectores de pantalla.
- Encoder real `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, revisión `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`, 384 dimensiones.
- Ollama real con `qwen3.5:2b`: cuatro casos positivos con búsqueda léxica y cuatro con búsqueda neural, sin fallback, recuperando y citando el artículo esperado. Se verificaron además abstención y un caso adversarial acotado.
- Prueba HTTP real de la API con encoder y LLM combinados, exigiendo generación real sin fallback silencioso.
- Auditorías de dependencias Python/npm y Bandit sin hallazgos conocidos al validar esa versión.

Correcciones que surgieron de estas pruebas:

1. El modelo alteraba citas al copiarlas. Se reemplazó la transcripción por selección de `quote_id` de un catálogo permitido, resuelto por el servidor al texto original.
2. El encoder truncaba artículos por su límite de 128 tokens. Se indexaron 214 ventanas de 96 tokens con paso 64, agregando similitud por artículo padre.
3. La evaluación ampliada detectó problemas de alcance con plurales y vocabulario cotidiano. Se corrigieron el control de alcance y la expansión de consultas.
4. Axe detectó contraste insuficiente. Se corrigieron colores y se repitieron las pruebas. También se corrigió un espacio faltante en el título móvil.
5. La carga inicial del modelo local podía superar el timeout de 25 segundos. Se documentó el calentamiento previo y se mantuvo el fallback; no se eliminó el límite de espera para disimularlo.

## 2026-11-14 — Incidente de CI resuelto

La ejecución del commit `979d804` falló en la comprobación Docker: el puerto publicado reinició una conexión mientras Uvicorn todavía arrancaba. El comprobador no contemplaba ese estado transitorio.

`ac57a67` corrigió la espera acotada para tolerar `ConnectionError` y `TimeoutError`, además de errores URL. La comprobación sigue fallando si el servicio no queda listo o responde incorrectamente.

La [ejecución 43641121762](https://github.com/andresListorti/RAG/actions/runs/43641121762) pasó completa en ese commit: verificación general, navegador, encoder real y contenedor en ejecución. Docker se probó con UID 10001 y raíz de solo lectura; la API respondió consultas, citas y abstención. El aviso por correo del fallo anterior era histórico, no el estado de la versión corregida.

## 2026-11-14 — Métricas y límites

| Backend | Hit@5 desarrollo | MRR@5 desarrollo | Hit@5 desafío | MRR@5 desafío |
|---|---:|---:|---:|---:|
| BM25 + TF-IDF de caracteres | 1,0000 | 0,7889 | 1,0000 | 0,8247 |
| BM25 + ventanas multilingües | 1,0000 | 0,8333 | 0,9200 | 0,7447 |

Hay 18 casos iniciales y 30 de desafío: 40 positivos y ocho negativos en total. Ambos backends se abstuvieron en los ocho negativos. Los conjuntos fueron escritos y usados durante desarrollo, también para corregir el sistema: **no son una evaluación independiente ni una garantía de calidad jurídica**. El backend neural no mejora todas las métricas; el predeterminado permanece léxico.

Las citas auténticas prueban procedencia, no implicación lógica ni preservación de todas las condiciones legales en la explicación. No existe revisión jurídica independiente, certificación de precisión legal ni actualización automática del corpus. No se validó un proveedor LLM pago. La evidencia detallada y los comandos están en [docs/validation.md](docs/validation.md) y los informes de `evals/`.

## 2026-11-14 — Estado de portfolio

Se considera listo para mostrar como **“RAG agéntico auditable sobre defensa del consumidor argentino”**: demo reproducible, modelos reales, fuentes visibles, trazas, tests, seguridad básica, contenedor comprobado y documentación bilingüe.

Esta aceptación se refiere al portfolio técnico. No equivale a un servicio jurídico de producción ni a un lanzamiento comercial. Las afirmaciones de validación anteriores describen los commits y ejecuciones citados; deben actualizarse cuando cambie el comportamiento.

## 2026-11-14 — Posicionamiento para Agensi

El usuario consultó si era un producto vendible en Agensi. La recomendación registrada es usarlo como **demo funcional para vender servicios de asistentes documentales con IA**, ofreciendo implementación, adaptación y mantenimiento según cada cliente.

Aplicaciones posibles para explorar comercialmente: consulta de documentación interna, soporte y procedimientos con respuestas respaldadas por fuentes. Son oportunidades propuestas, no funcionalidades o contratos ya vendidos.

Antes de ofrecerlo como servicio operativo quedan pendientes:

- Autenticación/autorización y aislamiento de datos por cliente.
- Hosting, HTTPS, monitoreo y operación.
- Límites distribuidos, presupuestos de tokens y control de costos.
- Privacidad, retención de datos, soporte y mantenimiento.
- Para la versión jurídica: revisión profesional, actualización normativa y alcance contractual claro.

No se acordaron precio, lanzamiento, despliegue público, clientes ni contratación de infraestructura. El repositorio público no implica que la aplicación esté publicada como servicio.

## 2026-11-14 — Preferencias de colaboración

El usuario pidió avisos de avance y confirmación del primer push; buen README en español e inglés; tests y medidas de seguridad; y correo desde su cuenta personal hacia sí mismo al terminar o ante bloqueos que requieran intervención. Se enviaron avisos de permisos y resúmenes de cierre mediante la conexión autorizada, sin registrar la dirección personal en este repositorio público.

También se consultaron aprobaciones desde Android. La guía oficial consultada indica que pueden revisarse mediante Codex/Remote tras vincular el teléfono con el host; no se verificó en esta colaboración el emparejamiento concreto del dispositivo.

Las instrucciones operativas para futuros trabajos están en [AGENTS.md](AGENTS.md). Mantener esta bitácora como historial de decisiones y evidencia, diferenciando hechos comprobados de recomendaciones y pendientes.
