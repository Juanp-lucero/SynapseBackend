# Synapse IA · Backend

Backend de Synapse IA para procesar documentos, extraer entidades, identificar relaciones y patrones, generar hipótesis y consultar un grafo de conocimiento.

## Despliegue

Desplegado en Vercel:

| | URL | Repositorio |
|---|---|---|
| Aplicación (frontend) | https://synapse-frontend-alpha-khaki.vercel.app | [Juanp-lucero/SynapseFronted](https://github.com/Juanp-lucero/SynapseFronted) |
| API (backend) | https://synapse-backend-eight.vercel.app | [Juanp-lucero/SynapseBackend](https://github.com/Juanp-lucero/SynapseBackend) |
| Estado de la API | https://synapse-backend-eight.vercel.app/health | |
| Documentación de la API | https://synapse-backend-eight.vercel.app/docs | |

## Cuenta de prueba

Para revisar Synapse IA sin registrarse:

| Aplicación | Correo | Contraseña |
|---|---|---|
| https://synapse-frontend-alpha-khaki.vercel.app | `profesor.demo@example.com` | `ProfeDemo2026*` |

Es una cuenta de demostración creada solo para la evaluación; no contiene datos personales.

## Cómo probarlo

1. Entra a https://synapse-frontend-alpha-khaki.vercel.app e inicia sesión con la [cuenta de prueba](#cuenta-de-prueba) (o crea una cuenta en **Crear cuenta**).
2. **Proyectos → Nuevo proyecto**: por ejemplo `Investigación Colombia`, y pulsa **Crear proyecto**.
3. **Fuentes**: elige el proyecto, selecciona el documento y pulsa **Cargar fuente**. Sirve un PDF, DOCX, TXT o CSV. Para una prueba rápida, guarda este texto como `prueba.txt`:

   ```text
   Gabriel García Márquez nació en Aracataca, Colombia, en 1927.
   Trabajó como periodista en El Espectador en Bogotá.
   La Universidad Nacional de Colombia lo homenajeó en 1982, el mismo año en que recibió el Nobel.
   ```

4. En la fuente, pulsa **Analizar**. En **Análisis** aparecen las entidades (personas, lugares, organizaciones, años), las relaciones, los patrones y las hipótesis. Lo que encontró la IA lleva la etiqueta **IA**.
5. En el panel **Interpretación con IA**: **Generar resumen** o escribe una pregunta, por ejemplo *¿Qué organizaciones aparecen?*
6. **Explorar Knowledge Graph**:
   - la leyenda filtra por tipo (los números sueltos empiezan ocultos);
   - **Buscar** centra un nodo; **Ajustar**, **Reorganizar** y **Exportar PNG** controlan la vista;
   - al hacer clic en un nodo o una relación se abre su detalle;
   - con dos o más fuentes, la línea punteada morada une los documentos que comparten entidades.

## Cómo funciona

```
Angular (Vercel) ──REST + JWT──▶ FastAPI (Vercel) ──▶ PostgreSQL (Neon)
                                       │
                                       └──▶ Groq (IA, opcional)
```

1. **Carga:** el backend extrae el texto del archivo (PDF, DOCX, TXT o CSV) y lo guarda en la base de datos junto a la fuente.
2. **Análisis por reglas:** siempre se ejecuta. Detecta nombres propios, organizaciones, años, números, métricas y categorías, y las relaciones entre ellos (por ejemplo, nombres mencionados en la misma oración).
3. **Análisis con IA:** si hay `GROQ_API_KEY`, el modelo `openai/gpt-oss-120b` devuelve entidades, relaciones e hipótesis en JSON. El backend lo valida antes de guardarlo:
   - cada entidad tiene que aparecer en el texto;
   - cada relación debe unir entidades válidas;
   - la confianza se limita entre 0 y 1.
   Si Groq falla o no está configurado, se usa solo el resultado por reglas. Si el modelo configurado deja de existir, el backend prueba otro automáticamente.
4. **Knowledge Graph:** se construye con los análisis guardados en PostgreSQL. Une las entidades repetidas y conecta los documentos que comparten entidades. Neo4j es opcional.
5. **Resumen y preguntas:** la IA responde solo con la evidencia extraída de esa fuente y del usuario autenticado. El texto de los documentos se trata como dato, nunca como instrucción.

## Estructura

```
.
├── app/
│   ├── api/          # Rutas FastAPI (auth, proyectos, fuentes, análisis, grafo, IA)
│   ├── core/         # Configuración y seguridad (JWT)
│   ├── database/     # Conexiones a PostgreSQL y Neo4j
│   ├── models/       # Modelos SQLAlchemy
│   ├── schemas/      # Esquemas Pydantic
│   ├── services/     # Extracción, análisis, grafo e integración con Groq
│   └── main.py       # Punto de entrada (también para Vercel)
├── scripts/manual/   # Comprobaciones manuales (no forman parte de pytest)
├── tests/            # Pruebas automáticas (pytest)
├── .env.example
├── pytest.ini
└── requirements.txt
```

## Tecnologías

- FastAPI y SQLAlchemy
- PostgreSQL para usuarios, proyectos, fuentes, análisis y el grafo de conocimiento
- Neo4j (opcional) como almacenamiento alterno del grafo
- Groq para resúmenes y preguntas en lenguaje natural basadas en resultados extraídos

## Instalación

Desde la raíz del repositorio:

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
- `GROQ_MODEL`: modelo de lenguaje. Valor por defecto: `openai/gpt-oss-120b`.

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
4. Los resultados se guardan en PostgreSQL; si Neo4j está configurado, también se sincroniza el grafo.
5. Groq puede generar un resumen explicativo fundamentado en los resultados estructurados.

La IA complementa el pipeline extractor: lo que devuelve se valida contra el texto antes de guardarse. Si el servicio no está configurado o falla, el análisis estructurado se conserva.

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
