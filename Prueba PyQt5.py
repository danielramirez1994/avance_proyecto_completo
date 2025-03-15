from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
                            QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QGridLayout, 
                            QScrollArea, QCheckBox, QGroupBox, QFileDialog, QFrame, QComboBox,
                            QMessageBox)  # Añadido QMessageBox
from PyQt5.QtCore import Qt, QSizeF  # Añadido QSizeF
from PyQt5.QtGui import QPen, QColor, QPainter  # Añadido QPainter
from PyQt5.QtPrintSupport import QPrinter  # Añadido QPrinter
import json
import random

class NestingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel Nesting Optimizer")
        
        self.inches_to_pixels = 16
        self.panel_width = 96.5 * self.inches_to_pixels
        self.panel_height = 48.5 * self.inches_to_pixels

        self.panels = []
        self.panel_pieces = []  # Lista de piezas para cada panel
        self.panel_free_spaces = []  # Lista de espacios libres para cada panel
        self.panel_utilization = []  # Porcentaje de utilización de cada panel
        self.panel_rows = []  # Lista de filas para cada panel
        self.current_panel_index = 0

        # Criterio de ordenación de piezas
        self.sort_criteria = "area_desc"  # Por defecto, ordenar por área descendente

        # Diccionarios para las selecciones de piezas
        self.all_pieces = set()  # Nombres únicos de todas las piezas
        self.add_pieces = set([
            "Base",
            "Lateral Derecho",
            "Lateral Izquierdo",
        ])
        
        self.piezas_girables = []
        
        # Variables para almacenar las selecciones de UI
        self.piece_checkboxes = {}  # Para piezas a ignorar
        self.rotatable_checkboxes = {}  # Para piezas girables
        
        # Nuevo - Para selección de gabinetes
        self.all_gabinetes = set()  # IDs únicos de todos los gabinetes
        self.selected_gabinetes = set()  # IDs de gabinetes seleccionados
        self.gabinete_checkboxes = {}  # Para selección de gabinetes
        
        # Cargar los datos y extraer nombres de piezas
        self.json_data = self.load_json_data("temp_gabinetes.json")
        self.extract_piece_names()
        self.extract_gabinete_ids()  # Nuevo - Extraer IDs de gabinetes
        
        # Iniciar la interfaz
        self.setup_ui()
        
        # Inicializar checkboxes con la configuración actual
        self.update_piece_checkboxes()
        self.update_gabinete_checkboxes()
        
        # Ejecutar el algoritmo de optimización
        self.refresh_panels()

    def setup_ui(self):
        # Layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Panel izquierdo para controles
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Información del panel actual
        self.info_label = QLabel("Panel 1 de 1 | Utilización: 0%")
        left_layout.addWidget(self.info_label)

        # ComboBox para seleccionar criterio de ordenación
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Criterio de ordenación:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Área (Mayor a menor)", "area_desc")
        self.sort_combo.addItem("Área (Menor a mayor)", "area_asc")
        self.sort_combo.addItem("Ancho (Mayor a menor)", "width_desc")
        self.sort_combo.addItem("Ancho (Menor a mayor)", "width_asc")
        self.sort_combo.addItem("Alto (Mayor a menor)", "height_desc")
        self.sort_combo.addItem("Alto (Menor a mayor)", "height_asc")
        self.sort_combo.currentIndexChanged.connect(self.update_sort_criteria)
        sort_layout.addWidget(self.sort_combo)
        left_layout.addLayout(sort_layout)

        # Grupo de selección de gabinetes
        gabinete_group = QGroupBox("Selección de Gabinetes")
        self.gabinete_layout = QGridLayout()
        gabinete_group.setLayout(self.gabinete_layout)
        left_layout.addWidget(gabinete_group)

        # Grupo de selección de piezas a ignorar
        ignore_group = QGroupBox("Piezas a Ignorar")
        self.ignore_layout = QGridLayout()
        ignore_group.setLayout(self.ignore_layout)
        left_layout.addWidget(ignore_group)

        # Grupo de selección de piezas girables
        rotatable_group = QGroupBox("Piezas Girables")
        self.rotatable_layout = QGridLayout()
        rotatable_group.setLayout(self.rotatable_layout)
        left_layout.addWidget(rotatable_group)

        # Botones de acción y navegación
        action_layout = QGridLayout()
        self.prev_button = QPushButton("Anterior Panel")
        self.next_button = QPushButton("Siguiente Panel")
        self.refresh_button = QPushButton("Refrescar")
        self.export_button = QPushButton("Exportar")
        self.exit_button = QPushButton("Salir")
        self.load_json_button = QPushButton("Cargar JSON")

        action_layout.addWidget(self.prev_button, 0, 0)
        action_layout.addWidget(self.next_button, 0, 1)
        action_layout.addWidget(self.refresh_button, 1, 0)
        action_layout.addWidget(self.export_button, 1, 1)
        action_layout.addWidget(self.exit_button, 2, 0, 1, 2)
        action_layout.addWidget(self.load_json_button, 3, 0, 1, 2)

        left_layout.addLayout(action_layout)

        self.prev_button.clicked.connect(self.show_previous_panel)
        self.next_button.clicked.connect(self.show_next_panel)
        self.refresh_button.clicked.connect(self.refresh_panels)
        self.export_button.clicked.connect(self.export_panels)
        self.exit_button.clicked.connect(self.close)
        self.load_json_button.clicked.connect(self.load_new_json_file)

        self.view = QGraphicsView()
        self.view.setRenderHint(0x01)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.view, 3)

        self.setCentralWidget(main_widget)
        self.resize(1200, 800)

    def load_new_json_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON", "", "Archivos JSON (*.json);;Todos los archivos (*)", options=options)
        if file_name:
            self.json_data = self.load_json_data(file_name)
            self.all_pieces.clear()
            self.all_gabinetes.clear()
            self.add_pieces = set([

            ])
            self.piezas_girables = [
                "Lateral Izquierdo",
                "Lateral Derecho",
                "Trasera",
            ]
            self.selected_gabinetes.clear()
            self.extract_piece_names()
            self.extract_gabinete_ids()
            self.update_piece_checkboxes()
            self.update_gabinete_checkboxes()
            self.refresh_panels()

    def update_piece_checkboxes(self):
        for checkbox in self.piece_checkboxes.values():
            checkbox.setParent(None)
        self.piece_checkboxes.clear()

        for checkbox in self.rotatable_checkboxes.values():
            checkbox.setParent(None)
        self.rotatable_checkboxes.clear()

        row, col = 0, 0
        for piece_name in sorted(self.all_pieces):
            checkbox = QCheckBox(piece_name)
            checkbox.setChecked(piece_name in self.add_pieces)  # Modificado para usar estado inicial
            checkbox.stateChanged.connect(self.update_ignored_pieces)
            self.piece_checkboxes[piece_name] = checkbox
            self.ignore_layout.addWidget(checkbox, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1

        row, col = 0, 0
        for piece_name in sorted(self.all_pieces):
            checkbox = QCheckBox(piece_name)
            checkbox.setChecked(piece_name in self.piezas_girables)  # Modificado para usar estado inicial
            checkbox.stateChanged.connect(self.update_rotatable_pieces)
            self.rotatable_checkboxes[piece_name] = checkbox
            self.rotatable_layout.addWidget(checkbox, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1

    def update_gabinete_checkboxes(self):
        for checkbox in self.gabinete_checkboxes.values():
            checkbox.setParent(None)
        self.gabinete_checkboxes.clear()

        row, col = 0, 0
        for gabinete_id in sorted(self.all_gabinetes):
            checkbox = QCheckBox(f"Gabinete {gabinete_id}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_selected_gabinetes)
            self.gabinete_checkboxes[gabinete_id] = checkbox
            self.selected_gabinetes.add(gabinete_id)
            self.gabinete_layout.addWidget(checkbox, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1

    def update_sort_criteria(self, index):
        """Actualiza el criterio de ordenación cuando se cambia en el ComboBox"""
        self.sort_criteria = self.sort_combo.currentData()
        # Opcionalmente, puedes refrescar los paneles automáticamente
        # self.refresh_panels()
        
    # NUEVO - Método para actualizar gabinetes seleccionados
    def update_selected_gabinetes(self):
        """Actualiza la lista de gabinetes seleccionados basado en checkboxes"""
        self.selected_gabinetes = set()
        for gabinete_id, checkbox in self.gabinete_checkboxes.items():
            if checkbox.isChecked():
                self.selected_gabinetes.add(gabinete_id)

    def load_json_data(self, filepath):
        """Carga datos del archivo JSON"""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                # Extraer la lista de gabinetes y piezas
                self.gabinetes = data.get("gabinetes", [])
                self.piezas = data.get("piezas", [])
                return data
        except Exception as e:
            print(f"Error al cargar archivo JSON: {e}")
            return []

    def extract_piece_names(self):
        """Extrae todos los nombres únicos de piezas del JSON"""
        for pieza in self.piezas:
            if 'nombre' in pieza:
                self.all_pieces.add(pieza['nombre'])
    
    # NUEVO - Método para extraer IDs de gabinetes
    def extract_gabinete_ids(self):
        """Extrae todos los IDs únicos de gabinetes del JSON"""
        for gabinete in self.gabinetes:
            if 'ID' in gabinete:
                self.all_gabinetes.add(gabinete['ID'])

    def update_ignored_pieces(self):
        """Actualiza la lista de piezas ignoradas basado en checkboxes (lógica invertida)"""
        self.add_pieces = set()
        for piece_name, checkbox in self.piece_checkboxes.items():
            # Ahora añadimos a ignored_pieces si el checkbox NO está marcado
            if not checkbox.isChecked():
                self.add_pieces.add(piece_name)
        
        # Actualizar checkboxes de piezas girables para mostrar solo piezas incluidas
        self.update_rotatable_checkboxes()

    def update_rotatable_checkboxes(self):
        """Actualiza visibilidad de checkboxes para piezas girables"""
        # Limpiar layout existente
        for piece_name in self.rotatable_checkboxes:
            self.rotatable_checkboxes[piece_name].setVisible(piece_name not in self.add_pieces)
        
    def update_rotatable_pieces(self):
        """Actualiza la lista de piezas girables basado en checkboxes"""
        self.piezas_girables = []
        for piece_name, checkbox in self.rotatable_checkboxes.items():
            if checkbox.isChecked() and piece_name not in self.add_pieces:
                self.piezas_girables.append(piece_name)

    def load_pieces_from_json(self, json_data):
        """Procesa los datos JSON para extraer las piezas considerando selecciones de usuario"""
        pieces = []
        for pieza in self.piezas:
            nombre = pieza.get('nombre')
            if nombre in self.add_pieces:
                continue
            ancho = pieza.get('ancho')
            alto = pieza.get('alto')
            gabinete_id = pieza.get('gabinete_id')
            if ancho and alto and gabinete_id in self.selected_gabinetes:
                # Verificar si se debe rotar la pieza
                if nombre in self.piezas_girables:
                    ancho, alto = alto, ancho
                pieces.append({
                    "width": ancho,
                    "height": alto,
                    "nombre": nombre,
                    "gabinete_id": gabinete_id
                })
        return pieces

    def refresh_panels(self):
        """Actualiza los paneles según las selecciones actuales"""
        # Reiniciar datos de paneles
        self.panels = []
        self.panel_pieces = []
        self.panel_utilization = []
        self.panel_rows = []
        self.panel_structure = []
        
        # Procesar piezas del JSON con las selecciones actuales
        pieces = self.load_pieces_from_json(self.json_data)
        
        # Ejecutar algoritmo de optimización
        self.optimize_panels(pieces)
        self.update_panels()
        
        # Mostrar primer panel
        if self.panels:
            self.show_panel(0)
        else:
            self.info_label.setText("No hay paneles para mostrar")

    def export_panels(self):
        """Exporta los paneles actuales a un archivo PDF"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", 
                                                "Archivos PDF (*.pdf);;Todos los archivos (*)", 
                                                options=options)
        if fileName:
            # Asegurarse de que el nombre del archivo termine en .pdf
            if not fileName.lower().endswith('.pdf'):
                fileName += '.pdf'
            
            # Importar los módulos necesarios para generar PDF
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtGui import QPainter
            from PyQt5.QtCore import QSizeF  # Importación correcta para QSizeF
            
            # Crear una instancia de QPrinter configurada para PDF
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fileName)
            
            # Configurar el tamaño de página para que se ajuste a nuestros paneles
            # Convertir de píxeles a milímetros (QPrinter usa milímetros)
            width_mm = self.panel_width / self.inches_to_pixels * 25.4  # 1 pulgada = 25.4 mm
            height_mm = self.panel_height / self.inches_to_pixels * 25.4
            
            printer.setPageSize(QPrinter.Custom)
            printer.setPageSizeMM(QSizeF(width_mm, height_mm))  # Usando QSizeF sin QtCore.
            
            # Crear un QPainter para dibujar en el PDF
            painter = QPainter()
            success = painter.begin(printer)
            
            if success:
                try:
                    # Dibujar cada panel en una página diferente
                    for i, scene in enumerate(self.panels):
                        # Si no es la primera página, añadir una nueva página
                        if i > 0:
                            printer.newPage()
                        
                        # Dibujar la escena actual
                        scene.render(painter)
                        
                        # Añadir información adicional en la parte superior
                        painter.save()
                        font = painter.font()
                        font.setPointSize(12)
                        painter.setFont(font)
                        
                        utilization = self.panel_utilization[i] if i < len(self.panel_utilization) else 0
                        title_text = f"Panel {i+1} de {len(self.panels)} | Utilización: {utilization:.1f}%"
                        
                        # Dibujar el texto de información en la parte superior
                        painter.drawText(10, 20, title_text)
                        painter.restore()
                    
                    # Finalizar la operación de dibujo
                    painter.end()
                    
                    # Mostrar mensaje de éxito
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Exportación Exitosa", 
                                        f"Los paneles han sido exportados exitosamente a:\n{fileName}")
                    
                except Exception as e:
                    painter.end()
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Error de Exportación", 
                                    f"Error al generar el PDF: {e}")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", "No se pudo iniciar la generación del PDF.")

    def optimize_panels(self, pieces):
        # Ordenar las piezas según el criterio seleccionado
        if self.sort_criteria == "area_desc":
            pieces.sort(key=lambda p: (p['height'] * p['width'], p['width']), reverse=True)
        elif self.sort_criteria == "area_asc":
            pieces.sort(key=lambda p: (p['height'] * p['width'], p['height']), reverse=False)
        elif self.sort_criteria == "width_desc":
            pieces.sort(key=lambda p: p['width'], reverse=True)
        elif self.sort_criteria == "width_asc":
            pieces.sort(key=lambda p: p['width'], reverse=False)
        elif self.sort_criteria == "height_desc":
            pieces.sort(key=lambda p: p['height'], reverse=True)
        elif self.sort_criteria == "height_asc":
            pieces.sort(key=lambda p: p['height'], reverse=False)
        
        # Inicializamos las listas para paneles
        self.panel_pieces = []  # Lista para almacenar las piezas colocadas en cada panel
        self.panel_utilization = []  # Lista para almacenar el porcentaje de utilización de cada panel
        self.panel_structure = []

        for piece in pieces:
            # Convertir dimensiones de pulgadas a píxeles
            separator = 0.125 * self.inches_to_pixels
            piece_width = piece['width'] * self.inches_to_pixels
            piece_height = piece['height'] * self.inches_to_pixels
            nombre = piece['nombre']
            gabinete_id = piece['gabinete_id']
            rotated = nombre in self.piezas_girables

            # Variables para el mejor lugar encontrado
            best_fit = {
                'panel_idx': -1,
                'row_idx': -1,
                'col_idx': -1,
                'position': None,
                'y': float('inf')  # Priorizar posiciones más altas
            }
            
        
            # 1. Buscar en espacios existentes PRIORIZANDO COLUMNAS
            for panel_idx, panel in enumerate(self.panel_structure):
                for row_idx, row in enumerate(panel):
                    row_y = row['y']
                    row_height = row['height']
                    
                    # Verificar si la pieza cabe en la altura de la fila
                    if piece_height <= row_height:
                        for col_idx, col in enumerate(row['columns']):
                            col_x = col['x']
                            col_width = self.panel_width
                            
                            # Verificar si la pieza cabe en el ancho de la columna
                            if piece_width <= col_width:
                                # Verificar si la posición es válida sin colisiones
                                if self.is_position_valid(panel_idx, col_x, row_y, piece_width, piece_height, col_limit=(col_x, col_width), row_limit=(row_y, row_height)):
                                    # Evaluar si es la mejor posición encontrada
                                    if row_y < best_fit['y']:
                                        best_fit = {
                                            'panel_idx': panel_idx,
                                            'row_idx': row_idx,
                                            'col_idx': col_idx,
                                            'position': (col_x, row_y, piece_width, piece_height),
                                            'y': row_y
                                        }

                                break
                    
                    
                    if best_fit['panel_idx'] != -1:
                        break
                
                # Si ya encontramos un espacio, salir del bucle de paneles
                if best_fit['panel_idx'] != -1:
                    break
            
            # 2. Si no encontramos espacio en columnas existentes
            if best_fit['panel_idx'] == -1:
                # Intentar crear una nueva columna en filas existentes
                for panel_idx, panel in enumerate(self.panel_structure):
                    for row_idx, row in enumerate(panel):
                        # Calcular espacio disponible para nueva columna
                        total_columns_width = sum(col['width'] for col in row['columns'])
                        if total_columns_width + piece_width <= self.panel_width:
                            # Crear nueva columna en la fila
                            nueva_columna_x = (row['columns'][-1]['x'] + row['columns'][-1]['width']) if row['columns'] else 0
                            
                            if self.is_position_valid(panel_idx, nueva_columna_x, row_y, piece_width, piece_height, col_limit=(nueva_columna_x, piece_width), row_limit=(row_y, row_height)):
                                best_fit = {
                                    'panel_idx': panel_idx,
                                    'row_idx': row_idx,
                                    'col_idx': -1,  # Nueva columna
                                    'position': (nueva_columna_x, row['y'], piece_width, piece_height),
                                    'y': row['y']
                                }
                                break
                    
                    if best_fit['panel_idx'] != -1:
                        break
            
            # 3. Si aún no encontramos espacio, crear nueva fila
            if best_fit['panel_idx'] == -1:
                for panel_idx, panel in enumerate(self.panel_structure):
                    # Calcular posición Y para nueva fila
                    max_y = max(row['y'] + row['height'] + separator for row in panel) if panel else 0
                    
                    if max_y + piece_height <= self.panel_height:
                        if self.is_position_valid(panel_idx, 0, max_y, piece_width, piece_height):
                            best_fit = {
                                'panel_idx': panel_idx,
                                'row_idx': -1,  # Nueva fila
                                'col_idx': -1,
                                'position': (0, max_y, piece_width, piece_height),
                                'y': max_y
                            }
                            break
            
            # 4. Si no hay espacio, crear nuevo panel
            if best_fit['panel_idx'] == -1:
                self.panel_pieces.append([])
                self.panel_utilization.append(0)
                self.panel_structure.append([])
                
                best_fit = {
                    'panel_idx': len(self.panel_pieces) - 1,
                    'row_idx': -1,
                    'col_idx': -1,
                    'position': (0, 0, piece_width, piece_height),
                    'y': 0
                }
            
            # Colocar pieza
            panel_idx = best_fit['panel_idx']
            x, y, pw, ph = best_fit['position']
            
            # Añadir pieza al panel
            self.panel_pieces[panel_idx].append((x, y, pw, ph, piece['width'], piece['height'], piece['nombre'], rotated, gabinete_id))
            
            # Actualizar estructura
            if best_fit['row_idx'] >= 0 and best_fit['col_idx'] >= 0:
                # Pieza en columna existente
                self._update_existing_space(panel_idx, best_fit['row_idx'], best_fit['col_idx'], x, y, pw, ph)
            elif best_fit['row_idx'] >= 0:
                # Nueva columna en fila existente
                row = self.panel_structure[panel_idx][best_fit['row_idx']]
                row['columns'].append({
                    'x': x,
                    'width': pw,
                    'max_height': ph
                })
            else:
                # Nueva fila
                self._create_new_row(panel_idx, x, y, pw, ph)
            
        # Calcular utilización y convertir estructura
        self._calculate_utilization()
        self._convert_structure_to_panel_rows()
        
    def is_position_valid(self, panel_idx, x, y, width, height, col_limit=None, row_limit=None):
        """Verifica si una posición está libre de colisiones y dentro de los límites de su fila y columna."""
        
        if panel_idx >= len(self.panel_pieces):
            return True  # Panel nuevo, siempre válido
        
        # Validar límites del panel completo
        if x < 0 or y < 0 or x + width > self.panel_width or y + height > self.panel_height:
            return False

        # Validar límites de la columna
        if col_limit:
            col_x, col_width = col_limit
            if x < col_x or x + width > col_x + col_width:
                return False

        # Validar límites de la fila
        if row_limit:
            row_y, row_height = row_limit
            if y < row_y or y + height > row_y + row_height:
                return False

        # Verificar colisiones con otras piezas
        for px, py, pw, ph, _, _, _, _, _ in self.panel_pieces[panel_idx]:
            if (x < px + pw and x + width > px and
                y < py + ph and y + height > py):
                return False

        return True

    def _update_existing_space(self, panel_idx, row_idx, col_idx, x, y, piece_width, piece_height):
        """Actualiza los espacios después de colocar una pieza en un espacio existente."""
        row = self.panel_structure[panel_idx][row_idx]
        col = row['columns'][col_idx]
        # Convertir 0.125 pulgadas a píxeles
        separator = 0.125 * self.inches_to_pixels
        
        # 1. Actualizar columnas - espacios horizontales
        new_columns = []
        
        # Espacio a la izquierda de la pieza
        if x > col['x']:
            new_columns.append({
                'x': col['x'],
                'width': x - col['x'],
                'max_height': col['max_height']
            })
        
        # Espacio a la derecha de la pieza
        right_x = x + piece_width + separator
        if right_x < col['x'] + col['width']:
            new_columns.append({
                'x': right_x,
                'width': (col['x'] + col['width']) - right_x,
                'max_height': col['max_height']
            })
        
        # Mantener otras columnas en la fila
        for i, other_col in enumerate(row['columns']):
            if i != col_idx:
                new_columns.append(other_col)
        
        # Actualizar columnas de la fila
        row['columns'] = new_columns
        
        # 2. Crear espacio debajo de la pieza (nueva fila)
        space_below_y = y + piece_height + separator
        space_below_height = row['y'] + row['height'] - space_below_y
        
        if space_below_height > 0:
            # Buscar si existe una fila en esa posición Y
            existing_row_idx = -1
            for idx, exist_row in enumerate(self.panel_structure[panel_idx]):
                if abs(exist_row['y'] - space_below_y) < 1:  # Margen de error
                    existing_row_idx = idx
                    break
            
            if existing_row_idx >= 0:
                # Añadir columna a la fila existente
                self.panel_structure[panel_idx][existing_row_idx]['columns'].append({
                    'x': x,
                    'width': piece_width,
                    'max_height': space_below_height
                })
            else:
                # Crear nueva fila para el espacio debajo
                new_row = {
                    'y': space_below_y,
                    'height': space_below_height,
                    'columns': [{
                        'x': x,
                        'width': piece_width,
                        'max_height': space_below_height
                    }]
                }
                self.panel_structure[panel_idx].append(new_row)

    def _create_new_row(self, panel_idx, x, y, piece_width, piece_height):
        """Crea una nueva fila después de colocar una pieza, incluyendo una fila de 0.125 pulgadas."""
        
        # Convertir 0.125 pulgadas a píxeles
        separator = 0.125 * self.inches_to_pixels

        # 1. Crear la fila principal con la pieza
        new_row = {
            'y': y,
            'height': piece_height,
            'columns': []
        }
        
        # Añadir espacio a la derecha de la pieza
        remaining_width = self.panel_width - (x + piece_width)
        if remaining_width > 0:
            new_row['columns'].append({
                'x': x + piece_width + separator,
                'width': remaining_width,
                'max_height': piece_height
            })
        
        self.panel_structure[panel_idx].append(new_row)

    def _calculate_utilization(self):
        """Calcula el porcentaje de utilización de cada panel."""
        self.panel_utilization = []  # Reiniciar para evitar duplicados
        for i, pieces in enumerate(self.panel_pieces):
            total_area = self.panel_width * self.panel_height
            used_area = sum(p[2] * p[3] for p in pieces)  # Suma de áreas
            utilization = (used_area / total_area) * 100
            self.panel_utilization.append(utilization)

    def _convert_structure_to_panel_rows(self):
        """Convierte la estructura interna a formato panel_rows para compatibilidad."""
        self.panel_rows = []
        
        for panel in self.panel_structure:
            panel_rows = []
            
            for row in panel:
                # Convertir columnas al formato esperado (x, width) para compatibilidad
                compatible_columns = [(col['x'], col['width']) for col in row['columns']]
                panel_rows.append((row['y'], row['height'], compatible_columns))
            
            self.panel_rows.append(panel_rows)
        
    def update_panels(self):
        self.panels = []
        for i, panel_pieces in enumerate(self.panel_pieces):
            scene = QGraphicsScene()
            scene.setSceneRect(0, 0, self.panel_width, self.panel_height)

            # Asignar colores aleatorios para cada tipo de pieza
            piece_colors = {}
            
            for x, y, pw, ph, aw, ah, nombre, rotated, gabinete_id in panel_pieces:
                # Asignar un color consistente para cada tipo de pieza
                if nombre not in piece_colors:
                    h = hash(nombre) % 360
                    piece_colors[nombre] = QColor.fromHsv(h, 10, 10, 10)
                
                rect = QGraphicsRectItem(x, y, pw, ph)
                rect.setBrush(piece_colors[nombre])
                rect.setPen(QPen(Qt.black, 1))
                scene.addItem(rect)

                rot_text = " (Rotada)" if rotated else ""
                text = f"{nombre}{rot_text}\nGabinete {gabinete_id}\n{aw:.1f} x {ah:.1f}"
                text_item = scene.addText(text)
                text_item.setPos(x + pw / 2 - text_item.boundingRect().width() / 2,
                                y + ph / 2 - text_item.boundingRect().height() / 2)

            # Visualizar filas (opcional, para depuración)
            if i < len(self.panel_rows):
                for row_y, row_height, row_spaces in self.panel_rows[i]:
                    # Dibujar el contorno de la fila
                    row_rect = QGraphicsRectItem(0, row_y, self.panel_width, row_height)
                    row_rect.setPen(QPen(Qt.blue, 1, Qt.DashLine))
                    #scene.addItem(row_rect)
                    
                    # Dibujar los espacios libres en la fila
                    for space_x, space_width in row_spaces:
                        if space_width > 0:
                            space_rect = QGraphicsRectItem(space_x, row_y, space_width, row_height)
                            space_rect.setPen(QPen(Qt.blue, 1, Qt.DotLine))
                            scene.addItem(space_rect)

            # Mostrar porcentaje de utilización en cada panel
            util_text = f"Utilización: {self.panel_utilization[i]:.1f}%"
            util_item = scene.addText(util_text)
            util_item.setPos(10, 10)  # Esquina superior izquierda

            # Borde del panel
            border = QGraphicsRectItem(0, 0, self.panel_width, self.panel_height)
            border.setPen(QPen(Qt.red, 1))
            scene.addItem(border)

            self.panels.append(scene)

    def show_panel(self, index):
        if 0 <= index < len(self.panels):
            self.current_panel_index = index
            self.view.setScene(self.panels[index])
            
            # Actualizar etiqueta de información
            utilization = self.panel_utilization[index] if index < len(self.panel_utilization) else 0
            self.info_label.setText(f"Panel {index+1} de {len(self.panels)} | Utilización: {utilization:.1f}%")

    def show_next_panel(self):
        if self.current_panel_index < len(self.panels) - 1:
            self.show_panel(self.current_panel_index + 1)

    def show_previous_panel(self):
        if self.current_panel_index > 0:
            self.show_panel(self.current_panel_index - 1)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = NestingWindow()
    window.show()
    sys.exit(app.exec_())