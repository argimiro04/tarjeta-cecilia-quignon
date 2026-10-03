"""
Prepara las fotos de las obras para publicarlas en la web.

Lee los originales de la carpeta "fotos originales" (que NO se sube al repo)
y deja en "imagenes/" una version lista para publicar:

  - rotacion EXIF aplicada (si no, las verticales salen tumbadas)
  - color convertido a sRGB, que es lo que entienden los navegadores
  - 1400 px el lado largo como maximo (nunca se amplia)
  - WebP, buscando que ningun archivo pase de 300 KB
  - sin EXIF ni GPS: se guarda solo el mapa de pixeles
  - se anade el (c) de la autora

Uso:   py herramientas/procesar-fotos.py
"""

from pathlib import Path
import io
import sys

from PIL import Image, ImageCms, ImageOps

# --- Ajustes ---------------------------------------------------------------
BASE        = Path(__file__).resolve().parent.parent
ORIGINALES  = BASE / "fotos originales"
SALIDA      = BASE / "imagenes"
LADO_LARGO  = 1400              # px del lado mas largo
CALIDADES   = [82, 76, 70, 64]  # se va bajando hasta que el archivo quepa
PESO_MAX    = 300 * 1024        # 300 KB por obra
AUTORA      = "Cecilia Quignon"
EXTENSIONES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}

XMP = (
    '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>'
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">'
    f'<dc:creator><rdf:Seq><rdf:li>{AUTORA}</rdf:li></rdf:Seq></dc:creator>'
    '<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">'
    f'(c) {AUTORA}. Todos los derechos reservados.'
    '</rdf:li></rdf:Alt></dc:rights>'
    '</rdf:Description></rdf:RDF></x:xmpmeta>'
    '<?xpacket end="r"?>'
).encode("utf-8")


def tenia_gps(imagen):
    """Mira si el original traia coordenadas antes de limpiarlo."""
    try:
        exif = imagen.getexif()
        return bool(exif and exif.get_ifd(0x8825))
    except Exception:
        return False


def a_srgb(imagen):
    """Pasa la imagen a sRGB usando su perfil incrustado, si lo trae."""
    icc = imagen.info.get("icc_profile")
    if icc:
        try:
            origen = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            destino = ImageCms.createProfile("sRGB")
            return ImageCms.profileToProfile(imagen, origen, destino, outputMode="RGB"), True
        except Exception:
            pass
    return imagen.convert("RGB"), False


def guardar(imagen, destino):
    """Guarda en WebP bajando calidad hasta que quepa. Devuelve (calidad, peso)."""
    perfil_srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()

    for calidad in CALIDADES:
        opciones = dict(quality=calidad, method=6, icc_profile=perfil_srgb)
        try:
            imagen.save(destino, "WEBP", xmp=XMP, **opciones)
        except (TypeError, ValueError):
            # Pillow sin soporte de xmp en WebP: el (c) es un extra, no un requisito
            imagen.save(destino, "WEBP", **opciones)
        peso = destino.stat().st_size
        if peso <= PESO_MAX:
            return calidad, peso
    return CALIDADES[-1], destino.stat().st_size


def main():
    if not ORIGINALES.is_dir():
        sys.exit(f"No encuentro la carpeta de originales: {ORIGINALES}")

    fotos = sorted(f for f in ORIGINALES.iterdir() if f.suffix.lower() in EXTENSIONES)
    if not fotos:
        sys.exit(f"No hay fotos en {ORIGINALES}")

    SALIDA.mkdir(exist_ok=True)

    print(f"{'#':>2}  {'archivo':24} {'original':>12}  {'final':>11}  {'peso':>8} "
          f" {'cal':>3}  GPS  perfil")
    print("-" * 80)

    for n, ruta in enumerate(fotos, 1):
        original = Image.open(ruta)
        medidas_ini = original.size
        gps = tenia_gps(original)

        imagen = ImageOps.exif_transpose(original)      # 1) rotacion
        imagen, convertida = a_srgb(imagen)             # 2) color
        imagen.thumbnail((LADO_LARGO, LADO_LARGO), Image.LANCZOS)   # 3) tamano

        destino = SALIDA / f"obra-{n:02d}.webp"
        calidad, peso = guardar(imagen, destino)        # 4) y 5)

        aviso = "  <-- mas pequena de 1400 px" if max(medidas_ini) < LADO_LARGO else ""
        print(f"{n:>2}  {ruta.name:24} {medidas_ini[0]:>5}x{medidas_ini[1]:<6} "
              f"{imagen.size[0]:>5}x{imagen.size[1]:<5} {peso/1024:>7.0f}K "
              f"{calidad:>4}  {'SI' if gps else ' -'}  "
              f"{'convertido' if convertida else 'sRGB'}{aviso}")

    print("-" * 80)
    print(f"Listo: {len(fotos)} obras en {SALIDA.relative_to(BASE)}/")
    print("Los originales se quedan sin tocar y fuera del repo.")


if __name__ == "__main__":
    main()
