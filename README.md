# TranscriptCSV

Aplicación de escritorio para abrir, visualizar y transformar archivos CSV con datos de productos y categorías. La herramienta detecta la codificación y el delimitador automáticamente, reestructura columnas de edad y clasificación, y permite exportar el resultado a un nuevo CSV.

## Características

- Carga de archivos CSV desde el sistema
- Detección automática de codificación con `chardet`
- Soporte para delimitadores `,` y `;`
- Transformación de columnas como edad, categoría y clasificación BISACT
- Vista tabular con `PyQt5`
- Exportación del archivo transformado a CSV

## Tecnologías

- Python
- PyQt5
- pandas
- chardet

## Requisitos

- Python 3.10 o superior
- pip

## Instalación

```bash
pip install pandas pyqt5 chardet
```

## Ejecución

```bash
python main.py
```

## Nota

Los archivos de datos locales grandes, como exportaciones CSV o SQL, quedan excluidos del repositorio para evitar problemas de tamaño en GitHub.
