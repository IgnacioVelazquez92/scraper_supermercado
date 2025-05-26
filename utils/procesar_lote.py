import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import threading

from scrapers.libre_scraper import buscar_vtex_httpx
from scrapers.carrefour_scraper import buscar_carrefour_httpx
from scrapers.vea_scraper import buscar_vea_httpx
from scrapers.jumbo_scraper import buscar_jumbo_httpx


def procesar_excel(nombre_archivo, desvio_param, carpeta_destino, nombre_busqueda):
    df = pd.read_excel(nombre_archivo)
    precios_competencia = []
    desvio_significativo = []

    for index, row in df.iterrows():
        eans_raw = str(row["ean"]).lstrip("'")
        eans = [e.strip().lstrip("'") for e in eans_raw.split(",")]
        nombre_producto = str(row["nombre"])
        precio_venta = row["precio de venta"]

        resultados = []

        for dominio in ["www.comodinencasa.com.ar", "www.hiperlibertad.com.ar"]:
            try:
                encontrados = buscar_vtex_httpx(
                    keywords=nombre_producto, dominio=dominio, exacta=False)
                filtrados = [p for p in encontrados if p["ean"] in eans]
                for p in filtrados:
                    resultados.append((dominio, p["precio"], p["isAvailable"]))
            except Exception as e:
                print(f"Error {dominio}: {e}")

        for nombre, funcion in [("Carrefour", buscar_carrefour_httpx), ("Vea", buscar_vea_httpx), ("Jumbo", buscar_jumbo_httpx)]:
            try:
                encontrados = funcion(keywords=nombre_producto, exacta=False)
                filtrados = [p for p in encontrados if p["ean"] in eans]
                for p in filtrados:
                    resultados.append((nombre, p["precio"], p["isAvailable"]))
            except Exception as e:
                print(f"Error {nombre}: {e}")

        if resultados:
            precios = [
                f"{r[0]}: ${r[1]}, {'disponible' if r[2] else 'no disponible'}" for r in resultados]
            precios_str = "; ".join(precios)
            precios_competencia.append(precios_str)

            disponibles = [r[1] for r in resultados if r[2]]
            if disponibles:
                promedio = sum(disponibles) / len(disponibles)
                desvio = abs((precio_venta - promedio) / promedio) * 100
                desvio_significativo.append(
                    "SI" if desvio >= desvio_param else "NO")
            else:
                desvio_significativo.append("NO")
        else:
            precios_competencia.append("Sin resultados")
            desvio_significativo.append("NO")

    df["precio competencia"] = precios_competencia
    df["desvío"] = desvio_significativo

    salida = os.path.join(carpeta_destino, f"{nombre_busqueda}.xlsx")
    df.to_excel(salida, index=False)
    messagebox.showinfo(
        "¡Listo!", f"El archivo {salida} se generó correctamente.")
    print(f"✅ Archivo generado: {salida}")


def descargar_plantilla():
    plantilla_data = {
        "codigo unico": [""],
        "nombre": [""],
        "ean": [""],
        "costo final": [""],
        "precio de venta": [""],
        "precio competencia": [""],
        "desvío": [""]
    }
    df_plantilla = pd.DataFrame(plantilla_data)
    ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[
                                        ("Excel files", "*.xlsx")], title="Guardar plantilla como")
    if ruta:
        df_plantilla.to_excel(ruta, index=False)
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
