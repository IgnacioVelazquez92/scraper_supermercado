import httpx
import json


def cargar_cookies(path="cookies_carrefour.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cookies.")
        return None


def buscar_carrefour_httpx(keywords, exacta=False):
    query = keywords.replace(" ", "%20")
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

    try:
        with httpx.Client(http2=True, headers=headers, cookies=cookies, timeout=10.0) as client:
            response = client.get(url)
            print(f"🛰️ [Carrefour] Status: {response.status_code}")

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
                    nombre_palabras = nombre_lower.split()

                    if exacta and not all(p in nombre_palabras for p in palabras):
                        continue

                    ean = item.get("ean", "Sin EAN")
                    precio = item.get("sellers", [{}])[0].get(
                        "commertialOffer", {}).get("Price", "No disponible")
                    link = f"https://www.carrefour.com.ar/{producto.get('linkText')}/p"

                    resultados.append({
                        "nombre": nombre,
                        "ean": ean,
                        "precio": precio,
                        "url": link
                    })

            return resultados

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


if __name__ == "__main__":
    resultados = buscar_carrefour_httpx(
        "caldo knorr verdura 12 cubos", exacta=True)

    if not resultados:
        print("⚠️ No se encontraron resultados.")
    else:
        for r in resultados:
            print(
                f"- {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | {r['url']}")
