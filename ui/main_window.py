import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

from scrapers.libre_scraper import buscar_vtex_httpx
from scrapers.carrefour_scraper import buscar_carrefour_httpx
from scrapers.vea_scraper import buscar_vea_httpx
from scrapers.jumbo_scraper import buscar_jumbo_httpx
from scrapers.farmacias.farmacity_scraper import buscar_farmacity_httpx
from scrapers.farmacias.fdp_scraper import buscar_fdp_httpx

from utils import renovar_cookies_carrefour, renovar_cookies_vea, renovar_cookies_jumbo, procesar_lote
from utils import renovar_cookies_farmacity, renovar_cookies_fdp, procesar_lote
from . import lote_window


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
        self.notebook.add(self.tab_nombre, text="🔎 Buscar en Supermercados")
        self.init_tab_nombre()

        # Pestaña de búsqueda por lote
        self.tab_lote = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_lote, text="📦 Buscar por Lote")
        tk.Button(self.tab_lote, text="📥 Subir Excel y Procesar",
                  command=self.procesar_lote).pack(pady=20)

        # Pestaña Farmacias
        self.tab_farmacias = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_farmacias, text="🏥 Buscar en Farmacias")
        self.init_tab_farmacias()

        # Pestaña Cálculo de Utilidades
        self.tab_utilidades = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_utilidades, text="💰 Cálculo de Utilidades")
        # Inputs
        tk.Label(self.tab_utilidades, text="Costo Final:",
                 font=("Arial", 12)).pack(pady=5)
        self.entry_costo = tk.Entry(self.tab_utilidades, font=("Arial", 12))
        self.entry_costo.pack()

        tk.Label(self.tab_utilidades, text="Precio de Venta:",
                 font=("Arial", 12)).pack(pady=5)
        self.entry_venta = tk.Entry(self.tab_utilidades, font=("Arial", 12))
        self.entry_venta.pack()

        tk.Label(self.tab_utilidades, text="% Utilidad:",
                 font=("Arial", 12)).pack(pady=5)
        self.entry_utilidad = tk.Entry(self.tab_utilidades, font=("Arial", 12))
        self.entry_utilidad.pack()

        # Check % basado en costo o venta
        self.base_costo = tk.BooleanVar(value=True)
        tk.Checkbutton(self.tab_utilidades, text="Calcular utilidad sobre COSTO (✓) o VENTA",
                       variable=self.base_costo, font=("Arial", 11)).pack(pady=5)

        # Botón Calcular
        tk.Button(self.tab_utilidades, text="Calcular",
                  command=self.calcular_utilidades, font=("Arial", 12)).pack(pady=10)

        # Resultado
        self.resultado_label = tk.Label(
            self.tab_utilidades, text="", font=("Arial", 12))
        self.resultado_label.pack(pady=10)

    def procesar_lote(self):
        lote_window.main()

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

        self.tree.heading("EAN", text="EAN",
                          command=lambda: self.sort_column("EAN", False))

        self.tree.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree.bind("<Double-1>", self.abrir_url)
        self.tree.bind("<Control-c>", self.copiar_seleccion)

        self.cookie_frame = tk.Frame(self.tab_nombre)
        self.cookie_frame.pack(pady=10)
        tk.Button(self.cookie_frame, text="♻️ Carrefour",
                  command=self.renovar_carrefour).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Vea",
                  command=self.renovar_vea).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Jumbo",
                  command=self.renovar_jumbo).pack(side=tk.LEFT, padx=5)

    def init_tab_farmacias(self):
        self.entry_farmacias = tk.Entry(
            self.tab_farmacias, font=("Arial", 14), width=50)
        self.entry_farmacias.pack(pady=10)

        self.coincidencia_exacta_farmacias = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.tab_farmacias, text="Coincidencia exacta", variable=self.coincidencia_exacta_farmacias, font=("Arial", 11)
        ).pack()

        tk.Button(
            self.tab_farmacias, text="Buscar", command=self.buscar_farmacias, font=("Arial", 12)
        ).pack()

        self.tree_farmacias = ttk.Treeview(
            self.tab_farmacias,
            columns=("Farmacia", "Nombre", "EAN",
                     "Precio", "Disponible", "URL"),
            show="headings"
        )
        for col in ("Farmacia", "Nombre", "EAN", "Precio", "Disponible", "URL"):
            self.tree_farmacias.heading(col, text=col)
            if col == "URL":
                self.tree_farmacias.column(col, width=80, anchor=tk.CENTER)
            else:
                self.tree_farmacias.column(col, width=180, anchor=tk.W)

        self.tree_farmacias.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree_farmacias.bind("<Double-1>", self.abrir_url)

        self.cookie_frame_farmacias = tk.Frame(self.tab_farmacias)
        self.cookie_frame_farmacias.pack(pady=10)
        tk.Button(self.cookie_frame_farmacias, text="♻️ Farmacity",
                  command=self.renovar_farmacity).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame_farmacias, text="♻️ FDP",
                  command=self.renovar_fdp).pack(side=tk.LEFT, padx=5)

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

    def buscar_farmacias(self):
        keywords = self.entry_farmacias.get().strip()
        if not keywords:
            messagebox.showwarning("Atención", "Ingrese un producto a buscar.")
            return

        exacta = self.coincidencia_exacta_farmacias.get()
        self.tree_farmacias.delete(*self.tree_farmacias.get_children())

        for nombre, funcion in [("Farmacity", buscar_farmacity_httpx), ("Farmacias del Pueblo", buscar_fdp_httpx)]:
            try:
                resultados = funcion(keywords, exacta)
                if not resultados:
                    self.tree_farmacias.insert("", tk.END, values=(
                        nombre, "Sin resultados", "-", "-", "-", "-"))
                else:
                    for r in resultados:
                        self.tree_farmacias.insert("", tk.END, values=(
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
            if len(valores) >= 4:
                # Solo copiar Supermercado, Nombre y Precio
                texto = f"{valores[0]} - {valores[1]} - ${valores[3]}"
            else:
                # Fallback si no tiene los campos esperados
                texto = "\t".join(valores)

            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            print(f"📋 Copiado: {texto}")

    def renovar_carrefour(self):
        try:
            renovar_cookies_carrefour.renovar_cookies_carrefour()
            messagebox.showinfo(
                "Listo", "Cookies de Carrefour renovadas correctamente.")
        except Exception as e:
            error_msg = str(e)
            chrome_version = None
            chromedriver_version = None

            if "Current browser version is" in error_msg:
                parts = error_msg.split("Current browser version is")
                chrome_version = parts[1].split("\n")[0].strip()
            if "only supports Chrome version" in error_msg:
                parts = error_msg.split("only supports Chrome version")
                chromedriver_version = parts[1].split("\n")[0].strip()

            mensaje_final = f"Error al renovar cookies de Carrefour:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la versión {chromedriver_version} o superior.\nVe a:\nchrome://settings/help"
            if not chromedriver_version:
                mensaje_final = f"Error al renovar cookies de Carrefour:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la última versión.\nVe a:\nchrome://settings/help"

            messagebox.showerror("Error", mensaje_final)
            print(f"[ERROR] Carrefour: {e}")

    def renovar_vea(self):
        try:
            renovar_cookies_vea.renovar_cookies_vea()
            messagebox.showinfo(
                "Listo", "Cookies de Vea renovadas correctamente.")
        except Exception as e:
            error_msg = str(e)
            chrome_version = None
            chromedriver_version = None

            if "Current browser version is" in error_msg:
                parts = error_msg.split("Current browser version is")
                chrome_version = parts[1].split("\n")[0].strip()
            if "only supports Chrome version" in error_msg:
                parts = error_msg.split("only supports Chrome version")
                chromedriver_version = parts[1].split("\n")[0].strip()

            mensaje_final = f"Error al renovar cookies de Vea:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la versión {chromedriver_version} o superior.\nVe a:\nchrome://settings/help"
            if not chromedriver_version:
                mensaje_final = f"Error al renovar cookies de Vea:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la última versión.\nVe a:\nchrome://settings/help"

            messagebox.showerror("Error", mensaje_final)
            print(f"[ERROR] Vea: {e}")

    def renovar_jumbo(self):
        try:
            renovar_cookies_jumbo.renovar_cookies_jumbo()
            messagebox.showinfo(
                "Listo", "Cookies de Jumbo renovadas correctamente.")
        except Exception as e:
            error_msg = str(e)
            chrome_version = None
            chromedriver_version = None

            if "Current browser version is" in error_msg:
                parts = error_msg.split("Current browser version is")
                chrome_version = parts[1].split("\n")[0].strip()
            if "only supports Chrome version" in error_msg:
                parts = error_msg.split("only supports Chrome version")
                chromedriver_version = parts[1].split("\n")[0].strip()

            mensaje_final = f"Error al renovar cookies de Jumbo:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la versión {chromedriver_version} o superior.\nVe a:\nchrome://settings/help"
            if not chromedriver_version:
                mensaje_final = f"Error al renovar cookies de Jumbo:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la última versión.\nVe a:\nchrome://settings/help"

            messagebox.showerror("Error", mensaje_final)
            print(f"[ERROR] Jumbo: {e}")

    def renovar_farmacity(self):
        try:
            renovar_cookies_farmacity.renovar_cookies_farmacity()
            messagebox.showinfo(
                "Listo", "Cookies de Farmacity renovadas correctamente.")
        except Exception as e:
            error_msg = str(e)
            chrome_version = None
            chromedriver_version = None

            if "Current browser version is" in error_msg:
                parts = error_msg.split("Current browser version is")
                chrome_version = parts[1].split("\n")[0].strip()
            if "only supports Chrome version" in error_msg:
                parts = error_msg.split("only supports Chrome version")
                chromedriver_version = parts[1].split("\n")[0].strip()

            mensaje_final = f"Error al renovar cookies de Farmacity:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la versión {chromedriver_version} o superior.\nVe a:\nchrome://settings/help"
            if not chromedriver_version:
                mensaje_final = f"Error al renovar cookies de Farmacity:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la última versión.\nVe a:\nchrome://settings/help"

            messagebox.showerror("Error", mensaje_final)
            print(f"[ERROR] Farmacity: {e}")

    def renovar_fdp(self):
        try:
            renovar_cookies_fdp.renovar_cookies_fdp()
            messagebox.showinfo(
                "Listo", "Cookies de Farmacias del Pueblo renovadas correctamente.")
        except Exception as e:
            error_msg = str(e)
            chrome_version = None
            chromedriver_version = None

            if "Current browser version is" in error_msg:
                parts = error_msg.split("Current browser version is")
                chrome_version = parts[1].split("\n")[0].strip()
            if "only supports Chrome version" in error_msg:
                parts = error_msg.split("only supports Chrome version")
                chromedriver_version = parts[1].split("\n")[0].strip()

            mensaje_final = f"Error al renovar cookies de Farmacias del Pueblo:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la versión {chromedriver_version} o superior.\nVe a:\nchrome://settings/help"
            if not chromedriver_version:
                mensaje_final = f"Error al renovar cookies de Farmacias del Pueblo:\n\n{e}\n\n💡 Solución recomendada:\nAbre Chrome y actualiza a la última versión.\nVe a:\nchrome://settings/help"

            messagebox.showerror("Error", mensaje_final)
            print(f"[ERROR] FDP: {e}")

    def cerrar_programa(self):
        self.root.destroy()
        os._exit(0)

    def calcular_utilidades(self):
        try:
            costo = float(self.entry_costo.get())
            venta = self.entry_venta.get()
            utilidad = self.entry_utilidad.get()
            base_costo = self.base_costo.get()

            resultado = ""

            if not costo:
                self.resultado_label.config(
                    text="⚠️ Costo final es obligatorio.")
                return

            if venta and utilidad:
                self.resultado_label.config(
                    text="⚠️ Completa solo 1: Precio o % Utilidad.")
                return

            if not venta and not utilidad:
                self.resultado_label.config(
                    text="⚠️ Ingresa al menos Precio o % Utilidad.")
                return

            if utilidad:
                utilidad = float(utilidad)
                if base_costo:
                    venta = costo * (1 + utilidad / 100)
                else:
                    venta = costo / (1 - utilidad / 100)
                resultado = f"💰 Precio de Venta = ${venta:.2f}"
            else:
                venta = float(venta)
                if base_costo:
                    utilidad = ((venta - costo) / costo) * 100
                else:
                    utilidad = ((venta - costo) / venta) * 100
                resultado = f"📊 % Utilidad = {utilidad:.2f}%"

            self.resultado_label.config(text=resultado)

        except ValueError:
            self.resultado_label.config(
                text="❌ Ingresa valores numéricos válidos.")
