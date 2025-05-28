import pandas as pd
import os
from tkinter import messagebox

from scrapers.lote_scraper.carrefour_scraper_lote import buscar_carrefour_lote
from scrapers.lote_scraper.vea_scraper_lote import buscar_vea_lote
from scrapers.lote_scraper.jumbo_scraper_lote import buscar_jumbo_lote
from scrapers.lote_scraper.libre_scraper_lote import buscar_vtex_lote


def procesar_excel(nombre_archivo, desvio_param, carpeta_destino, nombre_busqueda):
    df = pd.read_excel(nombre_archivo)
    precios_competencia = []
    desvio_significativo = []

    for index, row in df.iterrows():
        print(f"\n🔎 Procesando producto:")
        eans_raw = str(row.get("codigo_barra", "")).replace(
            "\n", "").replace("\r", "")
        eans = [e.strip().lstrip("'")
                for e in eans_raw.split(";") if e.strip()]
        print(f"📦 EANs cargados: {eans}")

        nombre_producto = str(row.get("descripcion", "")).lower()
        precio_venta = float(row.get("precio_venta", 0))

        resultados = []

        for dominio in ["www.comodinencasa.com.ar", "www.hiperlibertad.com.ar"]:
            try:
                encontrados = buscar_vtex_lote(nombre_producto, eans, dominio)
                resultados.extend(encontrados)
            except Exception as e:
                print(f"❌ Error {dominio} Lote: {e}")

        for nombre, funcion in [("Carrefour", buscar_carrefour_lote),
                                ("Vea", buscar_vea_lote),
                                ("Jumbo", buscar_jumbo_lote)]:
            try:
                encontrados = funcion(nombre_producto, eans)
                resultados.extend(encontrados)
            except Exception as e:
                print(f"❌ Error {nombre} Lote: {e}")

        # Filtrar resultados por coincidencia exacta de EAN
        resultados_filtrados = []
        for r in resultados:
            match = any(r['ean'] == ean for ean in eans)
            print(
                f"🔎 Comparando EAN Excel: {eans} ⬄ EAN Scrapeado: {r['ean']} ➡️ Match: {match}")
            if match and r['isAvailable']:
                resultados_filtrados.append(r)

        if resultados_filtrados:
            detalles = [
                f"{r['supermercado']}: ${r['precio']}" for r in resultados_filtrados]
            precios_competencia.append(" | ".join(detalles))

            disponibles = [r['precio'] for r in resultados_filtrados]
            if disponibles:
                promedio = sum(disponibles) / len(disponibles)
                desvio = abs((precio_venta - promedio) / promedio) * 100
                desvio_significativo.append(
                    "SI" if desvio >= desvio_param else "NO")
            else:
                desvio_significativo.append("NO")
        else:
            precios_competencia.append("Sin disponibles")
            desvio_significativo.append("NO")

    df["precio_competencia"] = precios_competencia
    df["desvio"] = desvio_significativo

    salida = os.path.join(carpeta_destino, f"{nombre_busqueda}.xlsx")
    df.to_excel(salida, index=False)
    messagebox.showinfo(
        "¡Listo!", f"El archivo {salida} se generó correctamente.")
    print(f"✅ Archivo generado: {salida}")
