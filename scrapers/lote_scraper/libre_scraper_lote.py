import httpx
import re


def buscar_vtex_lote(nombre_producto, eans, dominio):
    query = nombre_producto.replace(" ", "%20")
    url = f"https://{dominio}/api/catalog_system/pub/products/search/?ft={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "es-AR,es;q=0.9",
        "Referer": f"https://{dominio}/",
        "Origin": f"https://{dominio}"
    }

    # Mapeamos el dominio a nombre amigable
    nombres_tienda = {
        "www.comodinencasa.com.ar": "Comodín",
        "www.hiperlibertad.com.ar": "Hiperlibertad"
    }
    nombre_super = nombres_tienda.get(dominio, dominio)

    try:
        with httpx.Client(http2=True, headers=headers, timeout=15.0) as client:
            response = client.get(url)
            print(
                f"🛰️ [{nombre_super} - Lote] Status code: {response.status_code}")
            if response.status_code not in [200, 206]:
                return []

            productos = response.json()
            resultados = []

            palabras = [p.lower()
                        for p in nombre_producto.split() if len(p) > 1]

            for producto in productos:
                for item in producto.get("items", []):
                    nombre = item.get("nameComplete", "").lower()
                    ean_item = item.get("ean", "").strip().lstrip("'")

                    # 🎯 Si EAN coincide, lo traemos
                    if any(ean_item == e.strip().lstrip("'") for e in eans if e):
                        precio = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("Price", "No disponible")
                        disponible = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("IsAvailable", False)
                        link = f"https://{dominio}/{producto.get('linkText', '')}/p"
                        resultados.append({
                            "supermercado": nombre_super,
                            "nombre": nombre,
                            "ean": ean_item,
                            "precio": precio,
                            "isAvailable": disponible,
                            "url": link
                        })
                        continue

                    # 🎯 Si no hay EAN o no coincide, filtro laxo por palabras
                    if any(p in nombre for p in palabras):
                        precio = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("Price", "No disponible")
                        disponible = item.get("sellers", [{}])[0].get(
                            "commertialOffer", {}).get("IsAvailable", False)
                        link = f"https://{dominio}/{producto.get('linkText', '')}/p"
                        resultados.append({
                            "supermercado": nombre_super,
                            "nombre": nombre,
                            "ean": ean_item,
                            "precio": precio,
                            "isAvailable": disponible,
                            "url": link
                        })

            return resultados

    except Exception as e:
        print(f"❌ Error {nombre_super} Lote: {e}")
        return []


if __name__ == "__main__":
    print("\n🔍 Buscando...")
    dominios = ["www.comodinencasa.com.ar", "www.hiperlibertad.com.ar"]
    for dominio in dominios:
        resultados = buscar_vtex_lote(
            nombre_producto="cafe torrado",
            eans=["7790150006375", "7790150006177"],
            dominio=dominio
        )
        if not resultados:
            print(f"⚠️ No se encontraron resultados en {dominio}.")
        else:
            for r in resultados:
                print(
                    f"- {r['supermercado']} | {r['nombre']} | EAN: {r['ean']} | ${r['precio']} | Disponible: {r['isAvailable']} | {r['url']}")
