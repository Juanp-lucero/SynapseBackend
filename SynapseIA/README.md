# Synapse IA · Backend

Backend de Synapse IA para procesar documentos, extraer entidades, identificar relaciones y patrones, generar hipótesis y consultar un grafo de conocimiento.

## Tecnologías

- FastAPI y SQLAlchemy
- PostgreSQL para usuarios, proyectos, fuentes e historiales
- Neo4j para el grafo de conocimiento
- Groq para resúmenes y preguntas en lenguaje natural basadas en resultados extraídos

## Instalación

Desde la carpeta `SynapseIA`:

```bash
python -m venv .venv

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Copia `.env.example` como `.env` y configura PostgreSQL, Neo4j y Groq. No subas `.env` a Git.

## Variables de entorno

- `DATABASE_URL`: URL de conexión a PostgreSQL.
- `SECRET_KEY`: clave aleatoria y privada para JWT.
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`: conexión al grafo.
- `GROQ_API_KEY`: clave privada de Groq.
- `GROQ_MODEL`: modelo de lenguaje. Valor por defecto: `llama-3.3-70b-versatile`.

Obtén una clave desde https://console.groq.com/keys.

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Documentación: http://127.0.0.1:8000/docs

## Flujo de análisis

1. Un usuario autenticado carga un documento a un proyecto propio.
2. El procesador extrae texto del archivo.
3. El pipeline determinístico identifica entidades, relaciones, patrones e hipótesis.
4. Los resultados se guardan en PostgreSQL y se intenta sincronizar el grafo en Neo4j.
5. Groq puede generar un resumen explicativo fundamentado en los resultados estructurados.

Groq no reemplaza el pipeline extractor ni se utiliza para inventar relaciones. Si el servicio no está configurado o falla, el análisis estructurado se conserva.

## Endpoints de IA

Todos los endpoints de IA requieren autenticación.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/ai/status` | Verifica si Groq está configurado sin exponer la clave. |
| POST | `/ai/source/{source_id}/summary` | Genera un resumen del análisis más reciente de una fuente propia. |
| POST | `/ai/source/{source_id}/ask` | Responde una pregunta usando las entidades, relaciones, patrones e hipótesis del último análisis. |

Ejemplo de pregunta:

```json
{
  "question": "¿Qué patrones principales se identificaron en este documento?"
}
```

Los endpoints devuelven `503` cuando no hay clave de Groq y `502` cuando el proveedor no está disponible. Las respuestas se generan bajo demanda y no se guardan en base de datos por defecto.

## Seguridad importante

El archivo `.env` no debe versionarse. Si una credencial real estuvo publicada en Git, cambiarla en el archivo no revoca la credencial anterior: debes rotarla en PostgreSQL, Neo4j y el proveedor correspondiente. La clave JWT también debe reemplazarse para invalidar tokens firmados con la clave expuesta.
