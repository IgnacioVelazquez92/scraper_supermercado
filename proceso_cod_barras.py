import pandas as pd

# 📂 Archivo Excel
archivo_entrada = "codigo_de_barras.xlsx"
hoja = "Hoja1"
archivo_salida = "productos_unificados.xlsx"

# 📥 Leer el archivo Excel
df = pd.read_excel(archivo_entrada, sheet_name=hoja)

# 🔧 Limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# 🧹 Limpiar precios: transformar a float (manejar decimales correctamente)
df['precio'] = df['precio'].astype(str).str.replace(
    '.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

# 🔄 Agrupar por 'codigo' y 'descripcion'


def procesar_grupo(grupo):
    codigos = sorted(grupo['codigo_barra'].dropna().unique())
    precios = sorted(grupo['precio'].dropna().unique())

    codigos_str = ';\n'.join(codigos)

    if len(precios) == 1:
        precio_str = str(precios[0])
    else:
        precio_str = ';\n'.join([str(p) for p in precios])

    tiene_multiples_codigos = "sí" if len(codigos) > 1 else "no"
    tiene_multiples_precios = "sí" if len(precios) > 1 else "no"

    return pd.Series({
        'codigo_barra': codigos_str,
        'precio': precio_str,
        'multiples_cb': tiene_multiples_codigos,
        'multiples_p': tiene_multiples_precios
    })


df_grouped = df.groupby(['codigo', 'descripcion'], group_keys=False).apply(
    procesar_grupo).reset_index()


# 📤 Guardar a Excel
df_grouped.to_excel(archivo_salida, index=False)

print(f"✅ Archivo procesado y guardado como: {archivo_salida}")
