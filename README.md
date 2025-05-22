# 🛒 Comparador de Precios de Supermercados (Argentina)

Este proyecto es una aplicación de escritorio desarrollada en **Python con Tkinter** para comparar precios de productos entre diferentes supermercados que utilizan la tecnología **VTEX** en Argentina.

Permite buscar productos por nombre o código de barras (EAN), visualizar precios de varios sitios simultáneamente y renovar cookies de sesión para evitar bloqueos por Cloudflare.

---

## 🧱 Estructura del Proyecto

```
scraper_supermercados/
├── main_tkinter.py                # Interfaz gráfica principal
├── libre_scraper.py               # Scraper para Comodín e HiperLibertad
├── carrefour_scraper.py          # Scraper con cookies para Carrefour
├── vea_scraper.py                # Scraper con cookies para Vea
├── jumbo_scraper.py              # Scraper con cookies para Jumbo
├── renovar_cookies_carrefour.py  # Script para renovar cookies Carrefour
├── renovar_cookies_vea.py        # Script para renovar cookies Vea
├── renovar_cookies_jumbo.py      # Script para renovar cookies Jumbo
├── cookies_carrefour.json        # Cookies vigentes para Carrefour
├── cookies_vea.json              # Cookies vigentes para Vea
├── cookies_jumbo.json            # Cookies vigentes para Jumbo
├── requirements.txt              # Dependencias del proyecto
```

---

## 🚀 Características principales

- Búsqueda de productos por nombre o EAN
- Comparación simultánea entre:

  - Carrefour
  - Vea
  - Jumbo
  - Comodín
  - HiperLibertad

- Modo de coincidencia flexible o exacta (próxima funcionalidad)
- Botones para renovar cookies directamente desde la interfaz
- Acceso directo a los productos con doble clic

---

## 💻 Requisitos

- Python 3.9 o superior
- Google Chrome instalado

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

---

## 🧪 Ejecución del proyecto

```bash
python main_tkinter.py
```

---

## ♻️ Renovar cookies manualmente

Si Carrefour, Vea o Jumbo dejan de funcionar, ejecutá alguno de estos scripts:

```bash
python renovar_cookies_carrefour.py
python renovar_cookies_vea.py
python renovar_cookies_jumbo.py
```

---

## 📦 Empaquetado como .exe (opcional)

Si querés distribuir la app como ejecutable para Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main_tkinter.py
```

---

## 👨‍💻 Autor

- Desarrollado por **Nacho**
- Proyecto en evolución: se están agregando mejoras para coincidencia exacta, empaquetado y rendimiento avanzado

---

## 🛠️ TODO (Próximos pasos)

- [x] Soporte para scraping con httpx + HTTP/2
- [x] Manejo de cookies para evitar bloqueos
- [x] Interfaz gráfica amigable
- [ ] Checkbox de "coincidencia exacta"
- [ ] Mejora visual para categorizar supermercados
- [ ] Filtros por precio y ordenamiento
