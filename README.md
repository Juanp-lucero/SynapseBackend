# SynapseBackend

Backend de Synapse IA. El proyecto principal se encuentra en `SynapseIA/`.

## Despliegue

Desplegado en Vercel:

| | URL | Repositorio |
|---|---|---|
| Aplicación (frontend) | https://synapse-frontend-alpha-khaki.vercel.app | [Juanp-lucero/SynapseFronted](https://github.com/Juanp-lucero/SynapseFronted) |
| API (backend) | https://synapse-backend-eight.vercel.app | [Juanp-lucero/SynapseBackend](https://github.com/Juanp-lucero/SynapseBackend) |
| Estado de la API | https://synapse-backend-eight.vercel.app/health | |
| Documentación de la API | https://synapse-backend-eight.vercel.app/docs | |

Consulta [SynapseIA/README.md](SynapseIA/README.md) para instalación, configuración de PostgreSQL y Neo4j, ejecución de FastAPI y uso de la integración con Groq.

**Seguridad:** no publiques archivos `.env`, claves JWT, contraseñas de bases de datos ni API keys. Usa `SynapseIA/.env.example` como plantilla y configura credenciales propias en tu entorno.

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
