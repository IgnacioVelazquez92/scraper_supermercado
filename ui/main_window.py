import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

from scrapers.libre_scraper import buscar_vtex_httpx
from scrapers.carrefour_scraper import buscar_carrefour_httpx
from scrapers.vea_scraper import buscar_vea_httpx
from scrapers.jumbo_scraper import buscar_jumbo_httpx

from utils import renovar_cookies_carrefour, renovar_cookies_vea, renovar_cookies_jumbo, procesar_lote


class SupermercadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Precios Supermercados")
        self.root.geometry("1000x600")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_programa)

        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Pestaña de búsqueda por nombre
        self.tab_nombre = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_nombre, text="🔎 Buscar por Nombre")
        self.init_tab_nombre()

        # Pestaña para búsqueda por lote (por ahora placeholder)
        self.tab_lote = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_lote, text="📦 Buscar por Lote")
        tk.Button(self.tab_lote, text="📥 Subir Excel y Procesar",
                  command=self.procesar_lote).pack(pady=20)

    def procesar_lote(self):
        procesar_lote.main()

    def init_tab_nombre(self):
        self.entry = tk.Entry(self.tab_nombre, font=("Arial", 14), width=50)
        self.entry.pack(pady=10)

        self.coincidencia_exacta = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.tab_nombre, text="Coincidencia exacta", variable=self.coincidencia_exacta, font=("Arial", 11)
        ).pack()

        tk.Button(
            self.tab_nombre, text="Buscar", command=self.buscar, font=("Arial", 12)
        ).pack()

        self.tree = ttk.Treeview(
            self.tab_nombre,
            columns=("Supermercado", "Nombre", "EAN",
                     "Precio", "Disponible", "URL"),
            show="headings"
        )
        for col in ("Supermercado", "Nombre", "EAN", "Precio", "Disponible", "URL"):
            self.tree.heading(col, text=col)
            if col == "URL":
                self.tree.column(col, width=80, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=180, anchor=tk.W)

        # Habilitar ordenamiento por EAN
        self.tree.heading("EAN", text="EAN",
                          command=lambda: self.sort_column("EAN", False))

        self.tree.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree.bind("<Double-1>", self.abrir_url)

        # Habilitar copiar con Ctrl+C
        self.tree.bind("<Control-c>", self.copiar_seleccion)

        self.cookie_frame = tk.Frame(self.tab_nombre)
        self.cookie_frame.pack(pady=10)
        tk.Button(self.cookie_frame, text="♻️ Carrefour",
                  command=self.renovar_carrefour).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Vea",
                  command=self.renovar_vea).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Jumbo",
                  command=self.renovar_jumbo).pack(side=tk.LEFT, padx=5)

    def abrir_url(self, event):
        item = self.tree.item(self.tree.selection()[0])
        url = item['values'][5]
        webbrowser.open(url)

    def buscar(self):
        keywords = self.entry.get().strip()
        if not keywords:
            messagebox.showwarning("Atención", "Ingrese un producto a buscar.")
            return

        exacta = self.coincidencia_exacta.get()
        self.tree.delete(*self.tree.get_children())

        # Scrapers VTEX (comodín e hiperlibertad)
        for dominio in ["www.comodinencasa.com.ar", "www.hiperlibertad.com.ar"]:
            try:
                resultados = buscar_vtex_httpx(keywords, dominio, exacta)
                if not resultados:
                    # Usamos el nombre amigable del super
                    nombre_super = "Comodín" if dominio == "www.comodinencasa.com.ar" else "Hiperlibertad"
                    self.tree.insert("", tk.END, values=(
                        nombre_super, "Sin resultados", "-", "-", "-", "-"))
                else:
                    for r in resultados:
                        self.tree.insert("", tk.END, values=(
                            # Aquí usamos el nombre devuelto por el scraper
                            r.get('supermercado', dominio),
                            r['nombre'], r['ean'], r['precio'],
                            "Sí" if r.get('isAvailable', False) else "No",
                            r['url']
                        ))
            except Exception as e:
                print(f"Error en {dominio}: {e}")

        # Scrapers específicos
        for nombre, funcion in [("Carrefour", buscar_carrefour_httpx), ("Vea", buscar_vea_httpx), ("Jumbo", buscar_jumbo_httpx)]:
            try:
                resultados = funcion(keywords, exacta)
                if not resultados:
                    self.tree.insert("", tk.END, values=(
                        nombre, "Sin resultados", "-", "-", "-", "-"))
                else:
                    for r in resultados:
                        self.tree.insert("", tk.END, values=(
                            nombre, r['nombre'], r['ean'], r['precio'],
                            "Sí" if r.get('isAvailable', False) else "No",
                            r['url']
                        ))
            except Exception as e:
                print(f"{nombre} falló:", e)

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]))
        except ValueError:
            l.sort(key=lambda t: t[0])

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(
            col, command=lambda: self.sort_column(col, not reverse))

    def copiar_seleccion(self, event):
        item = self.tree.focus()
        if item:
            valores = self.tree.item(item, 'values')
            texto = "\t".join(valores)
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            print(f"📋 Copiado: {texto}")

    def renovar_carrefour(self):
        renovar_cookies_carrefour.renovar_cookies_carrefour()
        messagebox.showinfo("Listo", "Cookies de Carrefour renovadas")

    def renovar_vea(self):
        renovar_cookies_vea.renovar_cookies_vea()
        messagebox.showinfo("Listo", "Cookies de Vea renovadas")

    def renovar_jumbo(self):
        renovar_cookies_jumbo.renovar_cookies_jumbo()
        messagebox.showinfo("Listo", "Cookies de Jumbo renovadas")

    def cerrar_programa(self):
        self.root.destroy()
        os._exit(0)
