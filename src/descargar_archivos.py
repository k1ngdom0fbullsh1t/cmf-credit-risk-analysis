"""
Descarga todos los archivos Excel de provisiones por riesgo de crédito
desde el portal CMF Chile.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re

BASE_URL = "https://www.cmfchile.cl/portal/estadisticas/626/"
PAGE_URL = BASE_URL + "w4-propertyvalue-29875.html"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ANIO_DESDE = 2016


def obtener_links(session: requests.Session) -> list[dict]:
    """Extrae todos los links de descarga desde la página principal."""
    response = session.get(PAGE_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=re.compile(r"articles-\d+_recurso_1\.(xlsx?)")):
        href = a["href"]
        # el título está en el <article> padre, no en el <a>
        article = a.find_parent("article")
        nombre = article.get_text(separator=" ", strip=True) if article else ""
        url_completa = BASE_URL + href if not href.startswith("http") else href
        extension = "xlsx" if "xlsx" in href else "xls"
        links.append({"nombre": nombre, "url": url_completa, "ext": extension})

    return links


def nombre_archivo(nombre: str, ext: str) -> str:
    """Genera un nombre de archivo limpio desde el título del documento."""
    # Extraer mes y año del título
    meses = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    nombre_lower = nombre.lower()
    mes_num = next((v for k, v in meses.items() if k in nombre_lower), "00")
    anio = re.search(r"\b(20\d{2})\b", nombre)
    anio_num = anio.group(1) if anio else "0000"
    return f"cmf_{anio_num}_{mes_num}.{ext}"


def descargar(session: requests.Session, url: str, destino: Path) -> bool:
    """Descarga un archivo y lo guarda en destino. Retorna True si tuvo éxito."""
    try:
        r = session.get(url, timeout=60, stream=True)
        r.raise_for_status()
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; investigacion-academica)"})

    print("Obteniendo lista de archivos...")
    todos = obtener_links(session)
    links = [l for l in todos if re.search(r"\b(20\d{2})\b", l["nombre"]) and
             int(re.search(r"\b(20\d{2})\b", l["nombre"]).group(1)) >= ANIO_DESDE]
    print(f"Total encontrados: {len(todos)} | Filtrando desde {ANIO_DESDE}: {len(links)} archivos.\n")

    ok, omitidos, errores = 0, 0, 0

    for i, link in enumerate(links, 1):
        fname = nombre_archivo(link["nombre"], link["ext"])
        destino = OUTPUT_DIR / fname

        if destino.exists():
            print(f"[{i:>3}/{len(links)}] Omitido (ya existe): {fname}")
            omitidos += 1
            continue

        print(f"[{i:>3}/{len(links)}] Descargando: {fname}")
        exito = descargar(session, link["url"], destino)

        if exito:
            ok += 1
        else:
            errores += 1

        time.sleep(0.5)  # pausa para no saturar el servidor

    print(f"\nResumen: {ok} descargados, {omitidos} omitidos, {errores} errores.")


if __name__ == "__main__":
    main()
