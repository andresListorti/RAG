# Decisiones de arquitectura

## Corpus pequeño y verificable

La primera versión cubre una sola ley. Esto permite revisar los bloques y reproducir evaluaciones. Se indexa cada artículo completo para preservar excepciones y notas. El costo es que artículos largos pueden diluir ranking y exceder la ventana del encoder opcional. La siguiente iteración debería usar subchunks por inciso con recuperación del artículo padre.

## Recuperación sin infraestructura externa

BM25 implementado sobre frecuencias + TF-IDF de caracteres ofrece un baseline offline barato. RRF combina posiciones sin comparar escalas incompatibles. Con embeddings habilitados, el segundo ranking cambia por similitud coseno multilingüe. No se necesita una base vectorial para 75 bloques; una matriz en memoria simplifica ejecución y pruebas. El filtro léxico conserva trazabilidad, pero limita la recuperación puramente semántica: medir ese tradeoff antes de eliminarlo.

## Orquestación explícita

El planificador LLM devuelve consultas JSON; no nombres de funciones ni código. La única herramienta ejecutable es `Retriever.search`. El orquestador permite hasta tres consultas más una corrección si hay menos de dos evidencias. La ruta offline usa expansión por temas. Esa expansión es una heurística observable, no una inferencia aprendida.

Se elige una implementación pequeña frente a LangGraph/LangChain para mostrar las transiciones y evitar infraestructura innecesaria. Un grafo con checkpointing sería útil si se incorporan herramientas múltiples, tareas duraderas o aprobación humana.

## Integridad de citas y límites de grounding

Cada claim generado debe referenciar un documento recuperado y contener una cita continua que exista en él. Si no pasa, toda la respuesta vuelve a extractiva. Esto previene citas fabricadas, pero NO prueba que la afirmación se deduzca de la cita. Una evaluación de entailment y revisión humana son futuras capas necesarias.

El truncado de contexto LLM a 12.000 caracteres por artículo y de fragmentos extractivos a 1.600 caracteres se hace explícito. La interfaz permite abrir el artículo completo. Nunca se promete que un fragmento incluya todas las excepciones.

## Privacidad por defecto

No hay persistencia de preguntas ni telemetría propia de contenido. En modo extractivo no hay llamadas de red durante consultas. En modo LLM el proveedor recibe pregunta y texto normativo. El frontend usa APIs DOM seguras y no incorpora SDKs externos, fuentes remotas ni analytics.
