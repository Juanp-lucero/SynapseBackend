# Comprobaciones manuales

Scripts para revisar a mano cada parte del pipeline con datos locales. No son pruebas automáticas: las pruebas de pytest están en `tests/`.

Se ejecutan desde la raíz del repositorio, con el entorno virtual activo y `.env` configurado:

```bash
python -m scripts.manual.check_entity_extractor
python -m scripts.manual.check_neo4j
```

`check_processor.py` necesita un archivo real en `uploads/`; cambia la ruta dentro del script antes de usarlo.
