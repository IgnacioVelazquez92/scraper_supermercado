import httpx
import json
import os
import re


def cargar_cookies(path=None):
    if path is None:
        path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), '..', '..', 'assets', 'cookies_farmacity.json'))

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cookies.")
        return None


def buscar_farmacity_httpx(keywords, exacta=False):
    query = keywords.replace(" ", "%20")
    url = f"https://www.farmacity.com/api/catalog_system/pub/products/search/?ft={query}"
    cookies_dict = cargar_cookies()
    if not cookies_dict:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": "https://www.farmacity.com/",
        "Origin": "https://www.farmacity.com"
    }

    cookies = {k: v for k, v in cookies_dict.items()}

    try:
        with httpx.Client(http2=True, headers=headers, cookies=cookies, timeout=10.0) as client:
            response = client.get(url)
            print(f"🛰️ [Farmacity] Status: {response.status_code}")

            if response.status_code not in [200, 206]:
                print("⚠️ Respuesta no válida.")
                return []

            productos = response.json()
            resultados = []
            palabras = keywords.lower().split()

            for producto in productos:
                for item in producto.get("items", []):
                    nombre = item.get("nameComplete", "Sin nombre")
                    nombre_lower = nombre.lower()
                    nombre_normalizado = re.sub(
                        r'[^a-z0-9]', ' ', nombre_lower).replace('  ', ' ')

                    palabras_normalizadas = [
                        re.sub(r'[^a-z0-9]', '', p) for p in palabras]

                    if exacta:
                        if not all(p in nombre_normalizado for p in palabras_normalizadas):
                            continue

                    ean = item.get("ean", "Sin EAN")
                    precio = item.get("sellers", [{}])[0].get(
                        "commertialOffer", {}).get("Price", "No disponible")
                    disponible = item.get("sellers", [{}])[0].get(
                        "commertialOffer", {}).get("IsAvailable", False)
                    link = f"https://www.farmacity.com/{producto.get('linkText')}/p"

                    resultados.append({
                        "nombre": nombre,
                        "ean": ean,
                        "precio": precio,
                        "isAvailable": disponible,
                        "url": link
                    })

            return resultados

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


if __name__ == "__main__":
    resultados = buscar_farmacity_httpx("ibuprofeno", exacta=False)
    if not resultados:
        print("⚠️ No se encontraron resultados.")
    else:
        for r in resultados:
            print(
                f"- {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | Disponible: {r['isAvailable']} | {r['url']}")
