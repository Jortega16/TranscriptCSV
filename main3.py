import sys
import pandas as pd
import chardet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, \
    QTableWidgetItem, QComboBox

class CSVViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Configura la interfaz de usuario del widget.
        """
        layout = QVBoxLayout()

        # Botón para cargar archivos CSV
        self.loadButton = QPushButton('Cargar CSV', self)
        self.loadButton.clicked.connect(self.loadCSV)  # Conectar el botón con la función de carga de CSV
        layout.addWidget(self.loadButton)

        # Botón para exportar archivos CSV
        self.exportButton = QPushButton('Exportar CSV', self)
        self.exportButton.clicked.connect(self.exportCSV)  # Conectar el botón con la función de exportación de CSV
        layout.addWidget(self.exportButton)

        # Tabla para mostrar los datos del CSV
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)
        self.setWindowTitle('Visualizador de CSV')
        self.resize(1200, 800)

    def loadCSV(self):
        """
        Carga un archivo CSV, detecta la codificación y el delimitador, y muestra los datos en la tabla.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo CSV', '', 'CSV Files (*.csv);;All Files (*)',
                                                  options=options)

        if fileName:
            try:
                # Detectar la codificación del archivo
                with open(fileName, 'rb') as file:
                    result = chardet.detect(file.read(10000))
                    encoding = result['encoding']

                # Intentar leer el archivo con diferentes delimitadores
                delimiters = [',', ';']
                df = None
                for delimiter in delimiters:
                    try:
                        df = pd.read_csv(fileName, encoding=encoding, delimiter=delimiter)
                        break
                    except Exception as e:
                        print(f'Error al leer con delimitador "{delimiter}": {e}')

                if df is not None:
                    self.df = df
                    self.transformData()  # Transformar los datos según las necesidades
                    self.displayData(self.df)  # Mostrar los datos en la tabla
                else:
                    print("No se pudo leer el archivo con los delimitadores proporcionados.")
            except Exception as e:
                print(f"Error al cargar el archivo CSV: {e}")

    def transformData(self):
        """
        Transforma los datos del DataFrame agregando columnas nuevas y reorganizando las existentes.
        """
        # Mapeo de códigos de edad a rangos de edad legibles
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

        # Funciones para transformar las columnas de edad
        def transform_pref_edad_1(val):
            if pd.isna(val) or val.strip() == '':
                return ''
            return age_mapping.get(val, val)

        def transform_pref_edad_2(val):
            if pd.isna(val) or val.strip() == '':
                return ''
            return age_mapping.get(val, val)

        self.df['Edad_1'] = self.df['Pref_Edad_1'].apply(transform_pref_edad_1)
        self.df['Edad_2'] = self.df['Pref_Edad_2'].apply(transform_pref_edad_2)

        # Agregar columna de categoría 'Abuelo'
        self.df['Abuelo'] = 'Books'

        bisact_columns = ['BISACT1', 'BISACT2', 'BISACT3', 'BISACT4', 'BISACT5', 'BISACT7', 'BISACT8']

        def dividir_categorias(bisact):
            """
            Divide la cadena BISACT en partes: padre, hijo y etiquetas.
            """
            if isinstance(bisact, str):
                partes = bisact.split(' / ')
                padre = partes[0]
                if 'NONFICTION' in padre:
                    padre = 'Non Fiction'
                elif 'FICTION' in padre:
                    padre = 'Fiction'
                hijo = partes[1] if len(partes) > 1 else ''
                tags = partes[2] if len(partes) > 2 else ''

                padre = padre.title() if padre else ''
                hijo = hijo.title() if hijo else ''
                tags = tags.title() if tags else ''

                return padre, hijo, tags
            return '', '', ''

        # Crear nuevas columnas para los resultados BISACT
        bisact_results = pd.DataFrame()
        for col in bisact_columns:
            padre_col = f'{col}_Padre'
            hijo_col = f'{col}_Hijo'
            tags_col = f'{col}_Tags'

            # Asignar nuevas columnas al DataFrame
            bisact_result = self.df[col].apply(lambda x: pd.Series(dividir_categorias(x)))
            bisact_results[padre_col] = bisact_result[0]
            bisact_results[hijo_col] = bisact_result[1]
            bisact_results[tags_col] = bisact_result[2]

        # Agregar la columna Titulo_Ref y las nuevas columnas al DataFrame
        self.df['Titulo_Ref'] = self.df['Titulo']
        self.df = pd.concat([self.df, bisact_results], axis=1)

        # Reorganizar el DataFrame para poner Titulo_Ref antes de las columnas BISACT
        bisact_columns_extended = [f'{col}_Padre' for col in bisact_columns] + \
                                  [f'{col}_Hijo' for col in bisact_columns] + \
                                  [f'{col}_Tags' for col in bisact_columns]
        original_columns = [col for col in self.df.columns if col not in bisact_columns_extended and col != 'Titulo_Ref']
        self.df = self.df[original_columns + ['Titulo_Ref'] + bisact_columns_extended]

    def displayData(self, df):
        """
        Muestra los datos del DataFrame en la tabla y configura los widgets adecuados en las celdas.
        """
        self.tableWidget.setRowCount(len(df))
        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        # Opciones para los comboboxes en las celdas
        hijo_options = [
            "Action and Adventure", "Activity Books", "Animals", "Architecture and Construction",
            "Art and Artists", "Atlases and Maps", "Biographies", "Biology", "Board Games",
            "Business and Economics", "Business Studies and Economics", "Card Games", "Chapter Books",
            "Chemistry", "Classics", "Computing and Technology", "Confident Readers", "Contemporary Fiction",
            "Crime and Mystery", "Dictionaries and Thesauri", "Dinosaurs and Dragons", "Diversity and Inclusion",
            "Dystopian", "Early Years Concepts", "Early Years Concepts, Literacy", "Early Years Concepts, Numeracy",
            "Early Readers", "Emotions and Behaviours", "Family and Home", "Fantasy and Magic", "Friends and School",
            "Games", "Ghosts and Zombies", "Graphic Novels", "Handicrafts", "Health and Nutrition",
            "Historical Fiction", "History", "Human Body", "Humour", "Interactive Game Book", "Journals",
            "Languages", "Marine and River Life", "Mathematics", "Media Tie-in", "Mental Health", "Minibeasts",
            "Music and Musicians", "Myths and Legends", "Nature and the Environment", "People and Places", "Philosophy",
            "Physics", "Poetry", "Politics", "Psychology", "Puzzles", "Reference", "Religion and Festivals", "Romance",
            "Science and Technology", "Science Fiction", "Social Topics", "Space and the Solar System", "Sport",
            "Study Guides", "Teacher Guides", "Traditional Stories", "Vehicles", "Women Power"
        ]

        abuelo_options = ["Books", "Toys", "Montessori", "Art and Crafts", "Accessories"]
        padre_options = ["Activity books", "Education", "Fiction", "Non Fiction"]
        edad_options = sorted([
            '1 to 3 years', '3 to 5 years', '9 to 12 years', '6 to 8 years', '7 to 10 years', 'YA', '13 to 15 years',
            '0 to 1 years', '0 to 2 years', '0 to 3 years', '1 to 2 years', '2 to 3 years', 'Adult'
        ])

        # Ajustar el ancho de las columnas
        titulo_ref_col_index = df.columns.get_loc('Titulo_Ref')
        self.tableWidget.setColumnWidth(titulo_ref_col_index, 350)  # Cambia el valor a tu gusto

        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = df.iloc[row, col]
                # Reemplazar NaN con una cadena vacía
                if pd.isna(value):
                    value = ''
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item)

                # Crear comboboxes en las celdas adecuadas
                if df.columns[col].endswith('_Hijo'):
                    combo = QComboBox()
                    combo.addItem(value)
                    combo.addItems([option for option in hijo_options if option != value])
                    self.tableWidget.setCellWidget(row, col, combo)

                elif df.columns[col] == 'Abuelo':
                    combo = QComboBox()
                    combo.addItem(value)
                    combo.addItems([option for option in abuelo_options if option != value])
                    self.tableWidget.setCellWidget(row, col, combo)

                elif df.columns[col].endswith('_Padre'):
                    combo = QComboBox()
                    combo.addItem(value)
                    combo.addItems([option for option in padre_options if option != value])
                    self.tableWidget.setCellWidget(row, col, combo)

                elif df.columns[col].endswith('_Tags'):
                    combo = QComboBox()
                    combo.addItem(value)
                    combo.addItems([option for option in padre_options if option != value])
                    self.tableWidget.setCellWidget(row, col, combo)

                elif df.columns[col].startswith('Edad_'):
                    combo = QComboBox()
                    combo.addItem(value)
                    combo.addItems([option for option in edad_options if option != value])
                    self.tableWidget.setCellWidget(row, col, combo)

    def exportCSV(self):
        """
        Exporta los datos actuales de la tabla a un archivo CSV.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, 'Guardar archivo CSV', '', 'CSV Files (*.csv);;All Files (*)',
                                                  options=options)

        if fileName:
            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    cellWidget = self.tableWidget.cellWidget(row, col)
                    if isinstance(cellWidget, QComboBox):
                        self.df.iat[row, col] = cellWidget.currentText()
                    else:
                        self.df.iat[row, col] = self.tableWidget.item(row, col).text()

            self.df.to_csv(fileName, index=False)
            print(f"Archivo exportado a: {fileName}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CSVViewer()
    viewer.show()
    sys.exit(app.exec_())
