import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from libre_scraper import buscar_vtex_httpx
from carrefour_scraper import buscar_carrefour_httpx
from vea_scraper import buscar_vea_httpx
from jumbo_scraper import buscar_jumbo_httpx


class SupermercadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Precios Supermercados")
        self.root.geometry("950x500")

        # Entrada de búsqueda
        self.entry = tk.Entry(self.root, font=("Arial", 14), width=50)
        self.entry.pack(pady=10)

        # Botón de búsqueda
        self.search_btn = tk.Button(
            self.root, text="Buscar", command=self.buscar, font=("Arial", 12))
        self.search_btn.pack()

        # Tabla de resultados
        self.tree = ttk.Treeview(self.root, columns=(
            "Supermercado", "Nombre", "EAN", "Precio", "URL"), show="headings")
        for col in ("Supermercado", "Nombre", "EAN", "Precio", "URL"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180 if col !=
                             "URL" else 250, anchor=tk.W)
        self.tree.pack(expand=True, fill=tk.BOTH, pady=10)
        self.tree.bind("<Double-1>", self.abrir_url)

        # Botones para renovar cookies
        self.cookie_frame = tk.Frame(self.root)
        self.cookie_frame.pack()

        tk.Button(self.cookie_frame, text="♻️ Carrefour",
                  command=self.renovar_carrefour).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Vea",
                  command=self.renovar_vea).pack(side=tk.LEFT, padx=5)
        tk.Button(self.cookie_frame, text="♻️ Jumbo",
                  command=self.renovar_jumbo).pack(side=tk.LEFT, padx=5)

    def abrir_url(self, event):
        item = self.tree.item(self.tree.selection()[0])
        url = item['values'][4]
        webbrowser.open(url)

    def buscar(self):
        keywords = self.entry.get().strip()
        if not keywords:
            messagebox.showwarning("Atención", "Ingrese un producto a buscar.")
            return

        self.tree.delete(*self.tree.get_children())

        # Buscar en sitios libres (Comodín y Hiperlibertad)
        for dominio in ["www.comodinencasa.com.ar", "www.hiperlibertad.com.ar"]:
            try:
                resultados = buscar_vtex_httpx(keywords, dominio)
                for r in resultados:
                    self.tree.insert("", tk.END, values=(
                        dominio, r['nombre'], r['ean'], r['precio'], r['url']))
            except Exception as e:
                print(f"Error en {dominio}: {e}")

        # Carrefour
        try:
            resultados = buscar_carrefour_httpx(keywords)
            for r in resultados:
                self.tree.insert("", tk.END, values=(
                    "Carrefour", r['nombre'], r['ean'], r['precio'], r['url']))
        except Exception as e:
            print("Carrefour falló:", e)

        # Vea
        try:
            resultados = buscar_vea_httpx(keywords)
            for r in resultados:
                self.tree.insert("", tk.END, values=(
                    "Vea", r['nombre'], r['ean'], r['precio'], r['url']))
        except Exception as e:
            print("Vea falló:", e)

        # Jumbo
        try:
            resultados = buscar_jumbo_httpx(keywords)
            for r in resultados:
                self.tree.insert("", tk.END, values=(
                    "Jumbo", r['nombre'], r['ean'], r['precio'], r['url']))
        except Exception as e:
            print("Jumbo falló:", e)

    def renovar_carrefour(self):
        import renovar_cookies_carrefour
        renovar_cookies_carrefour.renovar_cookies_carrefour()
        messagebox.showinfo("Listo", "Cookies de Carrefour renovadas")

    def renovar_vea(self):
        import renovar_cookies_vea
        renovar_cookies_vea.renovar_cookies_vea()
        messagebox.showinfo("Listo", "Cookies de Vea renovadas")

    def renovar_jumbo(self):
        import renovar_cookies_jumbo
        renovar_cookies_jumbo.renovar_cookies_jumbo()
        messagebox.showinfo("Listo", "Cookies de Jumbo renovadas")


if __name__ == "__main__":
    root = tk.Tk()
    app = SupermercadoApp(root)
    root.mainloop()
