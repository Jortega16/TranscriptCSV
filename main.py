import sys
import pandas as pd
import chardet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel


class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(PandasModel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(section + 1)
        return None


class CSVViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Layout principal
        layout = QVBoxLayout()

        # Botón para cargar archivo CSV
        self.loadButton = QPushButton('Cargar CSV', self)
        self.loadButton.clicked.connect(self.loadCSV)
        layout.addWidget(self.loadButton)

        # Botón para exportar archivo CSV
        self.exportButton = QPushButton('Exportar CSV', self)
        self.exportButton.clicked.connect(self.exportCSV)
        layout.addWidget(self.exportButton)

        # Vista para mostrar los datos
        self.tableView = QTableView()
        layout.addWidget(self.tableView)

        self.setLayout(layout)
        self.setWindowTitle('Visualizador de CSV')
        self.resize(800, 600)

    def loadCSV(self):
        # Diálogo para seleccionar archivo CSV
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo CSV', '', 'CSV Files (*.csv);;All Files (*)',
                                                  options=options)

        if fileName:
            # Detectar codificación del archivo
            with open(fileName, 'rb') as file:
                result = chardet.detect(file.read(10000))
                encoding = result['encoding']

            # Leer el archivo CSV
            delimiters = [',', ';']
            df = None
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(fileName, encoding=encoding, delimiter=delimiter)
                    break
                except Exception as e:
                    print(f'Error al leer con delimitador "{delimiter}": {e}')

            if df is not None:
                self.df = df  # Guardar DataFrame para exportación
                self.transformData()  # Aplicar transformaciones
                self.displayData(self.df)
            else:
                print("No se pudo leer el archivo con los delimitadores proporcionados.")

    def transformData(self):
        # Diccionario de mapeo
        age_mapping = {
            'EB': '1 to 3 years',
            'EL': '3 to 5 years',
            'EP': '3 to 5 years',
            'F11': '9 to 12 years',
            'F5': '6 to 8 years',
            'FXX': '6 to 8 years',
            'F7': '7 to 10 years',
            'F9': '9 to 12 years',
            'FT': 'YA',
            'N11': '9 to 12 years',
            'N5': '6 to 8 years',
            'N7': '7 to 10 years',
            'N9': '9 to 12 years',
            'NXX': '13 to 15 years',
            'NT': 'YA',
            '0to1': '0 to 1 years',
            '0to2': '0 to 2 years',
            '0to3': '0 to 3 years',
            '1to2': '1 to 2 years',
            '2to3': '2 to 3 years',
            '3to5': '3 to 5 years',
            '6to8': '6 to 8 years',
            '7to10': '7 to 10 years',
            '9to12': '9 to 12 years',
            ' ': 'Adult'
        }

        # Transformar Pref_Edad_1
        def transform_pref_edad_1(val):
            if pd.isna(val) or val.strip() == '':
                return 'Adult'
            return age_mapping.get(val, val)

        self.df['Edad_1'] = self.df['Pref_Edad_1'].apply(transform_pref_edad_1)

        # Transformar Pref_Edad_2
        def transform_pref_edad_2(val):
            if pd.isna(val) or val.strip() == '':
                return ''
            return age_mapping.get(val, val)

        self.df['Edad_2'] = self.df['Pref_Edad_2'].apply(transform_pref_edad_2)

        # Agregar columna "Abuelo"
        self.df['Cat_Abuelo'] = 'Books'

        # Crear nuevas columnas para cada BISACT
        bisact_columns = ['BISACT1', 'BISACT2', 'BISACT3', 'BISACT4', 'BISACT5', 'BISACT7', 'BISACT8']

        def dividir_categorias(bisact):
            if isinstance(bisact, str):
                partes = bisact.split(' / ')
                padre = partes[0]
                if 'NONFICTION' in padre:
                    padre = 'Non Fiction'
                elif 'FICTION' in padre:
                    padre = 'Fiction'
                hijo = partes[1] if len(partes) > 1 else None
                tags = partes[2] if len(partes) > 2 else None

                # Capitalizar las partes
                padre = padre.title() if padre else None
                hijo = hijo.title() if hijo else None
                tags = tags.title() if tags else None

                return padre, hijo, tags
            return None, None, None

        for col in bisact_columns:
            self.df[[f'{col}_Padre', f'{col}_Hijo', f'{col}_Tags']] = self.df[col].apply(
                lambda x: pd.Series(dividir_categorias(x)))



    def displayData(self, df):
        # Configurar el modelo de datos para la vista de tabla
        model = PandasModel(df)
        self.tableView.setModel(model)

        # Ajustar el ancho de columnas para mostrar el contenido completo
        self.tableView.resizeColumnsToContents()

    def exportCSV(self):
        # Diálogo para seleccionar archivo de salida
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, 'Guardar archivo CSV', '', 'CSV Files (*.csv);;All Files (*)',
                                                  options=options)

        if fileName:
            # Exportar el DataFrame transformado
            self.df.to_csv(fileName, index=False, encoding='utf-8')
            print(f"Archivo exportado a: {fileName}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CSVViewer()
    viewer.show()
    sys.exit(app.exec_())
