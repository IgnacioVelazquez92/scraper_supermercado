import httpx
import json
import os
import re


def cargar_cookies(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..',
                            '..', 'assets', 'cookies_carrefour.json')
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cookies.")
        return None


def buscar_carrefour_lote(nombre_producto, eans):
    query = nombre_producto.replace(" ", "%20")
    url = f"https://www.carrefour.com.ar/api/catalog_system/pub/products/search/?ft={query}"
    cookies_dict = cargar_cookies()
    if not cookies_dict:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.carrefour.com.ar/",
        "Origin": "https://www.carrefour.com.ar"
    }

    cookies = {k: v for k, v in cookies_dict.items()}

    # Limpiar y normalizar los EANs proporcionados
    eans_limpios = [re.sub(r"[^\d]", "", e.strip()) for e in eans if e.strip()]
    print(f"📦 EANs cargados: {eans_limpios}")

    try:
        with httpx.Client(http2=True, headers=headers, cookies=cookies, timeout=10.0) as client:
            response = client.get(url)
            print(f"🛰️ [Carrefour - Lote] Status: {response.status_code}")

            if response.status_code not in [200, 206]:
                return []

            productos = response.json()
            resultados = []

            palabras = [p.lower()
                        for p in nombre_producto.split() if len(p) > 1]

            for producto in productos:
                for item in producto.get("items", []):
                    nombre = item.get("nameComplete", "").lower()
                    ean_item = re.sub(
                        r"[^\d]", "", item.get("ean", "").strip())

                    # Mostrar EAN y URL para depuración
                    link = f"https://www.carrefour.com.ar/{producto.get('linkText', '')}/p"
                    print(
                        f"🔍 Carrefour - EAN encontrado: {ean_item} - URL: {link}")

                    # 🎯 Si EAN coincide, lo traemos
                    if ean_item in eans_limpios:
                        precio = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("Price", "No disponible")
                        disponible = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("IsAvailable", False)
                        resultados.append({
                            "supermercado": "Carrefour",
                            "nombre": nombre,
                            "ean": ean_item,
                            "precio": precio,
                            "isAvailable": disponible,
                            "url": link
                        })

            return resultados

    except Exception as e:
        print(f"❌ Error Carrefour Lote: {e}")
        return []


if __name__ == "__main__":
    print("\n🔍 Buscando...")
    resultados = buscar_carrefour_lote(
        nombre_producto="nuez moscada",
        eans=["7790150050040", "7790150536254"]
    )
    if not resultados:
        print("⚠️ No se encontraron resultados.")
    else:
        for r in resultados:
            print(
                f"- {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | Disponible: {r['isAvailable']} | {r['url']}")
