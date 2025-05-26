# 🛒 Comparador de Precios de Supermercados (Argentina)

Aplicación de escritorio desarrollada en **Python + Tkinter** para comparar precios de productos en supermercados argentinos que usan la tecnología **VTEX**.  
Permite buscar productos por **nombre**, **EAN**, o **subir un Excel por lote**, obteniendo precios y disponibilidad en tiempo real.  
Incluye sistema de **renovación de cookies** para superar bloqueos de Cloudflare.

---

## 🧱 Estructura del Proyecto

```
scraper_supermercados/
├── assets/ # Carpeta para archivos de cookies (.json)
│ ├── cookies_carrefour.json
│ ├── cookies_vea.json
│ ├── cookies_jumbo.json
├── scrapers/ # Scrapers para cada supermercado
│ ├── carrefour_scraper.py
│ ├── vea_scraper.py
│ ├── jumbo_scraper.py
│ ├── libre_scraper.py # Comodín e Hiperlibertad
├── utils/ # Utilidades y procesamiento
│ ├── procesar_lote.py # Lógica para búsqueda por lote (Excel)
│ ├── renovar_cookies_carrefour.py
│ ├── renovar_cookies_vea.py
│ ├── renovar_cookies_jumbo.py
├── ui/ # Interfaz gráfica de usuario
│ ├── main_window.py
├── requirements.txt # Dependencias del proyecto
```

---

## 🚀 Características principales

✅ Búsqueda de productos por **nombre** o **EAN**  
✅ Subida de **Excel por lote** con comparación cruzada por EAN  
✅ Scrapers para:

- Carrefour
- Vea
- Jumbo
- Comodín
- Hiperlibertad

✅ Renovación de cookies directamente desde la interfaz  
✅ Búsqueda **flexible** por nombre + cruce **preciso** por EAN  
✅ Generación de Excel final con:

- Precios de la competencia
- Disponibilidad
- Análisis de desvío de precios
- Comparativa resumida

✅ Soporta **múltiples EAN por producto** (separados por comas)  
✅ Loader visual durante el scraping y procesamiento

---

## 💻 Requisitos

- Python 3.9 o superior
- Google Chrome instalado
- ChromeDriver compatible (se descarga automáticamente con `undetected_chromedriver`)

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

---

## 🧪 Ejecución del proyecto

```bash
python ui/main_window.py
```

---

## ♻️ Renovar cookies manualmente

Si Carrefour, Vea o Jumbo dejan de funcionar, ejecutá alguno de estos scripts:

```bash
python utils/renovar_cookies_carrefour.py
python utils/renovar_cookies_vea.py
python utils/renovar_cookies_jumbo.py

```

---

## 📦 Empaquetado como .exe (opcional)

Si querés distribuir la app como ejecutable para Windows:

```bash
pyinstaller --noconfirm --onefile --windowed --add-data "assets;assets" ui/main_window.py
```

---

## 👨‍💻 Autor

- Desarrollado por **Nacho**
- Proyecto en evolución: se están agregando mejoras para coincidencia exacta, empaquetado y rendimiento avanzado

---
