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
