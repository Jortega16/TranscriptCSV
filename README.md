# TranscriptCSV

TranscriptCSV es una herramienta de escritorio desarrollada en Python para abrir archivos CSV, visualizar sus datos en una tabla y aplicar transformaciones de contenido antes de exportarlos nuevamente. Está orientada a procesos de limpieza y normalización de datos catalogados, especialmente para archivos con categorías, edades y clasificación BISACT.

## ¿Qué hace?

- Carga archivos CSV desde el sistema.
- Detecta automáticamente la codificación del archivo mediante `chardet`.
- Intenta leer el CSV con diferentes delimitadores (` , ` y ` ; `).
- Normaliza campos relacionados con edades y categorías.
- Genera columnas derivadas para clasificaciones tipo BISACT.
- Muestra el resultado en una tabla visual con `PyQt5`.
- Permite guardar el archivo transformado como CSV nuevo.

## Casos de uso

Este proyecto resulta útil para:

- Limpieza de exportaciones de productos.
- Normalización de datos para catálogos editoriales.
- Reorganización de información antes de cargarla en otra herramienta.
- Revisiones visuales rápidas de archivos CSV grandes.

## Stack tecnológico

- Python
- PyQt5
- pandas
- chardet

## Requisitos

- Python 3.10 o superior
- pip
- Entorno virtual recomendado

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas pyqt5 chardet
```

## Ejecución

```bash
python main.py
```

## Estructura del proyecto

- `main.py`: versión principal de la interfaz gráfica con vista de tabla.
- `main2.py`: alternativa o versión de pruebas.
- `main3.py`: otra variante del visor/exportador.
- `.gitignore`: excluye artefactos locales y archivos pesados.
- `README.md`: documentación del proyecto.

## Nota importante

Los datos grandes o exportaciones locales no se suben al repositorio para evitar el límite de tamaño de GitHub. El proyecto está pensado para trabajar con archivos locales en tu máquina.

## Licencia

Este proyecto se distribuye sin una licencia formal definida en este repositorio.
