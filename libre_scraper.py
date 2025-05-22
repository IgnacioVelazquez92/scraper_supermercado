import httpx


def buscar_vtex_httpx(keywords, dominio):
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

            for producto in productos:
                for item in producto.get("items", []):
                    nombre = item.get("nameComplete", "Sin nombre")
                    ean = item.get("ean", "Sin EAN")
                    precio = item.get("sellers", [{}])[0].get(
                        "commertialOffer", {}).get("Price", "No disponible")
                    imagen = item.get("images", [{}])[0].get("imageUrl", "")
                    url_producto = f"https://{dominio}/{producto.get('linkText', '')}/p"

                    resultados.append({
                        "nombre": nombre,
                        "ean": ean,
                        "precio": precio,
                        "imagen": imagen,
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
        resultados = buscar_vtex_httpx(keywords, dominio)
        if not resultados:
            print("⚠️ No se encontraron resultados.")
        for r in resultados:
            print(
                f"- {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | {r['url']}")
