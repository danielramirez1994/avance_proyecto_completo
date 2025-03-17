import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
import shutil

class MaterialManager:
    def __init__(self, parent):
        self.parent = parent  # El frame contenedor
        self.archivo_temp = "materiales.json"  # Archivo para guardar los materiales
        self.carpeta_imagenes = "imagenes_materiales"  # Carpeta para almacenar las imágenes
        self.materiales = []  # Lista para almacenar los materiales
        self.crear_carpeta_imagenes()  # Crear carpeta para imágenes si no existe
        self.setup_ui()  # Configurar la interfaz de usuario
        self.cargar_materiales()  # Cargar materiales después de configurar la interfaz

    def crear_carpeta_imagenes(self):
        """Crea la carpeta para almacenar las imágenes si no existe."""
        if not os.path.exists(self.carpeta_imagenes):
            os.makedirs(self.carpeta_imagenes)

    def cargar_materiales(self):
        """Carga los materiales desde el archivo JSON si existe."""
        if os.path.exists(self.archivo_temp):
            try:
                with open(self.archivo_temp, "r") as archivo:
                    datos = json.load(archivo)
                    self.materiales = datos.get("materiales", [])
                    print(f"Materiales cargados desde {self.archivo_temp}")
                    # Actualizar la tabla Treeview con los materiales cargados
                    self.actualizar_lista_materiales()  # Llamada añadida aquí
            except Exception as e:
                print(f"Error al cargar los materiales: {str(e)}")
        else:
            print(f"No se encontró el archivo {self.archivo_temp}. Se creará uno nuevo al guardar.")

    def setup_ui(self):
        """Configura la interfaz de usuario dentro del frame contenedor"""
        # Crear paneles principales
        self.paneles_ingreso = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
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
        """Configura el frame izquierdo con campos de entrada y lista de materiales"""
        # Frame para dimensiones y tipo de material
        self.frame_dimensiones = ttk.LabelFrame(self.frame_izquierdo, text="Dimensiones y Tipo de Material")
        self.frame_dimensiones.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Campos de entrada
        ttk.Label(self.frame_dimensiones, text="Alto (in):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_alto = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_alto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_dimensiones, text="Ancho (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_ancho = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_ancho.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_dimensiones, text="Grosor (in):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_grosor = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_grosor.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Combobox para tipo de material
        ttk.Label(self.frame_dimensiones, text="Tipo de Material:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_tipo_material = ttk.Combobox(self.frame_dimensiones, values=["Madera", "MDF", "Melamina", "Acero"])
        self.combo_tipo_material.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.combo_tipo_material.current(0)

        # Checkbox para grano del material
        self.var_grano = tk.BooleanVar()
        self.check_grano = ttk.Checkbutton(self.frame_dimensiones, text="Grano", variable=self.var_grano)
        self.check_grano.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        # Campo de entrada para precio
        ttk.Label(self.frame_dimensiones, text="Precio ($):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_precio = ttk.Entry(self.frame_dimensiones, width=10)
        self.entry_precio.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # Botón para agregar material
        self.btn_agregar = ttk.Button(self.frame_dimensiones, text="Agregar Material", command=self.agregar_material)
        self.btn_agregar.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # Frame para lista de materiales
        self.frame_lista_materiales = ttk.LabelFrame(self.frame_izquierdo, text="Lista de Materiales")
        self.frame_lista_materiales.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tabla Treeview para materiales (ajustar el ancho de las columnas)
        self.tree_materiales = ttk.Treeview(self.frame_lista_materiales, columns=("ID", "Tipo", "Alto", "Ancho", "Grosor", "Grano", "Precio"), show="headings")
        self.tree_materiales.heading("ID", text="ID")
        self.tree_materiales.heading("Tipo", text="Tipo")
        self.tree_materiales.heading("Alto", text="Alto")
        self.tree_materiales.heading("Ancho", text="Ancho")
        self.tree_materiales.heading("Grosor", text="Grosor")
        self.tree_materiales.heading("Grano", text="Grano")
        self.tree_materiales.heading("Precio", text="Precio")

        # Ajustar el ancho de las columnas
        self.tree_materiales.column("ID", width=30)
        self.tree_materiales.column("Tipo", width=60)
        self.tree_materiales.column("Alto", width=50)
        self.tree_materiales.column("Ancho", width=50)
        self.tree_materiales.column("Grosor", width=50)
        self.tree_materiales.column("Grano", width=50)
        self.tree_materiales.column("Precio", width=50)

        # Agregar scrollbar
        scrollbar_materiales = ttk.Scrollbar(self.frame_lista_materiales, orient=tk.VERTICAL, command=self.tree_materiales.yview)
        self.tree_materiales.configure(yscroll=scrollbar_materiales.set)
        scrollbar_materiales.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_materiales.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botón para eliminar material seleccionado
        self.btn_eliminar_material = ttk.Button(self.frame_lista_materiales, text="Eliminar Material", command=self.eliminar_material)
        self.btn_eliminar_material.pack(pady=5)

        # Vincular la selección de un material en el Treeview
        self.tree_materiales.bind("<<TreeviewSelect>>", self.seleccionar_material)
        
    def eliminar_material(self):
        """Elimina el material seleccionado de la lista"""
        seleccion = self.tree_materiales.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay material seleccionado para eliminar")
            return

        # Confirmar eliminación
        confirmacion = messagebox.askyesno("Confirmar eliminación", 
                                        "¿Estás seguro de que deseas eliminar este material?")
        if not confirmacion:
            return

        item = self.tree_materiales.item(seleccion[0])
        id_material = str(item["values"][0])  # Convertir explícitamente a string

        # Encontrar el material en la lista
        indice_material = None
        for i, material in enumerate(self.materiales):
            if material["ID"] == id_material:
                indice_material = i
                
                # Eliminar la imagen asociada si existe
                if material["Imagen"] and os.path.exists(material["Imagen"]):
                    try:
                        os.remove(material["Imagen"])
                    except Exception as e:
                        print(f"Error al eliminar la imagen: {str(e)}")
                
                break

        if indice_material is not None:
            # Eliminar material de la lista
            del self.materiales[indice_material]
            # Actualizar la tabla
            self.actualizar_lista_materiales()
            # Limpiar el canvas de imagen
            self.canvas_imagen.delete("all")
            # Guardar cambios
            self.guardar_materiales()
            messagebox.showinfo("Éxito", "Material eliminado correctamente")
        else:
            messagebox.showerror("Error", "No se pudo eliminar el material")

    def setup_frame_central(self):
        """Configura el frame central para la visualización de imágenes"""
        self.frame_visualizacion = ttk.LabelFrame(self.frame_central, text="Visualización de Material")
        self.frame_visualizacion.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas para mostrar la imagen del material
        self.canvas_imagen = tk.Canvas(self.frame_visualizacion, bg="white")
        self.canvas_imagen.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_frame_derecho(self):
        """Configura el frame derecho para editar los datos del material seleccionado"""
        self.frame_editar_material = ttk.LabelFrame(self.frame_derecho, text="Editar Material")
        self.frame_editar_material.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Campos de entrada para editar el material
        ttk.Label(self.frame_editar_material, text="Alto (in):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_alto = ttk.Entry(self.frame_editar_material, width=10)
        self.entry_editar_alto.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_material, text="Ancho (in):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_ancho = ttk.Entry(self.frame_editar_material, width=10)
        self.entry_editar_ancho.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_material, text="Grosor (in):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_grosor = ttk.Entry(self.frame_editar_material, width=10)
        self.entry_editar_grosor.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_material, text="Tipo de Material:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_editar_tipo_material = ttk.Combobox(self.frame_editar_material, values=["Madera", "MDF", "Melamina", "Acero"])
        self.combo_editar_tipo_material.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.frame_editar_material, text="Precio ($):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_editar_precio = ttk.Entry(self.frame_editar_material, width=10)
        self.entry_editar_precio.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        # Checkbox para grano del material
        self.var_editar_grano = tk.BooleanVar()
        self.check_editar_grano = ttk.Checkbutton(self.frame_editar_material, text="Grano", variable=self.var_editar_grano)
        self.check_editar_grano.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        # Botón para guardar cambios
        self.btn_guardar_cambios = ttk.Button(self.frame_editar_material, text="Guardar Cambios", command=self.guardar_cambios_material)
        self.btn_guardar_cambios.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # Botón para cargar imagen en el frame derecho
        self.btn_cargar_imagen_derecho = ttk.Button(self.frame_editar_material, text="Cargar Imagen", command=self.cargar_imagen_derecho)
        self.btn_cargar_imagen_derecho.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def obtener_siguiente_id(self):
        """Obtiene el siguiente ID disponible basado en el ID más alto existente"""
        max_id = 0
        for material in self.materiales:
            try:
                id_num = int(material["ID"])
                if id_num > max_id:
                    max_id = id_num
            except ValueError:
                # Si encuentra un ID que no es número, lo ignora
                pass
        return str(max_id + 1)

    def agregar_material(self):
        """Agrega un nuevo material a la lista"""
        try:
            alto = float(self.entry_alto.get())
            ancho = float(self.entry_ancho.get())
            grosor = float(self.entry_grosor.get())
            tipo_material = self.combo_tipo_material.get()
            grano = self.var_grano.get()
            precio = float(self.entry_precio.get())

            # Usar función para obtener el siguiente ID disponible
            siguiente_id = self.obtener_siguiente_id()

            material = {
                "ID": siguiente_id,
                "Tipo": tipo_material,
                "Alto": alto,
                "Ancho": ancho,
                "Grosor": grosor,
                "Grano": grano,
                "Precio": precio,
                "Imagen": None  # Aquí se almacenará la ruta de la imagen
            }

            self.materiales.append(material)
            self.actualizar_lista_materiales()
            self.limpiar_campos_ingreso()
            self.guardar_materiales()
            messagebox.showinfo("Éxito", "Material agregado correctamente")
        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")

    def actualizar_lista_materiales(self):
        """Actualiza la lista de materiales en el Treeview"""
        # Limpiar la tabla Treeview
        for item in self.tree_materiales.get_children():
            self.tree_materiales.delete(item)

        # Insertar los materiales en la tabla Treeview
        for material in self.materiales:
            self.tree_materiales.insert("", "end", values=(
                material["ID"],
                material["Tipo"],
                material["Alto"],
                material["Ancho"],
                material["Grosor"],
                "Sí" if material["Grano"] else "No",
                f"${material['Precio']:.2f}"
            ))

    def seleccionar_material(self, event):
        """Maneja la selección de un material en el Treeview"""
        seleccion = self.tree_materiales.selection()
        if seleccion:
            # Obtener los valores del material seleccionado
            item = self.tree_materiales.item(seleccion[0])
            valores = item["values"]
            id_material = str(valores[0])  # Convertir explícitamente a string
            
            # Buscar el material en la lista
            material_seleccionado = None
            for material in self.materiales:
                if material["ID"] == id_material:
                    material_seleccionado = material
                    break

            if material_seleccionado:
                # Actualizar los campos de entrada del panel derecho
                self.actualizar_campos_edicion(material_seleccionado)
                # Mostrar la imagen del material seleccionado
                self.mostrar_imagen_material(material_seleccionado)

    def actualizar_campos_edicion(self, material):
        """Actualiza los campos de entrada del panel derecho con los datos del material seleccionado"""
        # Limpiar campos de entrada
        self.entry_editar_alto.delete(0, tk.END)
        self.entry_editar_ancho.delete(0, tk.END)
        self.entry_editar_grosor.delete(0, tk.END)
        self.combo_editar_tipo_material.set("")
        self.var_editar_grano.set(False)
        self.entry_editar_precio.delete(0, tk.END)

        # Llenar campos con los datos del material seleccionado
        self.entry_editar_alto.insert(0, str(material["Alto"]))
        self.entry_editar_ancho.insert(0, str(material["Ancho"]))
        self.entry_editar_grosor.insert(0, str(material["Grosor"]))
        self.combo_editar_tipo_material.set(material["Tipo"])
        self.var_editar_grano.set(material["Grano"])
        self.entry_editar_precio.insert(0, str(material["Precio"]))

    def guardar_cambios_material(self):
        """Guarda los cambios realizados en el material seleccionado"""
        seleccion = self.tree_materiales.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay material seleccionado")
            return

        item = self.tree_materiales.item(seleccion[0])
        id_material = str(item["values"][0])  # Convertir explícitamente a string

        # Buscar el índice del material en la lista para actualizarlo correctamente
        indice_material = None
        for i, material in enumerate(self.materiales):
            if material["ID"] == id_material:
                indice_material = i
                break

        if indice_material is not None:
            try:
                # Crear un nuevo diccionario con los valores actualizados
                material_actualizado = self.materiales[indice_material].copy()  # Copia el material original
                material_actualizado["Alto"] = float(self.entry_editar_alto.get())
                material_actualizado["Ancho"] = float(self.entry_editar_ancho.get())
                material_actualizado["Grosor"] = float(self.entry_editar_grosor.get())
                material_actualizado["Tipo"] = self.combo_editar_tipo_material.get()
                material_actualizado["Grano"] = self.var_editar_grano.get()
                material_actualizado["Precio"] = float(self.entry_editar_precio.get())
                
                # Actualizar el material en la lista
                self.materiales[indice_material] = material_actualizado
                
                # Actualizar la lista en la interfaz y guardar
                self.actualizar_lista_materiales()
                self.guardar_materiales()
                messagebox.showinfo("Éxito", "Material actualizado correctamente")
            except ValueError as e:
                messagebox.showerror("Error de Datos", f"Datos inválidos: {str(e)}")
        else:
            messagebox.showerror("Error", "No se encontró el material para actualizar")

    def cargar_imagen_derecho(self):
        """Carga una imagen para el material seleccionado en el panel derecho"""
        seleccion = self.tree_materiales.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "No hay material seleccionado")
            return

        item = self.tree_materiales.item(seleccion[0])
        id_material = str(item["values"][0])  # Convertir explícitamente a string

        # Buscar el índice del material en la lista
        indice_material = None
        for i, material in enumerate(self.materiales):
            if material["ID"] == id_material:
                indice_material = i
                break

        if indice_material is not None:
            ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
            if ruta_imagen:
                ruta_guardada = self.guardar_imagen_material(ruta_imagen, id_material)
                # Actualizar la ruta de la imagen en el material
                self.materiales[indice_material]["Imagen"] = ruta_guardada
                # Mostrar la imagen
                self.mostrar_imagen_material(self.materiales[indice_material])
                # Guardar los cambios
                self.guardar_materiales()
        else:
            messagebox.showerror("Error", "No se encontró el material para actualizar")

    def guardar_imagen_material(self, ruta_imagen, id_material):
        """Guarda la imagen en la carpeta de imágenes y devuelve la ruta relativa"""
        nombre_archivo = f"material_{id_material}.{ruta_imagen.split('.')[-1]}"
        ruta_destino = os.path.join(self.carpeta_imagenes, nombre_archivo)
        shutil.copy(ruta_imagen, ruta_destino)
        return ruta_destino

    def mostrar_imagen_material(self, material):
        """Muestra la imagen del material seleccionado en el canvas"""
        if material["Imagen"]:
            imagen = Image.open(material["Imagen"])
            # Usar Image.Resampling.LANCZOS o Image.LANCZOS en lugar de Image.ANTIALIAS
            imagen = imagen.resize((300, 300), Image.Resampling.LANCZOS)  # Corregido aquí
            self.imagen_tk = ImageTk.PhotoImage(imagen)
            self.canvas_imagen.create_image(0, 0, anchor=tk.NW, image=self.imagen_tk)
        else:
            self.canvas_imagen.delete("all")

    def limpiar_campos_ingreso(self):
        """Limpia los campos de entrada"""
        self.entry_alto.delete(0, tk.END)
        self.entry_ancho.delete(0, tk.END)
        self.entry_grosor.delete(0, tk.END)
        self.combo_tipo_material.set("Madera")
        self.var_grano.set(False)
        self.entry_precio.delete(0, tk.END)

    def guardar_materiales(self):
        """Guarda los materiales en el archivo JSON"""
        datos = {"materiales": self.materiales}
        try:
            with open(self.archivo_temp, "w") as archivo:
                json.dump(datos, archivo, indent=4)
            print(f"Materiales guardados en {self.archivo_temp}")
        except Exception as e:
            print(f"Error al guardar los materiales: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MaterialManager(root)
    root.mainloop()