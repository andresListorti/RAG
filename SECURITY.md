# Seguridad

## Alcance y supuestos

Demo local educativa. No almacena conversaciones ni requiere PII. El corpus es público. Se considera no confiable la pregunta del usuario, la respuesta del LLM y el HTML descargado. Las variables de entorno, la configuración del proveedor y los archivos del repositorio son administrados por el operador.

| Amenaza | Control implementado | Límite conocido |
|---|---|---|
| Exposición de claves | Variables de entorno; `.env*` ignorados; clave solo backend | No protege un host comprometido; revisar commits antes de publicar |
| Prompt injection | Herramientas cerradas: solo búsqueda; datos separados del prompt; citas verificadas | Un LLM puede redactar una afirmación incorrecta con una cita auténtica |
| SSRF / exfiltración | El usuario no puede elegir URL; ingesta fija; proveedor definido por operador, HTTPS sin credenciales en URL | No usar una configuración de proveedor de origen no confiable |
| Redirección del proveedor | No se siguen redirecciones HTTP con Authorization | El proveedor configurado recibe consulta y contexto |
| XSS | DOM con `textContent`; no render de HTML/Markdown del modelo; URLs de fuente fijas; CSP | CSP no reemplaza una revisión de frontend |
| Abuso / costos | 1.500 caracteres; cuerpo máximo 8 KiB; 20 peticiones/minuto globales por proceso; 2 consultas concurrentes | Límites en memoria, no distribuidos; sin cuentas ni presupuesto diario |
| Respuesta excesiva / loops | Hasta 2 llamadas LLM, 25 s/call, 1.500 tokens/call; respuesta leída hasta 100 KB; búsquedas acotadas | Los timeouts son de socket, no un deadline total de la solicitud |
| Corpus alterado | SHA-256 y estructura validada al inicio | No son firmas; un atacante puede cambiar corpus y manifiesto juntos |
| Dependencias vulnerables | Lockfile, auditoría en CI, Bandit, Dependabot | Ningún escáner garantiza ausencia de vulnerabilidades |
| Filtración de errores | Excepciones del proveedor no se devuelven; sin logs de prompts | Los logs del proxy/proveedor dependen del operador |

No hay subida de documentos, ejecución de comandos, escritura de archivos por consultas, navegación web del agente, ni herramientas con acceso a correo o repositorios. El LLM no recibe la clave dentro del prompt. La clave se envía al endpoint configurado como cabecera de autenticación.

## Antes de exponer a internet

- Autenticación/autorización y HTTPS en un reverse proxy.
- Límite distribuido por cuenta, límites de conexión/cuerpo/tiempo en proxy y presupuesto de tokens del proveedor.
- Deshabilitar o proteger la documentación de API si corresponde.
- Política de privacidad y retención del proveedor, sin registrar consultas con datos personales.
- Revisión de dependencias e imágenes; gestión de secretos fuera del repositorio.
- Evaluación jurídica y de grounding más amplia, incluyendo casos adversariales.

La abstención usa reglas de alcance y coincidencia léxica. No distingue de forma robusta una pregunta irrelevante que incluya vocabulario de consumo. No usar como filtro de seguridad de alta confianza.

## Reportar un problema

No publiques claves, datos personales ni detalles explotables en un issue público. Usá la opción de reporte privado de vulnerabilidades de GitHub si está habilitada en el repositorio; si no, contactá al propietario por su perfil público sin compartir secretos. Revocá inmediatamente cualquier clave expuesta y revisá el historial, no solo el último commit.
