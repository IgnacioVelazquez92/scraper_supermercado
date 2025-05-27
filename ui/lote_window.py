import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from utils.procesar_lote import procesar_excel
import pandas as pd


def descargar_plantilla():
    plantilla_data = {
        "codigo unico": [""],
        "nombre": [""],
        "ean": [""],
        "precio": [""],  # 💡 Agregado: columna precio
        "costo final": [""],
        "precio de venta": [""],
        "precio competencia": [""],
        "desvío": [""]
    }
    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Guardar plantilla como"
    )
    if ruta:
        pd.DataFrame(plantilla_data).to_excel(ruta, index=False)
        messagebox.showinfo("Plantilla descargada",
                            f"Plantilla guardada en: {ruta}")


def main():
    root = tk.Tk()
    root.title("Búsqueda por Lote - Comparador de Precios")
    root.geometry("600x420")
    root.resizable(False, False)

    tk.Button(root, text="📄 Descargar Plantilla Excel",
              command=descargar_plantilla, bg="#2196F3", fg="white").pack(pady=10)

    frame = tk.Frame(root, bd=2, relief=tk.SUNKEN, padx=10, pady=10)
    frame.pack(pady=5)

    tk.Label(frame, text="Ruta del archivo Excel:").grid(
        row=0, column=0, sticky='w')
    entry_archivo = tk.Entry(frame, width=50)
    entry_archivo.grid(row=0, column=1)
    tk.Button(frame, text="Seleccionar", command=lambda: entry_archivo.insert(
        0, filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")]))).grid(row=0, column=2)

    tk.Label(frame, text="Carpeta de destino:").grid(
        row=1, column=0, sticky='w')
    entry_carpeta = tk.Entry(frame, width=50)
    entry_carpeta.grid(row=1, column=1)
    tk.Button(frame, text="Seleccionar", command=lambda: entry_carpeta.insert(
        0, filedialog.askdirectory())).grid(row=1, column=2)

    tk.Label(frame, text="Nombre del archivo de salida:").grid(
        row=2, column=0, sticky='w')
    entry_nombre = tk.Entry(frame, width=50)
    entry_nombre.grid(row=2, column=1)

    tk.Label(frame, text="% Desvío permitido:").grid(
        row=3, column=0, sticky='w')
    entry_desvio = tk.Entry(frame, width=50)
    entry_desvio.grid(row=3, column=1)

    def ejecutar():
        archivo = entry_archivo.get().strip()
        carpeta = entry_carpeta.get().strip()
        nombre_busqueda = entry_nombre.get().strip()
        desvio_str = entry_desvio.get().strip()

        if not all([archivo, carpeta, nombre_busqueda, desvio_str]):
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        try:
            desvio = float(desvio_str)
        except:
            messagebox.showerror("Error", "El desvío debe ser un número.")
            return

        loader = tk.Toplevel(root)
        loader.title("Procesando...")
        loader.geometry("300x100")
        tk.Label(loader, text="Procesando datos... por favor espera.",
                 font=("Arial", 12)).pack(pady=30)
        loader.update()

        def proceso():
            try:
                procesar_excel(archivo, desvio, carpeta, nombre_busqueda)
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")
                print(f"❌ Error: {e}")
            finally:
                loader.destroy()

        threading.Thread(target=proceso).start()

    tk.Button(root, text="📥 Subir y Procesar Excel", command=ejecutar,
              bg="#4CAF50", fg="white", height=2).pack(pady=20)

    root.mainloop()
