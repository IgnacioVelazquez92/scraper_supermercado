import httpx
import re


def buscar_vtex_httpx(keywords, dominio, exacta=False):
    query = keywords.replace(" ", "%20")
    url = f"https://{dominio}/api/catalog_system/pub/products/search/?ft={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": f"https://{dominio}/",
        "Origin": f"https://{dominio}"
    }

    try:
        with httpx.Client(http2=True, headers=headers, timeout=15.0) as client:
            response = client.get(url)
            print(f"🛰️ [{dominio}] Status code: {response.status_code}")
            if response.status_code not in [200, 206]:
                return []

            productos = response.json()
            resultados = []
            palabras = keywords.lower().split()

            # Mapeamos el dominio a nombre más amigable
            nombres_tienda = {
                "www.comodinencasa.com.ar": "Comodín",
                "www.hiperlibertad.com.ar": "Hiperlibertad"
            }
            nombre_super = nombres_tienda.get(dominio, dominio)

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
                    url_producto = f"https://{dominio}/{producto.get('linkText', '')}/p"

                    resultados.append({
                        "nombre": nombre,
                        "ean": ean,
                        "precio": precio,
                        "isAvailable": disponible,
                        "supermercado": nombre_super,  # Aquí agregamos el nombre del super
                        "url": url_producto
                    })

            return resultados

    except Exception as e:
        print(f"❌ Error con {dominio}: {e}")
        return []


# Test manual
if __name__ == "__main__":
    keywords = "caldo knorr verdura"
    dominios = [
        "www.comodinencasa.com.ar",
        "www.hiperlibertad.com.ar"
    ]
    for dominio in dominios:
        print(f"\n🔎 Resultados en {dominio}")
        resultados = buscar_vtex_httpx(keywords, dominio, exacta=True)
        if not resultados:
            print("⚠️ No se encontraron resultados.")
        for r in resultados:
            print(
                f"- {r['supermercado']} | {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | Disponible: {r['isAvailable']} | {r['url']}")
