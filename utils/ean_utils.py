import re


def limpiar_eans(eans_raw):
    """
    Recibe un string de EANs como:
    "'0000000000001;\n'2000001000000;\n'2100001000000"
    y devuelve una lista limpia de EANs:
    ['0000000000001', '2000001000000', '2100001000000']
    """
    if not eans_raw:
        return []

    # Separar por ; o salto de línea
    eans = re.split(r';|\n', eans_raw)
    eans = [e.strip().replace("'", "") for e in eans]
    eans = [e for e in eans if e]  # Quitar vacíos
    return eans
