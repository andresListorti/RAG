# Decisiones de arquitectura

## Corpus pequeño y verificable

La primera versión cubre una sola ley. Se conserva cada artículo completo para evidencia y BM25. El encoder opcional usa ventanas solapadas de 96 tokens, paso 64, con máxima similitud por artículo padre. Esto evita truncar artículos al límite de 128 tokens del modelo probado. Los incisos y las notas se conservan en la evidencia visible; una futura comparación puede evaluar segmentación estructural frente a ventanas de tokens.

## Recuperación sin infraestructura externa

BM25 implementado sobre frecuencias + TF-IDF de caracteres ofrece un baseline offline barato. RRF combina posiciones sin comparar escalas incompatibles. Con embeddings habilitados, el segundo ranking cambia por similitud coseno multilingüe. No se necesita una base vectorial para 75 bloques; una matriz en memoria simplifica ejecución y pruebas. El filtro léxico conserva trazabilidad, pero limita la recuperación puramente semántica: medir ese tradeoff antes de eliminarlo.

## Orquestación explícita

El planificador LLM devuelve consultas JSON; no nombres de funciones ni código. La única herramienta ejecutable es `Retriever.search`. El orquestador permite hasta tres consultas más una corrección si hay menos de dos evidencias. La ruta offline usa expansión por temas. Esa expansión es una heurística observable, no una inferencia aprendida.

Se elige una implementación pequeña frente a LangGraph/LangChain para mostrar las transiciones y evitar infraestructura innecesaria. Un grafo con checkpointing sería útil si se incorporan herramientas múltiples, tareas duraderas o aprobación humana.

## Integridad de citas y límites de grounding

El generador selecciona un ID de un catálogo de pasajes creado por el servidor. Solo IDs permitidos se resuelven a texto original y documento recuperado; luego se verifica la cita exacta. Si falla, toda la respuesta vuelve a extractiva. Esta decisión surgió de probar un LLM real que modificaba citas al copiarlas. Evita citas fabricadas, pero NO prueba que la explicación se deduzca de ellas. Una evaluación de entailment y revisión humana siguen siendo necesarias.

El truncado de contexto LLM a 12.000 caracteres por artículo y de fragmentos extractivos a 1.600 caracteres se hace explícito. La interfaz permite abrir el artículo completo. Nunca se promete que un fragmento incluya todas las excepciones.

## Privacidad por defecto

No hay persistencia de preguntas ni telemetría propia de contenido. En modo extractivo no hay llamadas de red durante consultas. En modo LLM el proveedor recibe pregunta y texto normativo. El frontend usa APIs DOM seguras y no incorpora SDKs externos, fuentes remotas ni analytics.
