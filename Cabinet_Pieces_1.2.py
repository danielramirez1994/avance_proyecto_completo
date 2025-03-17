import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import json
import uuid
from MaterialManager import MaterialManager


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.mostrar_tooltip)
        self.widget.bind("<Leave>", self.ocultar_tooltip)

    def mostrar_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")  # Obtener la posición del widget
        x += self.widget.winfo_rootx() + 25  # Ajustar la posición
        y += self.widget.winfo_rooty() + 25

        # Crear una ventana emergente (toplevel)
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Eliminar bordes de la ventana
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def ocultar_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class AplicacionGabinetes:
    def __init__(self, root):
        self.root = root
        self.root.title("Diseño de Gabinetes")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        self.root.bind("<Control-s>", lambda event: self.guardar_datos())  # Guardar con Ctrl+S
        self.root.bind("<Control-o>", lambda event: self.cargar_datos())  # Cargar con Ctrl+O
        self.root.bind("<Control-n>", lambda event: self.limpiar_datos())  # Limpiar con Ctrl+N

        
        # Variables para almacenar datos
        self.gabinetes = []
        self.piezas = []
        self.archivo_actual = None
        
        # Configuración para el autoguardado
        self.archivo_temp = "temp_gabinetes.json"  # Archivo temporal predeterminado
        
        # Crear pestañas principales
        self.notebook_principal = ttk.Notebook(self.root)
        self.notebook_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear las 5 pestañas principales
        self.tab_ingreso = ttk.Frame(self.notebook_principal)
        self.tab_organizar_2d = ttk.Frame(self.notebook_principal)
        self.tab_visualizar_3d = ttk.Frame(self.notebook_principal)
        self.tab_nesting = ttk.Frame(self.notebook_principal)
        self.tab_configuraciones = ttk.Frame(self.notebook_principal)
        
        # Agregar pestañas al notebook principal
        self.notebook_principal.add(self.tab_ingreso, text="Ingreso de datos")
        self.notebook_principal.add(self.tab_organizar_2d, text="Organizar Gabinetes 2D")
        self.notebook_principal.add(self.tab_visualizar_3d, text="Visualizar Cocina 3D")
        self.notebook_principal.add(self.tab_nesting, text="Nesting")
        self.notebook_principal.add(self.tab_configuraciones, text="Configuraciones")
        
        # Configurar la pestaña de ingreso de datos
        self.setup_tab_ingreso()
        self.setup_tab_nesting()
        self.setup_tab_configuraciones()  # Configurar la pestaña de Configuraciones
        # Verificar si hay un proyecto anterior y preguntar si desea cargarlo
        self.cargar_proyecto_anterior()
        
    def setup_tab_nesting(self):
        """Configura la pestaña de Nesting"""
        # Crear paneles redimensionables en la pestaña de Nesting
        self.paneles_nesting = ttk.PanedWindow(self.tab_nesting, orient=tk.VERTICAL)
        self.paneles_nesting.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para detalles del gabinete
        self.frame_detalles = ttk.LabelFrame(self.paneles_nesting, text="Detalles del Gabinete")
        self.paneles_nesting.add(self.frame_detalles, weight=1)

        # Texto informativo para detalles
        self.texto_detalles = tk.Text(self.frame_detalles, wrap=tk.WORD, height=10)
        self.texto_detalles.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar para el texto
        scrollbar_detalles = ttk.Scrollbar(self.texto_detalles, orient=tk.VERTICAL, command=self.texto_detalles.yview)
        self.texto_detalles.configure(yscroll=scrollbar_detalles.set)
        scrollbar_detalles.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para materiales
        self.frame_materiales = ttk.LabelFrame(self.paneles_nesting, text="Resumen de Materiales")
        self.paneles_nesting.add(self.frame_materiales, weight=1)

        # Tabla para materiales
        self.tree_materiales = ttk.Treeview(self.frame_materiales, columns=("Material", "Cantidad", "Área"), show="headings")
        self.tree_materiales.heading("Material", text="Material")
        self.tree_materiales.heading("Cantidad", text="Cantidad")
        self.tree_materiales.heading("Área", text="Área (m²)")

        self.tree_materiales.column("Material", width=100)
        self.tree_materiales.column("Cantidad", width=60)
        self.tree_materiales.column("Área", width=60)

        # Agregar scrollbar
        scrollbar_materiales = ttk.Scrollbar(self.frame_materiales, orient=tk.VERTICAL, command=self.tree_materiales.yview)
        self.tree_materiales.configure(yscroll=scrollbar_materiales.set)
        scrollbar_materiales.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_materiales.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_tab_ingreso(self):
        # Crear los paneles redimensionables
        self.paneles_ingreso = ttk.PanedWindow(self.tab_ingreso, orient=tk.HORIZONTAL)
        self.paneles_ingreso.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame izquierdo
        self.frame_izquierdo = ttk.Frame(self.paneles_ingreso)
        self.paneles_ingreso.add(self.frame_izquierdo, weight=1)
        
        # Frame central
        self.frame_central = ttk.Frame(self.paneles_ingreso)
        self.paneles_ingreso.add(self.frame_central, weight=2)
        
        # Frame derecho
        self.frame_derecho = ttk.Frame(self.paneles_ingreso)
        self.paneles_ingreso.add(self.frame_derecho, weight=1)
        
        # Configurar el frame izquierdo
        self.setup_frame_izquierdo()
        
        # Configurar el frame central
        self.setup_frame_central()
        
        # Configurar el frame derecho
        self.setup_frame_derecho()
    
    def setup_frame_izquierdo(self):
        # Frame para dimensiones y estilos
        self.frame_dimensiones = ttk.LabelFrame(self.frame_izquierdo, text="Dimensiones y Estilos")
        self.frame_dimensiones.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Campos de entrada
        ttk.Label(self.frame_dimensiones, text="Alto (in):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_alto = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_alto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        Tooltip(self.entry_alto, "Ingrese la altura del gabinete en Pulgadas.")
        
        ttk.Label(self.frame_dimensiones, text="Ancho (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_ancho = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_ancho.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(self.frame_dimensiones, text="Profundidad (in):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_profundidad = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_profundidad.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(self.frame_dimensiones, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_cantidad = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_cantidad.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.entry_cantidad.insert(0, "1")
        
        ttk.Label(self.frame_dimensiones, text="Grosor Material (in):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_grosor = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_grosor.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.entry_grosor.insert(0, "0.75")
        
        # Combobox para estilos
        ttk.Label(self.frame_dimensiones, text="Estilo de Gabinete:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_estilo = ttk.Combobox(self.frame_dimensiones, values=["Base_normal", "Base_Drawer", "Wall_cabinet"])
        self.combo_estilo.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_estilo.current(0)
        self.combo_estilo.bind("<<ComboboxSelected>>", self.actualizar_campos_estilo)
        
        ttk.Label(self.frame_dimensiones, text="Estilo de Slider:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_slider = ttk.Combobox(self.frame_dimensiones, values=["Undermount", "Sidemount"])
        self.combo_slider.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_slider.current(0)
        
        # Frame para opciones de gavetas (inicialmente oculto)
        self.frame_opciones_gavetas = ttk.LabelFrame(self.frame_dimensiones, text="Opciones de Gavetas")
        self.frame_opciones_gavetas.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        self.frame_opciones_gavetas.grid_remove()  # Inicialmente oculto
        
        ttk.Label(self.frame_opciones_gavetas, text="Número de Gavetas:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_num_gavetas = ttk.Spinbox(self.frame_opciones_gavetas, from_=1, to=4, width=5)
        self.entry_num_gavetas.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.entry_num_gavetas.set(1)
        self.entry_num_gavetas.bind("<<Increment>>", self.actualizar_campos_gavetas)
        self.entry_num_gavetas.bind("<<Decrement>>", self.actualizar_campos_gavetas)
        
        # Contenedor para campos de altura de gavetas
        self.frame_alturas_gavetas = ttk.Frame(self.frame_opciones_gavetas)
        self.frame_alturas_gavetas.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Botón para reiniciar valores modificados
        self.btn_reiniciar_modificados = ttk.Button(self.frame_opciones_gavetas, text="Reiniciar Modificaciones", command=self.reiniciar_valores_modificados)
        self.btn_reiniciar_modificados.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Se añadirán dinámicamente los campos de altura de gavetas
        self.entries_altura_gavetas = []
        self.actualizar_campos_gavetas()
        
        # Botón para agregar gabinete
        self.btn_agregar = ttk.Button(self.frame_dimensiones, text="Agregar Gabinete", command=self.agregar_gabinete)
        self.btn_agregar.grid(row=8, column=0, columnspan=2, padx=5, pady=10)
        
        # Agregar tooltip al botón
        Tooltip(self.btn_agregar, "Agrega un nuevo gabinete a la lista con las dimensiones especificadas.")
        
        # Frame para lista de gabinetes
        self.frame_lista_gabinetes = ttk.LabelFrame(self.frame_izquierdo, text="Lista de Gabinetes")
        self.frame_lista_gabinetes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabla Treeview para gabinetes
        self.tree_gabinetes = ttk.Treeview(self.frame_lista_gabinetes, columns=("ID", "Ancho", "Alto", "Profundidad", "Estilo", "Cantidad"), show="headings")
        self.tree_gabinetes.heading("ID", text="ID")
        self.tree_gabinetes.heading("Ancho", text="Ancho")
        self.tree_gabinetes.heading("Alto", text="Alto")
        self.tree_gabinetes.heading("Profundidad", text="Prof.")
        self.tree_gabinetes.heading("Estilo", text="Estilo")
        self.tree_gabinetes.heading("Cantidad", text="Cant.")
        self.tree_gabinetes.bind("<<TreeviewSelect>>", self.seleccionar_gabinete)
        
        self.tree_gabinetes.column("ID", width=30)
        self.tree_gabinetes.column("Ancho", width=50)
        self.tree_gabinetes.column("Alto", width=50)
        self.tree_gabinetes.column("Profundidad", width=50)
        self.tree_gabinetes.column("Estilo", width=80)
        self.tree_gabinetes.column("Cantidad", width=50)
        
        # Menú contextual para gabinetes
        self.menu_gabinetes = tk.Menu(self.root, tearoff=0)
        self.menu_gabinetes.add_command(label="Eliminar", command=self.eliminar_gabinete)
        self.menu_gabinetes.add_command(label="Editar", command=self.editar_gabinete)
        self.tree_gabinetes.bind("<Button-3>", self.mostrar_menu_gabinetes)
        
        # Agregar scrollbar
        scrollbar_gabinetes = ttk.Scrollbar(self.frame_lista_gabinetes, orient=tk.VERTICAL, command=self.tree_gabinetes.yview)
        self.tree_gabinetes.configure(yscroll=scrollbar_gabinetes.set)
        scrollbar_gabinetes.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_gabinetes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para lista de piezas
        self.frame_lista_piezas = ttk.LabelFrame(self.frame_izquierdo, text="Lista de Piezas")
        self.frame_lista_piezas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabla Treeview para piezas
        self.tree_piezas = ttk.Treeview(self.frame_lista_piezas, columns=("Gabinete", "Nombre", "Ancho", "Alto", "Grosor", "Material"), show="headings")
        self.tree_piezas.heading("Gabinete", text="Gabinete")
        self.tree_piezas.heading("Nombre", text="Nombre")
        self.tree_piezas.heading("Ancho", text="Ancho")
        self.tree_piezas.heading("Alto", text="Alto")
        self.tree_piezas.heading("Grosor", text="Grosor")
        self.tree_piezas.heading("Material", text="Material")  # Nueva columna para el material
        self.tree_piezas.bind("<<TreeviewSelect>>", self.seleccionar_pieza)
        
        # Configurar el ancho de las columnas
        self.tree_piezas.column("Gabinete", width=30)
        self.tree_piezas.column("Nombre", width=80)
        self.tree_piezas.column("Ancho", width=50)
        self.tree_piezas.column("Alto", width=50)
        self.tree_piezas.column("Grosor", width=50)
        self.tree_piezas.column("Material", width=75)
        
        # Agregar scrollbar
        scrollbar_piezas = ttk.Scrollbar(self.frame_lista_piezas, orient=tk.VERTICAL, command=self.tree_piezas.yview)
        self.tree_piezas.configure(yscroll=scrollbar_piezas.set)
        scrollbar_piezas.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_piezas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para botones de control
        self.frame_control = ttk.LabelFrame(self.frame_izquierdo, text="Botones Control de Datos")
        self.frame_control.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones de control
        self.btn_cargar = ttk.Button(self.frame_control, text="Cargar Datos", command=self.cargar_datos)
        self.btn_cargar.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        self.btn_guardar = ttk.Button(self.frame_control, text="Guardar Datos", command=self.guardar_datos)
        self.btn_guardar.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        self.btn_limpiar = ttk.Button(self.frame_control, text="Limpiar Lista", command=self.limpiar_datos)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
    
    def setup_frame_central(self):
        # Dividir en dos paneles: superior e inferior
        self.paneles_central = ttk.PanedWindow(self.frame_central, orient=tk.VERTICAL)
        self.paneles_central.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel superior - Visualizador de Gabinete
        self.frame_visualizador_gabinete = ttk.LabelFrame(self.paneles_central, text="Visualizador Gabinete")
        self.paneles_central.add(self.frame_visualizador_gabinete, weight=1)
        
        # Crear pestañas para visualizador de gabinete
        self.notebook_gabinete = ttk.Notebook(self.frame_visualizador_gabinete)
        self.notebook_gabinete.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestañas para visualizador de gabinete
        self.tab_frontal_gabinete = ttk.Frame(self.notebook_gabinete)
        self.tab_lateral_gabinete = ttk.Frame(self.notebook_gabinete)
        self.tab_3d_gabinete = ttk.Frame(self.notebook_gabinete)
        self.tab_render_gabinete = ttk.Frame(self.notebook_gabinete)
        
        self.notebook_gabinete.add(self.tab_frontal_gabinete, text="Vista Frontal")
        self.notebook_gabinete.add(self.tab_lateral_gabinete, text="Vista Lateral")
        self.notebook_gabinete.add(self.tab_3d_gabinete, text="Vista 3D")
        self.notebook_gabinete.add(self.tab_render_gabinete, text="Render")
        
        # Agregar canvas para vistas 2D
        self.setup_canvas_frontal_gabinete()
        self.setup_canvas_lateral_gabinete()
        
        # Canvas para vista 3D (placeholder por ahora)
        ttk.Label(self.tab_3d_gabinete, text="Vista 3D del Gabinete").pack(padx=10, pady=10)
        ttk.Label(self.tab_render_gabinete, text="Render del Gabinete").pack(padx=10, pady=10)
        
        # Panel inferior - Visualizador de Pieza
        self.frame_visualizador_pieza = ttk.LabelFrame(self.paneles_central, text="Visualizador Pieza")
        self.paneles_central.add(self.frame_visualizador_pieza, weight=1)
        
        # Crear pestañas para visualizador de pieza
        self.notebook_pieza = ttk.Notebook(self.frame_visualizador_pieza)
        self.notebook_pieza.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestañas para visualizador de pieza
        self.tab_frontal_pieza = ttk.Frame(self.notebook_pieza)
        self.tab_lateral_pieza = ttk.Frame(self.notebook_pieza)
        self.tab_3d_pieza = ttk.Frame(self.notebook_pieza)
        self.tab_render_pieza = ttk.Frame(self.notebook_pieza)
        
        self.notebook_pieza.add(self.tab_frontal_pieza, text="Vista Frontal")
        self.notebook_pieza.add(self.tab_lateral_pieza, text="Vista Lateral")
        self.notebook_pieza.add(self.tab_3d_pieza, text="Vista 3D")
        self.notebook_pieza.add(self.tab_render_pieza, text="Render")
        
        # Agregar canvas para vistas 2D de pieza
        self.setup_canvas_frontal_pieza()
        self.setup_canvas_lateral_pieza()
        
        # Canvas para vista 3D (placeholder por ahora)
        ttk.Label(self.tab_3d_pieza, text="Vista 3D de la Pieza").pack(padx=10, pady=10)
        ttk.Label(self.tab_render_pieza, text="Render de la Pieza").pack(padx=10, pady=10)
    
    def setup_frame_derecho(self):
        """Configura el frame derecho dividido en dos secciones: editar gabinete y editar pieza"""
        # Crear paneles redimensionables en el frame derecho
        self.paneles_derecho = ttk.PanedWindow(self.frame_derecho, orient=tk.VERTICAL)
        self.paneles_derecho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame superior para editar gabinete
        self.frame_editar_gabinete = ttk.LabelFrame(self.paneles_derecho, text="Editar Gabinete")
        self.paneles_derecho.add(self.frame_editar_gabinete, weight=1)

        # Frame inferior para editar pieza
        self.frame_editar_pieza = ttk.LabelFrame(self.paneles_derecho, text="Editar Pieza")
        self.paneles_derecho.add(self.frame_editar_pieza, weight=1)

        # Inicializar los frames de edición
        self.setup_frame_editar_gabinete()
        self.setup_frame_editar_pieza()    

    def setup_canvas_frontal_gabinete(self):
        # Crear figura de matplotlib
        self.fig = plt.Figure(figsize=(4, 5), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Vista Frontal del Gabinete")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_frame_on(False)
        self.ax.set_aspect('equal', adjustable='box')

        # Crear canvas y agregarlo a la pestaña
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_frontal_gabinete)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Agregar barra de herramientas para zoom y movimiento
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tab_frontal_gabinete)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Variables para etiquetas interactivas
        self.etiqueta_interactiva = None
        self.texto_etiqueta = self.ax.text(0, 0, "", visible=False, bbox=dict(facecolor="white", alpha=0.8))
    
    def setup_canvas_lateral_gabinete(self):
        # Crear figura de matplotlib
        self.fig_lateral_gabinete = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax_lateral_gabinete = self.fig_lateral_gabinete.add_subplot(111)
        self.ax_lateral_gabinete.set_title("Vista Lateral")
        self.ax_lateral_gabinete.set_xlabel("Profundidad")
        self.ax_lateral_gabinete.set_ylabel("Alto")
        self.ax_lateral_gabinete.grid(True)
        
        # Crear canvas
        self.canvas_lateral_gabinete = FigureCanvasTkAgg(self.fig_lateral_gabinete, self.tab_lateral_gabinete)
        self.canvas_lateral_gabinete.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_canvas_frontal_pieza(self):
        # Crear figura de matplotlib
        self.fig_frontal_pieza = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax_frontal_pieza = self.fig_frontal_pieza.add_subplot(111)
        self.ax_frontal_pieza.set_title("Vista Frontal de la Pieza")
        self.ax_frontal_pieza.set_xlabel("Ancho (cm)")
        self.ax_frontal_pieza.set_ylabel("Alto (cm)")
        self.ax_frontal_pieza.grid(True)
        
        # Crear canvas
        self.canvas_frontal_pieza = FigureCanvasTkAgg(self.fig_frontal_pieza, self.tab_frontal_pieza)
        self.canvas_frontal_pieza.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_canvas_lateral_pieza(self):
        # Crear figura de matplotlib
        self.fig_lateral_pieza = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax_lateral_pieza = self.fig_lateral_pieza.add_subplot(111)
        self.ax_lateral_pieza.set_title("Vista Lateral de la Pieza")
        self.ax_lateral_pieza.set_xlabel("Grosor (cm)")
        self.ax_lateral_pieza.set_ylabel("Alto (cm)")
        self.ax_lateral_pieza.grid(True)
        
        # Crear canvas
        self.canvas_lateral_pieza = FigureCanvasTkAgg(self.fig_lateral_pieza, self.tab_lateral_pieza)
        self.canvas_lateral_pieza.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_tab_configuraciones(self):
        """Configura la pestaña de Configuraciones para gestionar materiales"""
        # Crear un frame contenedor para el MaterialManager
        self.frame_configuraciones = ttk.Frame(self.tab_configuraciones)
        self.frame_configuraciones.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Inicializar el MaterialManager dentro del frame de Configuraciones
        self.material_manager = MaterialManager(self.frame_configuraciones)
            
    def seleccionar_gabinete(self, event):
        """Maneja la selección de un gabinete en el Treeview"""
        seleccion = self.tree_gabinetes.selection()
        if seleccion:
            # Obtener el ID del gabinete seleccionado
            item = self.tree_gabinetes.item(seleccion[0])
            id_gabinete = item["values"][0]
            
            # Buscar el gabinete en la lista
            gabinete_seleccionado = None
            for gabinete in self.gabinetes:
                if gabinete["ID"] == id_gabinete:
                    gabinete_seleccionado = gabinete
                    break
            
            if gabinete_seleccionado:
                # Actualizar los campos de edición en el frame superior
                self.actualizar_campos_edicion(gabinete_seleccionado)
                
                # Actualizar la lista de piezas
                self.actualizar_lista_piezas(gabinete_seleccionado["ID"])
                
                # Actualizar la visualización 2D
                self.actualizar_visualizacion(gabinete_seleccionado)
                
                # Actualizar los detalles del gabinete
                piezas_gabinete = [p for p in self.piezas if p.get("gabinete_id") == gabinete_seleccionado["ID"]]
                self.actualizar_detalles(gabinete_seleccionado, piezas_gabinete)

    def seleccionar_pieza(self, event):
        seleccion = self.tree_piezas.selection()
        if seleccion:
            # Obtener los valores de la pieza seleccionada
            item = self.tree_piezas.item(seleccion[0])
            valores = item["values"]
            id_gabinete = valores[0]  # ID del gabinete
            nombre_pieza = valores[1]  # Nombre de la pieza

            # Buscar la pieza en la lista
            pieza_seleccionada = None
            for pieza in self.piezas:
                if pieza.get("gabinete_id") == id_gabinete and pieza["nombre"] == nombre_pieza:
                    pieza_seleccionada = pieza
                    break

            if pieza_seleccionada:
                # Actualizar las vistas de la pieza
                self.actualizar_vista_frontal_pieza(pieza_seleccionada)
                self.actualizar_vista_lateral_pieza(pieza_seleccionada)

                # Actualizar los campos de edición de la pieza
                self.actualizar_campos_edicion_pieza(pieza_seleccionada)

    def actualizar_campos_edicion_pieza(self, pieza):
        """Actualiza los campos de edición con los datos de la pieza seleccionada"""
        # Limpiar campos de edición
        self.entry_editar_nombre_pieza.delete(0, tk.END)
        self.entry_editar_ancho_pieza.delete(0, tk.END)
        self.entry_editar_alto_pieza.delete(0, tk.END)
        self.entry_editar_grosor_pieza.delete(0, tk.END)
        self.combo_material_pieza.set("")  # Limpiar el combobox de material

        # Llenar campos con los datos de la pieza
        self.entry_editar_nombre_pieza.insert(0, pieza["nombre"])
        self.entry_editar_ancho_pieza.insert(0, str(pieza["ancho"]))
        self.entry_editar_alto_pieza.insert(0, str(pieza["alto"]))
        self.entry_editar_grosor_pieza.insert(0, str(pieza.get("grosor", "")))
        self.combo_material_pieza.set(pieza.get("material", ""))  # Establecer el material en el combobox

    def actualizar_vista_frontal_pieza(self, pieza):
        self.ax_frontal_pieza.clear()
        # Dibujar la pieza en vista frontal
        self.ax_frontal_pieza.add_patch(plt.Rectangle((0, 0), pieza["ancho"], pieza["alto"], fill=False, color='blue'))
        self.ax_frontal_pieza.set_xlim(-1, pieza["ancho"] + 1)
        self.ax_frontal_pieza.set_ylim(-1, pieza["alto"] + 1)
        self.ax_frontal_pieza.set_title(f"Vista Frontal - {pieza['nombre']}")
        self.canvas_frontal_pieza.draw()

    def actualizar_vista_lateral_pieza(self, pieza):
        self.ax_lateral_pieza.clear()
        # Dibujar la pieza en vista lateral
        self.ax_lateral_pieza.add_patch(plt.Rectangle((0, 0), pieza.get("grosor", 1), pieza["alto"], fill=False, color='blue'))
        self.ax_lateral_pieza.set_xlim(-1, pieza.get("grosor", 1) + 1)
        self.ax_lateral_pieza.set_ylim(-1, pieza["alto"] + 1)
        self.ax_lateral_pieza.set_title(f"Vista Lateral - {pieza['nombre']}")
        self.canvas_lateral_pieza.draw()
    
    def actualizar_campos_estilo(self, event=None):
        estilo = self.combo_estilo.get()
        if estilo == "Base_Drawer":
            self.frame_opciones_gavetas.grid()  # Mostrar el frame de gavetas
            self.actualizar_campos_gavetas()  # Actualizar los campos de gavetas
        else:
            self.frame_opciones_gavetas.grid_remove()  # Ocultar el frame de gavetas
    
    def actualizar_campos_gavetas(self, event=None):
        """Calcula y muestra automáticamente las alturas de las gavetas en función del espacio disponible"""
        self.frame_opciones_gavetas.after(10, self._realizar_actualizacion_gavetas)

    def _realizar_actualizacion_gavetas(self):
        """Realiza la actualización de los campos de entrada de altura de gavetas"""
        # Limpiar los campos anteriores
        for widget in self.frame_alturas_gavetas.winfo_children():
            widget.destroy()

        try:
            # Obtener valores de altura total y número de gavetas
            altura_total = float(self.entry_alto.get())  
            num_gavetas = int(self.entry_num_gavetas.get())

            # Definir constantes
            toe_kick = 4  # Altura del zócalo (Toe Kick)
            espacio_entre_gavetas = 0.25  # Espaciado entre gavetas

            # Calcular espacio disponible
            self.espacio_disponible = altura_total - toe_kick - ((num_gavetas - 1) * espacio_entre_gavetas)

            # Inicializar lista de alturas y estado de modificación
            self.entries_altura_gavetas = []
            self.valores_modificados = [False] * num_gavetas  # Para rastrear cambios manuales
            self.labels_check = []  # Lista para almacenar los labels de check mark

            # Label para mostrar espacio restante
            self.label_espacio_restante = ttk.Label(self.frame_alturas_gavetas, text=f"Espacio restante: {self.espacio_disponible:.2f} cm")
            self.label_espacio_restante.grid(row=num_gavetas, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

            # Crear campos de entrada para las gavetas
            for i in range(num_gavetas):
                ttk.Label(self.frame_alturas_gavetas, text=f"Altura Gaveta {i+1} (cm):").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
                entry = ttk.Entry(self.frame_alturas_gavetas, width=10)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)

                # Insertar el valor calculado inicialmente
                altura_gaveta = self.espacio_disponible / num_gavetas
                entry.insert(0, f"{altura_gaveta:.2f}")

                # Asociar evento de cambio
                entry.bind("<KeyRelease>", lambda e, index=i: self.actualizar_espacio_restante(index))

                # Crear un Label para el check mark (inicialmente oculto)
                check_label = ttk.Label(self.frame_alturas_gavetas, text="", foreground="green")
                check_label.grid(row=i, column=2, padx=5, pady=2, sticky=tk.W)
                self.labels_check.append(check_label)

                self.entries_altura_gavetas.append(entry)

        except ValueError:
            pass  # Si hay un error (por ejemplo, campos vacíos), simplemente no hacemos nada

    def actualizar_espacio_restante(self, index_modificado):
        """Recalcula el espacio restante cuando se modifica manualmente un campo de entrada"""
        try:
            # Obtener valores actuales de las gavetas
            valores_gavetas = []
            total_modificado = 0
            num_modificados = 0

            for i, entry in enumerate(self.entries_altura_gavetas):
                try:
                    valor = float(entry.get())
                    valores_gavetas.append(valor)
                    
                    if self.valores_modificados[i]:  # Si ya fue modificado antes
                        total_modificado += valor
                        num_modificados += 1
                except ValueError:
                    valores_gavetas.append(None)  # Si hay un valor no válido, ignorarlo

            # Marcar el campo como modificado
            self.valores_modificados[index_modificado] = True

            # Mostrar el check mark junto al campo modificado
            self.labels_check[index_modificado].config(text="✔️")

            # Calcular espacio restante
            espacio_restante = self.espacio_disponible - total_modificado

            # Si la suma total de alturas supera el espacio disponible
            if total_modificado > self.espacio_disponible:
                # Preguntar al usuario si desea redimensionar automáticamente
                respuesta = messagebox.askyesno(
                    "Redimensionar gavetas",
                    "La suma de las alturas de las gavetas supera el espacio disponible. ¿Deseas redimensionar automáticamente las otras gavetas?"
                )

                if respuesta:  # Si el usuario acepta
                    # Obtener el valor que se está modificando
                    valor_modificado = valores_gavetas[index_modificado]

                    # Calcular el espacio restante después de conservar el valor modificado
                    espacio_restante = self.espacio_disponible - valor_modificado

                    # Dividir el espacio restante entre las otras gavetas
                    num_gavetas_restantes = len(self.entries_altura_gavetas) - 1
                    nueva_altura = espacio_restante / num_gavetas_restantes

                    # Actualizar las otras gavetas
                    for i, entry in enumerate(self.entries_altura_gavetas):
                        if i != index_modificado:  # No modificar el campo que se está editando
                            entry.delete(0, tk.END)
                            entry.insert(0, f"{nueva_altura:.2f}")

                    # Actualizar el espacio restante en el Label
                    self.label_espacio_restante.config(text=f"Espacio restante: 0.00 cm")
                else:
                    # Si el usuario no acepta, no hacer nada y dejar que el usuario ingrese otro valor
                    return

            # Si hay espacio disponible, mostrarlo en el Label
            self.label_espacio_restante.config(text=f"Espacio restante: {espacio_restante:.2f} cm")

            # Si la suma es menor, dividir el espacio restante entre las gavetas no modificadas
            if espacio_restante > 0 and num_modificados < len(valores_gavetas):
                nueva_altura = espacio_restante / (len(valores_gavetas) - num_modificados)

                for i, entry in enumerate(self.entries_altura_gavetas):
                    if not self.valores_modificados[i]:  # Solo actualizar las que no han sido modificadas
                        entry.delete(0, tk.END)
                        entry.insert(0, f"{nueva_altura:.2f}")

        except ValueError:
            pass  # Manejar errores si los valores ingresados no son numéricos
        
    def actualizar_campos_gavetas_editar(self, event=None):
        """Actualiza los campos de altura de gavetas en el frame de ingreso de datos"""
        # Programar la actualización después de un breve retraso
        self.frame_opciones_gavetas.after(10, self.actualizar_campos_gavetas_editar1)

    def actualizar_campos_gavetas_editar1(self, event=None, num_gavetas=None, gabinete=None):
        """Actualiza los campos de altura de gavetas en el frame de edición, evitando que superen el espacio disponible"""
        if num_gavetas is None:
            num_gavetas = int(self.entry_editar_num_gavetas.get())

        # Limpiar frame de alturas de gavetas
        for widget in self.frame_alturas_gavetas_editar.winfo_children():
            widget.destroy()

        try:
            # Obtener la altura total del gabinete
            altura_total = float(self.entry_editar_alto.get())

            # Definir constantes
            toe_kick = 4  # Altura del zócalo
            espacio_entre_gavetas = 0.25  # Espacio entre gavetas

            # Calcular espacio disponible
            self.espacio_disponible_editar = altura_total - toe_kick - ((num_gavetas - 1) * espacio_entre_gavetas)

            # Inicializar lista de alturas y estado de modificación
            self.entries_altura_gavetas_editar = []
            self.valores_modificados_editar = [False] * num_gavetas  # Para rastrear cambios manuales
            self.labels_check_editar = []  # Lista para almacenar los labels de check mark

            # Label para mostrar espacio restante
            self.label_espacio_restante = ttk.Label(self.frame_alturas_gavetas_editar, text=f"Espacio restante: {self.espacio_disponible_editar:.2f} cm")
            self.label_espacio_restante.grid(row=num_gavetas, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

            # Crear campos de entrada para cada gaveta
            for i in range(num_gavetas):
                ttk.Label(self.frame_alturas_gavetas_editar, text=f"Altura Gaveta {i+1} (cm):").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
                entry = ttk.Entry(self.frame_alturas_gavetas_editar, width=10)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)

                # Insertar el valor desde el gabinete si existe, de lo contrario calcularlo
                if gabinete and f"high_drawer_{i}" in gabinete:
                    entry.insert(0, str(gabinete[f"high_drawer_{i}"]))
                    self.valores_modificados_editar[i] = True  # Marcar como modificado si viene del JSON
                else:
                    altura_gaveta = self.espacio_disponible_editar / num_gavetas
                    entry.insert(0, f"{altura_gaveta:.2f}")

                # Asociar evento de cambio
                entry.bind("<KeyRelease>", lambda e, index=i: self.actualizar_espacio_restante_editar(index))

                # Crear un Label para el check mark (inicialmente oculto)
                check_label = ttk.Label(self.frame_alturas_gavetas_editar, text="", foreground="green")
                check_label.grid(row=i, column=2, padx=5, pady=2, sticky=tk.W)
                self.labels_check_editar.append(check_label)

                self.entries_altura_gavetas_editar.append(entry)

            # Botón para reiniciar valores modificados
            self.btn_reiniciar_modificados_editar = ttk.Button(self.frame_alturas_gavetas_editar, text="Reiniciar Modificaciones", command=self.reiniciar_valores_modificados_editar)
            self.btn_reiniciar_modificados_editar.grid(row=num_gavetas + 1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)

        except ValueError:
            pass  # Manejar error si los valores ingresados no son numéricos
        
    def actualizar_espacio_restante_editar(self, index_modificado):
        """Recalcula el espacio restante cuando se modifica manualmente un campo de entrada en la edición de un gabinete,
        asegurando que el total no supere el espacio disponible"""
        try:
            # Obtener valores actuales de las gavetas
            valores_gavetas = []
            total_modificado = 0
            num_modificados = 0

            for i, entry in enumerate(self.entries_altura_gavetas_editar):
                try:
                    valor = float(entry.get())
                    valores_gavetas.append(valor)
                    
                    if self.valores_modificados_editar[i]:  # Si ya fue modificado antes
                        total_modificado += valor
                        num_modificados += 1
                except ValueError:
                    valores_gavetas.append(None)  # Si hay un valor no válido, ignorarlo

            # Marcar el campo como modificado
            self.valores_modificados_editar[index_modificado] = True

            # Mostrar el check mark junto al campo modificado
            self.labels_check_editar[index_modificado].config(text="✔️")

            # Calcular espacio restante
            espacio_restante = self.espacio_disponible_editar - total_modificado

            # Si la suma total de alturas supera el espacio disponible
            if total_modificado > self.espacio_disponible_editar:
                # Preguntar al usuario si desea redimensionar automáticamente
                respuesta = messagebox.askyesno(
                    "Redimensionar gavetas",
                    "La suma de las alturas de las gavetas supera el espacio disponible. ¿Deseas redimensionar automáticamente las otras gavetas?"
                )

                if respuesta:  # Si el usuario acepta
                    # Obtener el valor que se está modificando
                    valor_modificado = valores_gavetas[index_modificado]

                    # Calcular el espacio restante después de conservar el valor modificado
                    espacio_restante = self.espacio_disponible_editar - valor_modificado

                    # Dividir el espacio restante entre las otras gavetas
                    num_gavetas_restantes = len(self.entries_altura_gavetas_editar) - 1
                    nueva_altura = espacio_restante / num_gavetas_restantes

                    # Actualizar las otras gavetas
                    for i, entry in enumerate(self.entries_altura_gavetas_editar):
                        if i != index_modificado:  # No modificar el campo que se está editando
                            entry.delete(0, tk.END)
                            entry.insert(0, f"{nueva_altura:.2f}")

                    # Actualizar el espacio restante en el Label
                    self.label_espacio_restante.config(text=f"Espacio restante: 0.00 cm")
                else:
                    # Si el usuario no acepta, no hacer nada y dejar que el usuario ingrese otro valor
                    return

            # Si hay espacio disponible, mostrarlo en el Label
            self.label_espacio_restante.config(text=f"Espacio restante: {espacio_restante:.2f} cm")

            # Si la suma es menor, dividir el espacio restante entre las gavetas no modificadas
            if espacio_restante > 0 and num_modificados < len(valores_gavetas):
                nueva_altura = espacio_restante / (len(valores_gavetas) - num_modificados)

                for i, entry in enumerate(self.entries_altura_gavetas_editar):
                    if not self.valores_modificados_editar[i]:  # Solo actualizar las que no han sido modificadas
                        entry.delete(0, tk.END)
                        entry.insert(0, f"{nueva_altura:.2f}")

        except ValueError:
            pass  # Manejar errores si los valores ingresados no son numéricos    
        
    def calcular_piezas(self, gabinete):
        """
        Calcula las piezas necesarias para un gabinete según su estilo.
        """
        estilo = gabinete["Estilo"]

        if estilo == "Base_normal":
            return self.calcular_piezas_base_normal(gabinete)
        elif estilo == "Base_Drawer":
            return self.calcular_piezas_base_drawer(gabinete)  # Ya existe en el código
        elif estilo == "Wall_cabinet":
            return self.calcular_piezas_wall_cabinet(gabinete)  # Lo implementaremos después
        else:
            return []  # Estilo no reconocido

    def agregar_gabinete(self):
        try:
            # Validar y obtener datos
            gabinete = self.obtener_datos_gabinete()
            piezas_gabinete = self.calcular_piezas(gabinete)
            
            # Añadir relación con el gabinete
            for pieza in piezas_gabinete:
                pieza["gabinete_id"] = gabinete["ID"]
                pieza["grosor"] = gabinete["Espesor"]
            
            # Agregar a listas
            self.gabinetes.append(gabinete)
            self.piezas.extend(piezas_gabinete)
            
            # Actualizar UI
            self.actualizar_ui_despues_de_agregar(gabinete, piezas_gabinete)
            
            self.autoguardar_datos()
            
            # Limpiar campos
            self.limpiar_campos_ingreso()
            
            messagebox.showinfo("Éxito", f"Gabinete {gabinete['ID']} agregado correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")

    def obtener_datos_gabinete(self):
        alto = float(self.entry_alto.get())
        ancho = float(self.entry_ancho.get())
        profundidad = float(self.entry_profundidad.get())
        cantidad = int(self.entry_cantidad.get())
        grosor = float(self.entry_grosor.get())
        estilo = self.combo_estilo.get()
        slider = self.combo_slider.get()
        
        gabinete = {
            "ID": str(uuid.uuid4())[:8],
            "Alto": alto,
            "Ancho": ancho,
            "Profundidad": profundidad,
            "Cantidad": cantidad,
            "Espesor": grosor,
            "Estilo": estilo,
            "Slider": slider
        }
        
        if estilo == "Base_Drawer":
            num_gavetas = int(self.entry_num_gavetas.get())
            gabinete["num_gavetas"] = num_gavetas
            for i, entry in enumerate(self.entries_altura_gavetas):
                if entry.get():
                    gabinete[f"high_drawer_{i}"] = float(entry.get())
        
        return gabinete

    def actualizar_ui_despues_de_agregar(self, gabinete, piezas_gabinete):
        self.actualizar_lista_gabinetes()
        self.actualizar_lista_piezas()
        self.actualizar_visualizacion(gabinete)
        self.actualizar_detalles(gabinete, piezas_gabinete)
        self.actualizar_resumen_materiales()

    def limpiar_campos_ingreso(self):
        self.entry_alto.delete(0, tk.END)
        self.entry_ancho.delete(0, tk.END)
        self.entry_profundidad.delete(0, tk.END)
    
    def calcular_piezas_base_drawer(self, gabinete):
        """Calcula las piezas necesarias para un gabinete de estilo Base_Drawer"""
        gap = 0.125  # Espacio entre gavetas
        toe_kick = 4  # Altura del zócalo (Toe Kick)
        espacio_entre_gavetas = 0.25  # Espacio entre gavetas
        total = 6  # Total de orificios para estantes
        front = 2  # Distancia frontal de los orificios
        rear = 2  # Distancia trasera de los orificios
        top = 14  # Distancia superior de los orificios
        botton = 12  # Distancia inferior de los orificios
        space = 1.26  # Separación entre orificios
        rows = 2  # Filas de orificios
        dia = 0.25  # Diámetro de los orificios

        # Obtener el valor de drawer_mount según la selección del combobox
        slider = gabinete.get("Slider", "Undermount")  # Valor predeterminado: Undermount
        if slider == "Undermount":
            drawer_mount = 0.375
        elif slider == "Sidemount":
            drawer_mount = 1
        else:
            drawer_mount = 3  # Valor predeterminado si no se selecciona nada

        cantidad_gavetas = gabinete.get("num_gavetas", 1)  # Número de gavetas
        altura_disponible = gabinete["Alto"] - toe_kick - ((cantidad_gavetas - 1) * espacio_entre_gavetas)  # Altura disponible para gavetas

        # Calcular alturas de las gavetas
        alturas_gavetas = []
        for i in range(cantidad_gavetas):
            key = f"high_drawer_{i}"
            if key in gabinete:
                alturas_gavetas.append(gabinete[key])  # Usar altura definida por el usuario
            else:
                alturas_gavetas.append(altura_disponible / cantidad_gavetas)  # Dividir altura disponible entre las gavetas

        # Lista de piezas del gabinete
        piezas = [
            # Laterales
            {"nombre": "Lateral Izquierdo", "ancho": gabinete["Profundidad"] - 1, "alto": gabinete["Alto"], "material": "Plywood 3/4",
            "orificios_shelf": {"cantidad": total, "diametro": dia, "filas": rows, "distancia_frontal": front, "distancia_trasera": rear, "separacion": space, "distancia_inferior": botton, "distancia_superior": top}},
            {"nombre": "Lateral Derecho", "ancho": gabinete["Profundidad"] - 1, "alto": gabinete["Alto"], "material": "Plywood 3/4",
            "orificios_shelf": {"cantidad": total, "diametro": dia, "filas": rows, "distancia_frontal": front, "distancia_trasera": rear, "separacion": space, "distancia_inferior": botton, "distancia_superior": top}},

            # Base
            {"nombre": "Base", "ancho": gabinete["Ancho"] - 2 * gabinete["Espesor"], "alto": gabinete["Profundidad"] - 1, "material": "Plywood 3/4"},

            # Trasera
            {"nombre": "Trasera", "ancho": gabinete["Ancho"], "alto": gabinete["Alto"] - gabinete["Espesor"], "material": "Plywood 1/2"},

            # Rails (superior, media)
            {"nombre": "Under Drawer Rail Superior", "ancho": gabinete["Ancho"] - 2 * gabinete["Espesor"], "alto": 3, "material": "Plywood 3/4"},
            {"nombre": "Upper Drawer Rail Superior", "ancho": gabinete["Ancho"] - 2 * gabinete["Espesor"], "alto": 3, "material": "Plywood 3/4"},
            {"nombre": "Rear Drawer Rail Superior", "ancho": gabinete["Ancho"] - 2 * gabinete["Espesor"], "alto": 3, "material": "Plywood 3/4"},
            {"nombre": "Under Drawer Rail Media", "ancho": gabinete["Ancho"] - 2 * gabinete["Espesor"], "alto": 3, "material": "Plywood 3/4"},

            # Toe Kick (zócalo)
            {"nombre": "Toe Kick", "ancho": gabinete["Ancho"], "alto": toe_kick, "material": "Plywood 3/4"},
        ]

        # Agregar las caras de las gavetas (Drawer Faces)
        for i, altura_gaveta in enumerate(alturas_gavetas):
            piezas.append({
                "nombre": f"Drawer Face {i+1}",
                "ancho": gabinete["Ancho"] - gap,  # Ajuste para el espacio entre gavetas
                "alto": altura_gaveta,
                "material": "Medex 3/4"  # Material para las caras de las gavetas
            })

        # Determinar profundidad para las cajas de gavetas (Box Drawers)
        profundidad_box_drawer = 21  # Valor predeterminado
        if gabinete["Profundidad"] > 26:
            profundidad_box_drawer = 24
        elif gabinete["Profundidad"] > 23:
            profundidad_box_drawer = 21
        elif gabinete["Profundidad"] > 20:
            profundidad_box_drawer = 18
        elif gabinete["Profundidad"] > 17:
            profundidad_box_drawer = 15
        elif gabinete["Profundidad"] > 14:
            profundidad_box_drawer = 12
        elif gabinete["Profundidad"] > 11:
            profundidad_box_drawer = 9

        # Agregar las cajas de gavetas (Box Drawers)
        for i, altura_gaveta in enumerate(alturas_gavetas):
            # Determinar la altura de la Box Drawer
            if i == len(alturas_gavetas) - 1:  # Última gaveta
                altura_box_drawer = altura_gaveta - 2.125
            else:  # Las demás gavetas
                altura_box_drawer = altura_gaveta - 1.75

            piezas.append({
                "nombre": f"Box Drawer {i+1}",
                "ancho": gabinete["Ancho"] - drawer_mount - (gabinete["Espesor"] * 2),  # Ajuste para el montaje de la gaveta
                "alto": altura_box_drawer,
                "profundidad": profundidad_box_drawer,
                "material": "Plywood 5/8"  # Material para las cajas de gavetas
            })

        return piezas
    
    def calcular_piezas_base_normal(self, gabinete):
        """
        Calcula las piezas necesarias para un gabinete de estilo "Base_normal".
        Incluye una gaveta en la parte superior, puertas en la parte inferior,
        y la caja de la gaveta (Box Drawer).
        """
        piezas = []

        # Dimensiones del gabinete
        ancho = gabinete["Ancho"]
        alto = gabinete["Alto"]
        profundidad = gabinete["Profundidad"]
        grosor = gabinete["Espesor"]

        # Obtener el valor de drawer_mount según la selección del combobox
        slider = gabinete.get("Slider", "Undermount")  # Valor predeterminado: Undermount
        if slider == "Undermount":
            drawer_mount = 0.375
        elif slider == "Sidemount":
            drawer_mount = 1
        else:
            drawer_mount = 3  # Valor predeterminado si no se selecciona nada

        # Piezas básicas del gabinete
        piezas.extend([
            {"nombre": "Lateral Izquierdo", "ancho": profundidad - 1, "alto": alto, "material": "Plywood 3/4"},
            {"nombre": "Lateral Derecho", "ancho": profundidad - 1, "alto": alto, "material": "Plywood 3/4"},
            {"nombre": "Base", "ancho": ancho - 2 * grosor, "alto": profundidad - 1, "material": "Plywood 3/4"},
            {"nombre": "Techo", "ancho": ancho - 2 * grosor, "alto": profundidad - 1, "material": "Plywood 3/4"},
            {"nombre": "Trasera", "ancho": ancho, "alto": alto - grosor, "material": "Plywood 1/2"},
        ])

        # Toe Kick (zócalo)
        piezas.append({"nombre": "Toe Kick", "ancho": ancho, "alto": 4, "material": "Plywood 3/4"})

        # Gaveta superior
        altura_gaveta = gabinete.get("altura_gaveta", 6)  # Usar el valor guardado o 6 cm por defecto
        piezas.append({
            "nombre": "Gaveta Superior",
            "ancho": ancho - 0.125,  # Ajuste para el espacio entre gavetas
            "alto": altura_gaveta,
            "profundidad": profundidad - 1,  # Profundidad de la gaveta
            "material": "Medex 3/4"
        })

        # Box Drawer (caja de la gaveta)
        # Determinar profundidad para la caja de la gaveta
        profundidad_box_drawer = 21  # Valor predeterminado
        if profundidad > 26:
            profundidad_box_drawer = 24
        elif profundidad > 23:
            profundidad_box_drawer = 21
        elif profundidad > 20:
            profundidad_box_drawer = 18
        elif profundidad > 17:
            profundidad_box_drawer = 15
        elif profundidad > 14:
            profundidad_box_drawer = 12
        elif profundidad > 11:
            profundidad_box_drawer = 9

        # Calcular la altura de la Box Drawer restando 1.75 a la altura de la Gaveta Superior
        altura_box_drawer = altura_gaveta - 1.75

        # Agregar la caja de la gaveta
        piezas.append({
            "nombre": "Box Drawer",
            "ancho": ancho - drawer_mount - (grosor * 2),  # Ajuste para el montaje de la gaveta
            "alto": altura_box_drawer,  # Altura calculada
            "profundidad": profundidad_box_drawer,
            "material": "Plywood 5/8"
        })

        # Puertas inferiores
        altura_puerta = alto - 4 - altura_gaveta  # Restando el toe kick y la gaveta
        if ancho > 18:
            # Si el ancho es mayor a 18", agregar dos puertas
            ancho_puerta = (ancho / 2) - 0.125  # Ajuste para el espacio entre puertas
            piezas.extend([
                {"nombre": "Puerta Izquierda", "ancho": ancho_puerta, "alto": altura_puerta, "material": "Medex 3/4"},
                {"nombre": "Puerta Derecha", "ancho": ancho_puerta, "alto": altura_puerta, "material": "Medex 3/4"},
            ])
        else:
            # Si el ancho es 18" o menor, agregar una sola puerta
            piezas.append({"nombre": "Puerta", "ancho": ancho, "alto": altura_puerta, "material": "Medex 3/4"})

        return piezas

    def calcular_piezas_wall_cabinet(self, gabinete):
        """
        Calcula las piezas necesarias para un gabinete de estilo "Wall_cabinet".
        Incluye puertas, estantes y piezas básicas.
        """
        piezas = []

        # Dimensiones del gabinete
        ancho = gabinete["Ancho"]
        alto = gabinete["Alto"]
        profundidad = gabinete["Profundidad"]
        grosor = gabinete["Espesor"]

        # Piezas básicas del gabinete
        piezas.extend([
            {"nombre": "Lateral Izquierdo", "ancho": profundidad - 1, "alto": alto, "material": "Plywood 3/4"},
            {"nombre": "Lateral Derecho", "ancho": profundidad - 1, "alto": alto, "material": "Plywood 3/4"},
            {"nombre": "Base", "ancho": ancho - 2 * grosor, "alto": profundidad - 1, "material": "Plywood 3/4"},
            {"nombre": "Techo", "ancho": ancho - 2 * grosor, "alto": profundidad - 1, "material": "Plywood 3/4"},
            {"nombre": "Trasera", "ancho": ancho, "alto": alto - grosor, "material": "Plywood 1/2"},
        ])

        # Estante (fijo en la mitad del gabinete)
        altura_estante = alto / 2  # Estante en la mitad del gabinete
        piezas.append({
            "nombre": "Estante",
            "ancho": ancho - 2 * grosor,  # Ajuste para el grosor del material
            "alto": profundidad - 2,  # Profundidad del estante
            "material": "Plywood 3/4"
        })

        # Puertas
        if ancho > 18:  # Si el ancho es mayor a 18", agregar dos puertas
            ancho_puerta = (ancho / 2) - 0.125  # Ajuste para el espacio entre puertas
            piezas.extend([
                {"nombre": "Puerta Izquierda", "ancho": ancho_puerta, "alto": alto, "material": "Medex 3/4"},
                {"nombre": "Puerta Derecha", "ancho": ancho_puerta, "alto": alto, "material": "Medex 3/4"},
            ])
        else:  # Si el ancho es 18" o menor, agregar una sola puerta
            piezas.append({"nombre": "Puerta", "ancho": ancho, "alto": alto, "material": "Medex 3/4"})

        return piezas

    def autoguardar_datos(self):
        """Guarda automáticamente los datos en el archivo temporal"""
        # Preparar datos
        datos = {
            "gabinetes": self.gabinetes,
            "piezas": self.piezas
        }

        try:
            with open(self.archivo_temp, "w") as archivo:
                json.dump(datos, archivo, indent=4)
            print(f"Autoguardado: {len(self.gabinetes)} gabinetes guardados en {self.archivo_temp}")
            return True
        except Exception as e:
            print(f"Error al autoguardar: {str(e)}")
            return False
    
    def guardar_datos(self):
        if not self.gabinetes:
            messagebox.showwarning("Advertencia", "No hay gabinetes para guardar")
            return
        
        # Solicitar ubicación para guardar
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
        
        # Preparar datos
        datos = {
            "gabinetes": self.gabinetes,
            "piezas": self.piezas
        }
        
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            
            self.archivo_actual = archivo
            messagebox.showinfo("Éxito", f"Datos guardados en {archivo}")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo: {str(e)}")
    
    def cargar_datos(self):
        # Solicitar archivo para cargar
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if not archivo:
            return
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            self.gabinetes = datos.get("gabinetes", [])
            self.piezas = datos.get("piezas", [])
            
            self.archivo_actual = archivo
            
            # Actualizar UI
            self.actualizar_lista_gabinetes()
            self.actualizar_lista_piezas()
            self.actualizar_resumen_materiales()
            
            messagebox.showinfo("Éxito", f"Datos cargados desde {archivo}")
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar el archivo: {str(e)}")
            
    def actualizar_lista_gabinetes(self):
        """Actualiza la lista de gabinetes en el Treeview"""
        # Limpiar lista actual
        for item in self.tree_gabinetes.get_children():
            self.tree_gabinetes.delete(item)
        
        # Agregar gabinetes a la lista
        for gabinete in self.gabinetes:
            self.tree_gabinetes.insert("", "end", values=(
                gabinete["ID"],
                gabinete["Ancho"],
                gabinete["Alto"],
                gabinete["Profundidad"],
                gabinete["Estilo"],
                gabinete["Cantidad"]
            ))

    def actualizar_lista_piezas(self, gabinete_id=None):
        """Actualiza la lista de piezas en el Treeview, mostrando solo las piezas del gabinete seleccionado"""
        # Limpiar lista actual
        for item in self.tree_piezas.get_children():
            self.tree_piezas.delete(item)
        
        # Filtrar piezas por gabinete_id si se proporciona
        piezas_filtradas = [p for p in self.piezas if p.get("gabinete_id") == gabinete_id] if gabinete_id else self.piezas
        
        # Agregar piezas a la lista
        for pieza in piezas_filtradas:
            self.tree_piezas.insert("", "end", values=(
                pieza.get("gabinete_id", ""),
                pieza["nombre"],
                pieza["ancho"],
                pieza["alto"],
                pieza.get("grosor", ""),
                pieza.get("material", "")
            ))

    def actualizar_visualizacion(self, gabinete):
        """Actualiza la visualización 2D del gabinete seleccionado"""
        # Limpiar figura actual
        self.ax.clear()
        
        # Definir variables de espacio
        espacio_lateral = 0.0625  # Espacio lateral a cada lado
        gap_vertical = 0.125       # Espacio vertical entre gavetas y puertas
        gap_horizontal = 0.125     # Espacio horizontal entre puertas
        
        # Obtener dimensiones del gabinete
        ancho = gabinete["Ancho"]
        alto = gabinete["Alto"]
        
        # Configurar los límites de los ejes
        self.ax.set_xlim(0, ancho)
        self.ax.set_ylim(0, alto)
        
        # Quitar los números de los ejes
        self.ax.set_xticks([])  # Quitar números del eje X
        self.ax.set_yticks([])  # Quitar números del eje Y
        
        # Establecer la relación de aspecto para que sea igual (evitar estiramiento)
        self.ax.set_aspect('equal', adjustable='box')
        
        # Dibujar el contorno del gabinete
        self.ax.add_patch(plt.Rectangle((0, 0), ancho, alto, fill=False, color='black', linewidth=2))
        
        # Agregar etiquetas de dimensiones
        self.ax.text(ancho / 2, -1, f"Ancho: {ancho} in", 
                    horizontalalignment='center', verticalalignment='top', fontsize=10)
        self.ax.text(-2, alto / 2, f"Alto: {alto} in", 
                    rotation=90, horizontalalignment='right', verticalalignment='center', fontsize=10)
    
        
        # Si es un gabinete con gavetas (Base_Drawer), dibujarlas
        if gabinete["Estilo"] == "Base_Drawer":
            num_gavetas = gabinete.get("num_gavetas", 1)
            
            # Calcular la posición del toe kick
            toe_kick_height = 4  # Altura estándar del toe kick
            y_start = alto  # Comenzar desde la parte superior
            
            # Dibujar toe kick con contorno
            self.ax.add_patch(plt.Rectangle((0, 0), ancho, toe_kick_height, 
                            facecolor='white', edgecolor='black', linewidth=2))
            
            # Dibujar gavetas desde arriba hacia abajo
            for i in range(num_gavetas):
                altura_key = f"high_drawer_{i}"
                
                if altura_key in gabinete:
                    altura_gaveta = gabinete[altura_key]
                else:
                    # Calcular altura proporcional si no está especificada
                    altura_gaveta = (alto - toe_kick_height) / num_gavetas
                
                # Ajustar la posición de la gaveta (comenzar desde arriba)
                y_start -= altura_gaveta
                
                # Dibujar gaveta con contorno
                self.ax.add_patch(plt.Rectangle((espacio_lateral, y_start), 
                                ancho - 2 * espacio_lateral, altura_gaveta, 
                                facecolor='white', edgecolor='black', linewidth=1))
                
                # Dibujar rectángulos en los bordes de la gaveta
                self._dibujar_bordes_gaveta_puerta(espacio_lateral, y_start, 
                                                ancho - 2 * espacio_lateral, altura_gaveta)
                
                # Agregar texto de número de gaveta
                self.ax.text(ancho/2, y_start + altura_gaveta/2, f"Gaveta {i+1}", 
                        horizontalalignment='center', verticalalignment='center')
                
                # Agregar espacio entre gavetas (gap_vertical)
                y_start -= gap_vertical
        
        # Si es un gabinete base normal (Base_normal), dibujar gaveta superior y puertas inferiores
        elif gabinete["Estilo"] == "Base_normal":
            toe_kick_height = 4  # Altura del toe kick
            altura_gaveta = gabinete.get("altura_gaveta", 6)  # Altura de la gaveta superior
            
            # Dibujar toe kick con contorno
            self.ax.add_patch(plt.Rectangle((0, 0), ancho, toe_kick_height, 
                            facecolor='white', edgecolor='black', linewidth=2))
            
            # Dibujar gaveta superior con contorno
            self.ax.add_patch(plt.Rectangle((espacio_lateral, alto - altura_gaveta), 
                            ancho - 2 * espacio_lateral, altura_gaveta, 
                            facecolor='white', edgecolor='black', linewidth=1))
            
            # Dibujar rectángulos en los bordes de la gaveta superior
            self._dibujar_bordes_gaveta_puerta(espacio_lateral, alto - altura_gaveta, 
                                            ancho - 2 * espacio_lateral, altura_gaveta)
            
            # Agregar texto de gaveta superior
            self.ax.text(ancho/2, alto - altura_gaveta/2, "Gaveta Superior", 
                    horizontalalignment='center', verticalalignment='center')
            
            # Dibujar puertas inferiores
            altura_puerta = alto - toe_kick_height - altura_gaveta - gap_vertical  # Altura de las puertas
            if ancho > 18:  # Si el ancho es mayor a 18", dibujar dos puertas
                ancho_puerta = (ancho - 2 * espacio_lateral - gap_horizontal) / 2  # Ancho de cada puerta
                # Puerta izquierda
                self.ax.add_patch(plt.Rectangle((espacio_lateral, toe_kick_height), 
                                ancho_puerta, altura_puerta, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral, toe_kick_height, 
                                                ancho_puerta, altura_puerta)
                self.ax.text(espacio_lateral + ancho_puerta/2, toe_kick_height + altura_puerta/2, 
                        "Puerta Izq.", horizontalalignment='center', verticalalignment='center')
                # Puerta derecha
                self.ax.add_patch(plt.Rectangle((espacio_lateral + ancho_puerta + gap_horizontal, toe_kick_height), 
                                ancho_puerta, altura_puerta, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral + ancho_puerta + gap_horizontal, toe_kick_height, 
                                                ancho_puerta, altura_puerta)
                self.ax.text(espacio_lateral + ancho_puerta * 1.5 + gap_horizontal, toe_kick_height + altura_puerta/2, 
                        "Puerta Der.", horizontalalignment='center', verticalalignment='center')
            else:  # Si el ancho es 18" o menor, dibujar una sola puerta
                self.ax.add_patch(plt.Rectangle((espacio_lateral, toe_kick_height), 
                                ancho - 2 * espacio_lateral, altura_puerta, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral, toe_kick_height, 
                                                ancho - 2 * espacio_lateral, altura_puerta)
                self.ax.text(ancho/2, toe_kick_height + altura_puerta/2, "Puerta", 
                        horizontalalignment='center', verticalalignment='center')
        
        # Si es un gabinete de pared (Wall_cabinet), dibujar puertas y estante
        elif gabinete["Estilo"] == "Wall_cabinet":
            # Dibujar puertas
            if ancho > 18:  # Si el ancho es mayor a 18", dibujar dos puertas
                ancho_puerta = (ancho - 2 * espacio_lateral - gap_horizontal) / 2  # Ancho de cada puerta
                # Puerta izquierda
                self.ax.add_patch(plt.Rectangle((espacio_lateral, 0), ancho_puerta, alto, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral, 0, ancho_puerta, alto)
                self.ax.text(espacio_lateral + ancho_puerta/2, alto/2, "Puerta Izq.", 
                        horizontalalignment='center', verticalalignment='center')
                # Puerta derecha
                self.ax.add_patch(plt.Rectangle((espacio_lateral + ancho_puerta + gap_horizontal, 0), 
                                ancho_puerta, alto, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral + ancho_puerta + gap_horizontal, 0, 
                                                ancho_puerta, alto)
                self.ax.text(espacio_lateral + ancho_puerta * 1.5 + gap_horizontal, alto/2, "Puerta Der.", 
                        horizontalalignment='center', verticalalignment='center')
            else:  # Si el ancho es 18" o menor, dibujar una sola puerta
                self.ax.add_patch(plt.Rectangle((espacio_lateral, 0), ancho - 2 * espacio_lateral, alto, 
                                facecolor='white', edgecolor='black', linewidth=1))
                self._dibujar_bordes_gaveta_puerta(espacio_lateral, 0, ancho - 2 * espacio_lateral, alto)
                self.ax.text(ancho/2, alto/2, "Puerta", 
                        horizontalalignment='center', verticalalignment='center')
        
        # Configurar límites y etiquetas
        self.ax.set_title(f"Vista Previa - {gabinete['Estilo']} ({gabinete['ID']})")
        self.ax.grid(False)
        
        # Actualizar canvas
        self.canvas.draw()
    
    def _dibujar_bordes_gaveta_puerta(self, x, y, ancho, alto):
        """Dibuja los bordes (rectángulos) alrededor de una gaveta o puerta"""
        # Rectángulos en los lados izquierdo y derecho (2.5 cm de ancho)
        self.ax.add_patch(plt.Rectangle((x, y), 2.5, alto, fill=False, color='black', alpha=0.5))  # Izquierdo
        self.ax.add_patch(plt.Rectangle((x + ancho - 2.5, y), 2.5, alto, fill=False, color='black'))  # Derecho
        
        # Rectángulos en los bordes superior e inferior
        borde_superior_inferior_ancho = 1.5 if alto < 7 else 2.5  # Ancho del borde superior e inferior
        self.ax.add_patch(plt.Rectangle((x + 2.5, y + alto - borde_superior_inferior_ancho), 
                        ancho - 5, borde_superior_inferior_ancho, fill=False, color='black'))  # Superior
        self.ax.add_patch(plt.Rectangle((x + 2.5, y), ancho - 5, borde_superior_inferior_ancho, 
                        fill=False, color='black'))  # Inferior
            
    def actualizar_detalles(self, gabinete, piezas):
        """Actualiza el texto de detalles del gabinete seleccionado"""
        # Limpiar texto actual
        self.texto_detalles.delete(1.0, tk.END)
        
        # Añadir información general
        self.texto_detalles.insert(tk.END, f"ID: {gabinete['ID']}\n")
        self.texto_detalles.insert(tk.END, f"Estilo: {gabinete['Estilo']}\n")
        self.texto_detalles.insert(tk.END, f"Dimensiones: {gabinete['Ancho']} x {gabinete['Alto']} x {gabinete['Profundidad']}\n")
        self.texto_detalles.insert(tk.END, f"Espesor: {gabinete['Espesor']}\n")
        self.texto_detalles.insert(tk.END, f"Cantidad: {gabinete['Cantidad']}\n")
        self.texto_detalles.insert(tk.END, f"Deslizador: {gabinete['Slider']}\n\n")
        
        # Si es gabinete con gavetas, mostrar información de gavetas
        if gabinete["Estilo"] == "Base_Drawer":
            num_gavetas = gabinete.get("num_gavetas", 1)
            self.texto_detalles.insert(tk.END, f"Número de Gavetas: {num_gavetas}\n\n")
            
            for i in range(num_gavetas):
                altura_key = f"high_drawer_{i}"
                if altura_key in gabinete:
                    self.texto_detalles.insert(tk.END, f"Altura Gaveta {i+1}: {gabinete[altura_key]} cm\n")
            
            self.texto_detalles.insert(tk.END, "\n")
        
        # Mostrar lista de piezas
        self.texto_detalles.insert(tk.END, "Piezas:\n")
        for pieza in piezas:
            self.texto_detalles.insert(tk.END, f"- {pieza['nombre']}: {pieza['ancho']} x {pieza['alto']} cm\n")
        
        # Calcular volumen y área
        volumen = gabinete["Ancho"] * gabinete["Alto"] * gabinete["Profundidad"] / 1000000  # en metros cúbicos
        area_superficie = 2 * (gabinete["Ancho"] * gabinete["Alto"] + 
                        gabinete["Ancho"] * gabinete["Profundidad"] + 
                        gabinete["Alto"] * gabinete["Profundidad"]) / 10000  # en metros cuadrados
        
        self.texto_detalles.insert(tk.END, f"\nVolumen: {volumen:.3f} m³\n")
        self.texto_detalles.insert(tk.END, f"Área de Superficie: {area_superficie:.3f} m²\n")

    def actualizar_resumen_materiales(self):
        """Actualiza el resumen de materiales requeridos"""
        # Limpiar lista actual
        for item in self.tree_materiales.get_children():
            self.tree_materiales.delete(item)
        
        # Calcular materiales necesarios
        materiales = {}
        
        for pieza in self.piezas:
            # Buscar el gabinete correspondiente para multiplicar por cantidad
            gabinete_id = pieza.get("gabinete_id", "")
            cantidad = 1
            
            for gabinete in self.gabinetes:
                if gabinete["ID"] == gabinete_id:
                    cantidad = gabinete["Cantidad"]
                    break
            
            # Calcular área de la pieza
            area = (pieza["ancho"] * pieza["alto"] / 10000) * cantidad  # Convertir a m²
            
            # Determinar el tipo de material (simplificado)
            if "Drawer" in pieza["nombre"]:
                material = "Madera para Gavetas"
            elif "Lateral" in pieza["nombre"]:
                material = "Madera para Laterales"
            elif "Base" in pieza["nombre"] or "Techo" in pieza["nombre"]:
                material = "Madera para Base/Techo"
            elif "Trasera" in pieza["nombre"]:
                material = "Madera para Trasera"
            elif "Puerta" in pieza["nombre"]:
                material = "Madera para Puertas"
            elif "Estante" in pieza["nombre"]:
                material = "Madera para Estantes"
            elif "Toe Kick" in pieza["nombre"]:
                material = "Madera para Toe Kick"
            else:
                material = "Otros materiales"
            
            # Sumar al diccionario de materiales
            if material in materiales:
                materiales[material]["cantidad"] += cantidad
                materiales[material]["area"] += area
            else:
                materiales[material] = {"cantidad": cantidad, "area": area}
        
        # Agregar materiales al árbol
        for material, datos in materiales.items():
            self.tree_materiales.insert("", "end", values=(
                material,
                datos["cantidad"],
                f"{datos['area']:.2f}"
            ))

    def eliminar_gabinete(self):
        """Elimina el gabinete seleccionado"""
        seleccion = self.tree_gabinetes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay gabinete seleccionado")
            return
        
        # Obtener ID del gabinete seleccionado
        item = self.tree_gabinetes.item(seleccion[0])
        id_gabinete = item["values"][0]
        
        # Confirmar eliminación
        confirmacion = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el gabinete {id_gabinete}?")
        if not confirmacion:
            return
        
        # Eliminar gabinete
        for i, gabinete in enumerate(self.gabinetes):
            if gabinete["ID"] == id_gabinete:
                del self.gabinetes[i]
                break
        
        # Eliminar piezas asociadas
        self.piezas = [p for p in self.piezas if p.get("gabinete_id") != id_gabinete]
        
        # Actualizar UI
        self.actualizar_lista_gabinetes()
        self.actualizar_lista_piezas()
        self.actualizar_resumen_materiales()
        
        messagebox.showinfo("Éxito", f"Gabinete {id_gabinete} eliminado correctamente")

    def editar_gabinete(self):
        """Editar el gabinete seleccionado"""
        seleccion = self.tree_gabinetes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay gabinete seleccionado")
            return
        
        # Obtener ID del gabinete seleccionado
        item = self.tree_gabinetes.item(seleccion[0])
        id_gabinete = item["values"][0]
        
        # Buscar el gabinete en la lista
        gabinete_seleccionado = None
        for gabinete in self.gabinetes:
            if gabinete["ID"] == id_gabinete:
                gabinete_seleccionado = gabinete
                break
        
        if not gabinete_seleccionado:
            messagebox.showerror("Error", "No se encontró el gabinete")
            return
        
        # Crear ventana de edición
        ventana_edicion = tk.Toplevel(self.root)
        ventana_edicion.title(f"Editar Gabinete {id_gabinete}")
        ventana_edicion.geometry("500x600")
        ventana_edicion.grab_set()  # Modal
        
        # Frame para campos de edición
        frame_edicion = ttk.LabelFrame(ventana_edicion, text="Datos del Gabinete")
        frame_edicion.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos de entrada
        ttk.Label(frame_edicion, text="Alto (cm):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        entry_alto = ttk.Entry(frame_edicion, width=10)
        entry_alto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        entry_alto.insert(0, str(gabinete_seleccionado["Alto"]))
        
        ttk.Label(frame_edicion, text="Ancho (cm):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        entry_ancho = ttk.Entry(frame_edicion, width=10)
        entry_ancho.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        entry_ancho.insert(0, str(gabinete_seleccionado["Ancho"]))
        
        ttk.Label(frame_edicion, text="Profundidad (cm):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        entry_profundidad = ttk.Entry(frame_edicion, width=10)
        entry_profundidad.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        entry_profundidad.insert(0, str(gabinete_seleccionado["Profundidad"]))
        
        ttk.Label(frame_edicion, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry_cantidad = ttk.Entry(frame_edicion, width=10)
        entry_cantidad.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        entry_cantidad.insert(0, str(gabinete_seleccionado["Cantidad"]))
        
        ttk.Label(frame_edicion, text="Grosor Material (cm):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        entry_grosor = ttk.Entry(frame_edicion, width=10)
        entry_grosor.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        entry_grosor.insert(0, str(gabinete_seleccionado["Espesor"]))
        
        # Frame para opciones de gavetas (inicialmente oculto)
        frame_gavetas = ttk.LabelFrame(frame_edicion, text="Opciones de Gavetas")
        frame_gavetas.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Combobox para seleccionar el estilo de slider
        ttk.Label(frame_gavetas, text="Estilo de Slider:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        combo_slider = ttk.Combobox(frame_gavetas, values=["Undermount", "Sidemount"], width=10)
        combo_slider.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        combo_slider.set(gabinete_seleccionado.get("Slider", "Undermount"))  # Cargar valor actual
        
        # Si es un gabinete con gavetas (Base_Drawer), mostrar el frame de gavetas
        if gabinete_seleccionado["Estilo"] == "Base_Drawer":
            frame_gavetas.grid()  # Mostrar frame
            
            ttk.Label(frame_gavetas, text="Número de Gavetas:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            entry_num_gavetas = ttk.Spinbox(frame_gavetas, from_=1, to=4, width=5)
            entry_num_gavetas.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            entry_num_gavetas.set(gabinete_seleccionado.get("num_gavetas", 1))
            
            # Frame para alturas de gavetas
            frame_alturas = ttk.Frame(frame_gavetas)
            frame_alturas.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
            
            entries_altura_gavetas = []
            num_gavetas = gabinete_seleccionado.get("num_gavetas", 1)
            
            for i in range(num_gavetas):
                ttk.Label(frame_alturas, text=f"Altura Gaveta {i+1} (cm):").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
                entry = ttk.Entry(frame_alturas, width=10)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)
                
                altura_key = f"high_drawer_{i}"
                if altura_key in gabinete_seleccionado:
                    entry.insert(0, str(gabinete_seleccionado[altura_key]))
                
                entries_altura_gavetas.append(entry)
        else:
            frame_gavetas.grid_remove()  # Ocultar frame
        
        # Función para guardar cambios
        def guardar_cambios():
            try:
                # Actualizar datos
                gabinete_seleccionado["Alto"] = float(entry_alto.get())
                gabinete_seleccionado["Ancho"] = float(entry_ancho.get())
                gabinete_seleccionado["Profundidad"] = float(entry_profundidad.get())
                gabinete_seleccionado["Cantidad"] = int(entry_cantidad.get())
                gabinete_seleccionado["Espesor"] = float(entry_grosor.get())
                
                # Actualizar el estilo de slider
                gabinete_seleccionado["Slider"] = combo_slider.get()
                
                # Si es gabinete con gavetas, actualizar info de gavetas
                if gabinete_seleccionado["Estilo"] == "Base_Drawer":
                    gabinete_seleccionado["num_gavetas"] = int(entry_num_gavetas.get())
                    
                    for i, entry in enumerate(entries_altura_gavetas):
                        if entry.get():
                            gabinete_seleccionado[f"high_drawer_{i}"] = float(entry.get())
                
                # Recalcular piezas
                # Eliminar piezas actuales
                self.piezas = [p for p in self.piezas if p.get("gabinete_id") != id_gabinete]
                
                # Calcular nuevas piezas
                if gabinete_seleccionado["Estilo"] == "Base_Drawer":
                    piezas_nuevas = self.calcular_piezas_base_drawer(gabinete_seleccionado)
                elif gabinete_seleccionado["Estilo"] == "Base_normal":
                    piezas_nuevas = self.calcular_piezas_base_normal(gabinete_seleccionado)
                elif gabinete_seleccionado["Estilo"] == "Wall_cabinet":
                    piezas_nuevas = self.calcular_piezas_wall_cabinet(gabinete_seleccionado)
                else:
                    piezas_nuevas = []  # Estilo no reconocido
                
                # Añadir relación con el gabinete
                for pieza in piezas_nuevas:
                    pieza["gabinete_id"] = gabinete_seleccionado["ID"]
                    pieza["grosor"] = gabinete_seleccionado["Espesor"]
                
                # Agregar a la lista
                self.piezas.extend(piezas_nuevas)
                
                # Actualizar UI
                self.actualizar_lista_gabinetes()
                self.actualizar_lista_piezas()
                self.actualizar_visualizacion(gabinete_seleccionado)
                self.actualizar_detalles(gabinete_seleccionado, piezas_nuevas)
                self.actualizar_resumen_materiales()
                self.autoguardar_datos()
                
                # Cerrar ventana
                ventana_edicion.destroy()
                
                messagebox.showinfo("Éxito", f"Gabinete {id_gabinete} actualizado correctamente")
            except ValueError as e:
                messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")
        
        # Botones de acción
        frame_botones = ttk.Frame(ventana_edicion)
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(frame_botones, text="Guardar", command=guardar_cambios).pack(side=tk.RIGHT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana_edicion.destroy).pack(side=tk.RIGHT, padx=5)

    def mostrar_menu_gabinetes(self, event):
        """Muestra el menú contextual para gabinetes"""
        # Verificar si hay algún elemento seleccionado
        seleccion = self.tree_gabinetes.identify_row(event.y)
        if seleccion:
            # Seleccionar el elemento
            self.tree_gabinetes.selection_set(seleccion)
            # Mostrar el menú en la posición del clic
            self.menu_gabinetes.post(event.x_root, event.y_root)

    def limpiar_datos(self):
        """Limpia todos los datos de gabinetes y piezas"""
        # Confirmar acción
        confirmacion = messagebox.askyesno("Confirmar", "¿Está seguro de limpiar todos los datos?")
        if not confirmacion:
            return
        
        # Limpiar listas
        self.gabinetes = []
        self.piezas = []
        
        # Actualizar UI
        self.actualizar_lista_gabinetes()
        self.actualizar_lista_piezas()
        self.actualizar_resumen_materiales()
        
        # Limpiar visualización
        self.ax.clear()
        self.ax.set_title("Vista Previa 2D")
        self.ax.set_xlabel("Ancho (cm)")
        self.ax.set_ylabel("Alto (cm)")
        self.ax.grid(True)
        self.canvas.draw()
        
        # Limpiar texto de detalles
        self.texto_detalles.delete(1.0, tk.END)
        
        messagebox.showinfo("Éxito", "Datos limpiados correctamente")

    def setup_frame_editar_gabinete(self):
        """Configura el frame para editar el gabinete seleccionado"""
        # Campos de entrada para editar el gabinete
        ttk.Label(self.frame_editar_gabinete, text="Alto (in):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_alto = ttk.Entry(self.frame_editar_gabinete, width=10)
        self.entry_editar_alto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_gabinete, text="Ancho (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_ancho = ttk.Entry(self.frame_editar_gabinete, width=10)
        self.entry_editar_ancho.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_gabinete, text="Profundidad (in):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_profundidad = ttk.Entry(self.frame_editar_gabinete, width=10)
        self.entry_editar_profundidad.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_gabinete, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_cantidad = ttk.Entry(self.frame_editar_gabinete, width=10)
        self.entry_editar_cantidad.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_gabinete, text="Grosor Material (in):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_grosor = ttk.Entry(self.frame_editar_gabinete, width=10)
        self.entry_editar_grosor.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para opciones de gavetas (inicialmente oculto)
        self.frame_opciones_gavetas_editar = ttk.LabelFrame(self.frame_editar_gabinete, text="Opciones de Gavetas")
        self.frame_opciones_gavetas_editar.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        self.frame_opciones_gavetas_editar.grid_remove()  # Inicialmente oculto

        # Combobox para seleccionar el estilo de slider
        ttk.Label(self.frame_opciones_gavetas_editar, text="Estilo de Slider:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_slider_editar = ttk.Combobox(self.frame_opciones_gavetas_editar, values=["Undermount", "Sidemount"], width=10)
        self.combo_slider_editar.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_opciones_gavetas_editar, text="Número de Gavetas:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_num_gavetas = ttk.Spinbox(self.frame_opciones_gavetas_editar, from_=1, to=4, width=5)
        self.entry_editar_num_gavetas.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_num_gavetas.set(1)
        self.entry_editar_num_gavetas.bind("<<Increment>>", self.actualizar_campos_gavetas_editar)
        self.entry_editar_num_gavetas.bind("<<Decrement>>", self.actualizar_campos_gavetas_editar)
        
        # Campo de entrada para la altura de la gaveta (inicialmente oculto)
        self.frame_altura_gaveta = ttk.LabelFrame(self.frame_editar_gabinete, text="Opciones de Gavetas")
        self.frame_altura_gaveta.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        self.frame_altura_gaveta.grid_remove()  # Ocultar por defecto
        
        # Combobox para seleccionar el estilo de slider
        ttk.Label(self.frame_altura_gaveta, text="Estilo de Slider:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_slider_editar1 = ttk.Combobox(self.frame_altura_gaveta, values=["Undermount", "Sidemount"], width=10)
        self.combo_slider_editar1.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_altura_gaveta, text="Altura Gaveta (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_altura_gaveta = ttk.Entry(self.frame_altura_gaveta, width=10)
        self.entry_editar_altura_gaveta.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Contenedor para campos de altura de gavetas
        self.frame_alturas_gavetas_editar = ttk.Frame(self.frame_opciones_gavetas_editar)
        self.frame_alturas_gavetas_editar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        # Botón para guardar cambios
        self.btn_guardar_cambios = ttk.Button(self.frame_editar_gabinete, text="Guardar Cambios", command=self.guardar_cambios_gabinete)
        self.btn_guardar_cambios.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

    def guardar_cambios_gabinete(self):
        """Guarda los cambios realizados en el gabinete seleccionado."""
        seleccion = self.tree_gabinetes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay gabinete seleccionado")
            return

        # Obtener el ID del gabinete seleccionado
        item = self.tree_gabinetes.item(seleccion[0])
        id_gabinete = item["values"][0]

        # Buscar el gabinete en la lista
        gabinete_seleccionado = None
        for gabinete in self.gabinetes:
            if gabinete["ID"] == id_gabinete:
                gabinete_seleccionado = gabinete
                break

        if not gabinete_seleccionado:
            messagebox.showerror("Error", "No se encontró el gabinete")
            return

        try:
            # Actualizar datos del gabinete
            gabinete_seleccionado["Alto"] = float(self.entry_editar_alto.get())
            gabinete_seleccionado["Ancho"] = float(self.entry_editar_ancho.get())
            gabinete_seleccionado["Profundidad"] = float(self.entry_editar_profundidad.get())
            gabinete_seleccionado["Cantidad"] = int(self.entry_editar_cantidad.get())
            gabinete_seleccionado["Espesor"] = float(self.entry_editar_grosor.get())
            
            # Actualizar el estilo de slider
            gabinete_seleccionado["Slider"] = self.combo_slider_editar.get()
            gabinete_seleccionado["Slider"] = self.combo_slider_editar1.get()

            # Si es un gabinete "Base_normal", actualizar la altura de la gaveta
            if gabinete_seleccionado["Estilo"] == "Base_normal":
                altura_gaveta = float(self.entry_editar_altura_gaveta.get())
                gabinete_seleccionado["altura_gaveta"] = altura_gaveta

            # Si es un gabinete con gavetas (Base_Drawer), actualizar el número de gavetas y sus alturas
            if gabinete_seleccionado["Estilo"] == "Base_Drawer":
                num_gavetas = int(self.entry_editar_num_gavetas.get())
                gabinete_seleccionado["num_gavetas"] = num_gavetas

                # Actualizar las alturas de las gavetas
                for i, entry in enumerate(self.entries_altura_gavetas_editar):
                    if entry.get():
                        gabinete_seleccionado[f"high_drawer_{i}"] = float(entry.get())

            # Recalcular piezas
            # Eliminar piezas actuales
            self.piezas = [p for p in self.piezas if p.get("gabinete_id") != id_gabinete]

            # Calcular nuevas piezas
            if gabinete_seleccionado["Estilo"] == "Base_normal":
                piezas_nuevas = self.calcular_piezas_base_normal(gabinete_seleccionado)
            elif gabinete_seleccionado["Estilo"] == "Base_Drawer":
                piezas_nuevas = self.calcular_piezas_base_drawer(gabinete_seleccionado)
            elif gabinete_seleccionado["Estilo"] == "Wall_cabinet":
                piezas_nuevas = self.calcular_piezas_wall_cabinet(gabinete_seleccionado)
            else:
                piezas_nuevas = []  # Estilo no reconocido

            # Añadir relación con el gabinete
            for pieza in piezas_nuevas:
                pieza["gabinete_id"] = gabinete_seleccionado["ID"]
                pieza["grosor"] = gabinete_seleccionado["Espesor"]

            # Agregar a la lista
            self.piezas.extend(piezas_nuevas)

            # Actualizar UI
            self.actualizar_lista_gabinetes()
            self.actualizar_lista_piezas()
            self.actualizar_visualizacion(gabinete_seleccionado)
            self.actualizar_detalles(gabinete_seleccionado, piezas_nuevas)
            self.actualizar_resumen_materiales()
            self.autoguardar_datos()

            messagebox.showinfo("Éxito", f"Gabinete {id_gabinete} actualizado correctamente")
        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")

    def setup_frame_editar_pieza(self):
        """Configura el frame para editar la pieza seleccionada"""
        # Campos de entrada para editar la pieza
        ttk.Label(self.frame_editar_pieza, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_nombre_pieza = ttk.Entry(self.frame_editar_pieza, width=15)
        self.entry_editar_nombre_pieza.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_pieza, text="Ancho (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_ancho_pieza = ttk.Entry(self.frame_editar_pieza, width=10)
        self.entry_editar_ancho_pieza.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_pieza, text="Alto (in):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_alto_pieza = ttk.Entry(self.frame_editar_pieza, width=10)
        self.entry_editar_alto_pieza.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_pieza, text="Grosor (in):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_grosor_pieza = ttk.Entry(self.frame_editar_pieza, width=10)
        self.entry_editar_grosor_pieza.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Combobox para seleccionar el tipo de material
        ttk.Label(self.frame_editar_pieza, text="Material:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_material_pieza = ttk.Combobox(self.frame_editar_pieza, values=[
            "Plywood 3/4", "Plywood 5/8", "Plywood 1/2", "Plywood 3/8", "Plywood 1/4", "Medex 3/4", "Medex 1/4"
        ], width=15)
        self.combo_material_pieza.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        # Botón para guardar cambios en la pieza
        self.btn_guardar_cambios_pieza = ttk.Button(self.frame_editar_pieza, text="Guardar Cambios", command=self.guardar_cambios_pieza)
        self.btn_guardar_cambios_pieza.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def guardar_cambios_pieza(self):
        """Guarda los cambios realizados en la pieza seleccionada"""
        seleccion = self.tree_piezas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay pieza seleccionada")
            return

        # Obtener los valores de la pieza seleccionada
        item = self.tree_piezas.item(seleccion[0])
        valores = item["values"]
        id_gabinete = valores[0]  # ID del gabinete
        nombre_pieza = valores[1]  # Nombre de la pieza

        # Buscar la pieza en la lista
        pieza_seleccionada = None
        for pieza in self.piezas:
            if pieza.get("gabinete_id") == id_gabinete and pieza["nombre"] == nombre_pieza:
                pieza_seleccionada = pieza
                break

        if not pieza_seleccionada:
            messagebox.showerror("Error", "No se encontró la pieza")
            return

        try:
            # Actualizar datos de la pieza
            pieza_seleccionada["nombre"] = self.entry_editar_nombre_pieza.get()
            pieza_seleccionada["ancho"] = float(self.entry_editar_ancho_pieza.get())
            pieza_seleccionada["alto"] = float(self.entry_editar_alto_pieza.get())
            pieza_seleccionada["grosor"] = float(self.entry_editar_grosor_pieza.get())
            pieza_seleccionada["material"] = self.combo_material_pieza.get()

            # Actualizar UI
            self.actualizar_lista_piezas(id_gabinete)  # Actualizar solo las piezas del gabinete seleccionado
            self.actualizar_vista_frontal_pieza(pieza_seleccionada)
            self.actualizar_vista_lateral_pieza(pieza_seleccionada)
            self.autoguardar_datos()
            messagebox.showinfo("Éxito", f"Pieza {nombre_pieza} actualizada correctamente")
        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")
            
    def actualizar_campos_edicion(self, gabinete):
        """Actualiza los campos de edición con los datos del gabinete seleccionado"""
        # Limpiar campos de edición
        self.entry_editar_alto.delete(0, tk.END)
        self.entry_editar_ancho.delete(0, tk.END)
        self.entry_editar_profundidad.delete(0, tk.END)
        self.entry_editar_cantidad.delete(0, tk.END)
        self.entry_editar_grosor.delete(0, tk.END)
        self.combo_slider_editar.set("")  # Limpiar el combobox
        self.combo_slider_editar1.set("")  # Limpiar el combobox

        # Llenar campos con los datos del gabinete
        self.entry_editar_alto.insert(0, str(gabinete["Alto"]))
        self.entry_editar_ancho.insert(0, str(gabinete["Ancho"]))
        self.entry_editar_profundidad.insert(0, str(gabinete["Profundidad"]))
        self.entry_editar_cantidad.insert(0, str(gabinete["Cantidad"]))
        self.entry_editar_grosor.insert(0, str(gabinete["Espesor"]))
        self.entry_editar_altura_gaveta.delete(0, tk.END)
        self.combo_slider_editar.set(gabinete.get("Slider", "Undermount"))  # Cargar el valor del slider
        self.combo_slider_editar1.set(gabinete.get("Slider", "Undermount"))  # Cargar el valor del slider

        # Si es un gabinete con gavetas, actualizar el número y mostrar el frame de opciones
        if gabinete["Estilo"] == "Base_Drawer":
            # Mostrar frame de opciones de gavetas
            self.frame_opciones_gavetas_editar.grid()
            
            # Establecer número de gavetas
            num_gavetas = gabinete.get("num_gavetas", 1)
            self.entry_editar_num_gavetas.delete(0, tk.END)
            self.entry_editar_num_gavetas.insert(0, str(num_gavetas))
            
            # Actualizar campos de altura de gavetas con las alturas existentes
            # Usar self.frame_opciones_gavetas_editar.after para asegurar que el valor del spinbox se haya actualizado
            self.frame_opciones_gavetas_editar.after(10, 
                lambda: self.actualizar_campos_gavetas_editar1(num_gavetas=num_gavetas, gabinete=gabinete))
        else:
            # Ocultar frame de opciones de gavetas
            self.frame_opciones_gavetas_editar.grid_remove()
            
        # Si es un gabinete "Base_normal", mostrar el campo de altura de la gaveta
        if gabinete["Estilo"] == "Base_normal":
            self.frame_altura_gaveta.grid()  # Mostrar el frame de altura de la gaveta
            self.entry_editar_altura_gaveta.insert(0, str(gabinete.get("altura_gaveta", 6)))  # Valor predeterminado: 6 cm
        else:
            self.frame_altura_gaveta.grid_remove()  # Ocultar el frame de altura de la gaveta

    def reiniciar_valores_modificados(self):
        """Reinicia la lista de valores modificados y oculta los check marks"""
        self.valores_modificados = [False] * len(self.entries_altura_gavetas)
        for label in self.labels_check:
            label.config(text="")  # Ocultar los check marks
        self.actualizar_campos_gavetas()  # Recalcular los campos

    def reiniciar_valores_modificados_editar(self):
        """Reinicia la lista de valores modificados y oculta los check marks en la edición"""
        self.valores_modificados_editar = [False] * len(self.entries_altura_gavetas_editar)
        for label in self.labels_check_editar:
            label.config(text="")  # Ocultar los check marks
        self.actualizar_campos_gavetas_editar1()  # Recalcular los campos
        
    def cargar_proyecto_anterior(self):
        """Pregunta al usuario si desea cargar el proyecto anterior y carga los datos si es necesario"""
        if os.path.exists(self.archivo_temp):  # Verificar si el archivo temporal existe
            respuesta = messagebox.askyesno(
                "Recuperar proyecto anterior",
                "Se encontró un proyecto guardado temporalmente. ¿Deseas recuperarlo?"
            )

            if respuesta:  # Si el usuario acepta
                try:
                    with open(self.archivo_temp, "r") as archivo:
                        datos = json.load(archivo)
                    
                    # Cargar los datos del archivo temporal
                    self.gabinetes = datos.get("gabinetes", [])
                    self.piezas = datos.get("piezas", [])

                    # Actualizar la interfaz con los datos cargados
                    self.actualizar_lista_gabinetes()
                    self.actualizar_lista_piezas()
                    self.actualizar_resumen_materiales()

                    messagebox.showinfo("Éxito", "Proyecto anterior cargado correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar el proyecto anterior: {str(e)}")
        else:
            print("No se encontró un proyecto anterior para cargar.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionGabinetes(root)
    root.mainloop()