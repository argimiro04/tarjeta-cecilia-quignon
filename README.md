# Tarjeta de presentación · Cecilia Quignón

Tarjeta digital de una artista plástica: una sola página, pensada para abrirse desde un
código QR impreso. Encargo real, en desarrollo.

🔗 **Ver la página:** `https://USUARIO.github.io/REPOSITORIO/`

> **Estado: maqueta en curso.** El diseño y el funcionamiento están terminados, pero los
> textos (biografía, títulos de las obras, años y técnicas) aparecen como `Rellenar` a la
> espera de que los facilite la artista. Las imágenes sí son las definitivas.

---

## El encargo

Una artista necesita algo que enseñar en exposiciones y ferias: un QR en una tarjeta de
papel que, al escanearlo, abra su obra en el móvil de quien lo escanea. Sin menús, sin
páginas sueltas, sin que haya que explicar nada.

De ahí salen las tres restricciones que mandan sobre todo lo demás:

1. **Una sola página autocontenida.** Todo el HTML, CSS, JavaScript y los gráficos
   decorativos viven dentro de `index.html`. Sin frameworks, sin CDN, sin dependencias.
2. **Primero el móvil.** Se abre desde la cámara de un teléfono, muchas veces con datos y
   mala cobertura. El peso importa.
3. **Todo el estilo, cambiable desde un sitio.** La artista y su entorno no tocan código:
   colores y tipografías tenían que poder ajustarse sin bucear por la hoja de estilos.

## Decisiones técnicas

### Sin dependencias, a propósito

No hay build, ni `node_modules`, ni paquetes que actualizar. Se abre el archivo y
funciona. Para una página que debe seguir viva dentro de cinco años sin mantenimiento,
cada dependencia es una fecha de caducidad.

### Un único bloque de variables

Toda la paleta y las tipografías están en un `:root` comentado al principio del archivo.
Cambiar el aspecto de la página entera es editar ese bloque; el resto del CSS no se toca.

```css
--color-fondo:     #f5f7f9;
--fuente-titulo:   Georgia, "Times New Roman", serif;
--ancho-obra:      60%;     /* ancho de cada obra en móvil */
```

### La galería respeta la obra

Las obras se alternan en zigzag con `flex` y `align-self`. Lo relevante es lo que **no**
se hizo: la retícula cuadrada quedaría más regular, pero obligaría a recortar cuadros que
no son cuadrados. Cada pieza conserva su proporción real.

```css
.obra .marco { aspect-ratio: 1 / 1; }          /* solo huecos sin foto */
.obra .marco:has(img) { aspect-ratio: auto; }  /* con foto manda la obra */
```

Añadir o quitar obras es copiar o borrar un `<figure>`: la alternancia se recoloca sola
con `nth-child`.

### Correo a prueba de robots

La dirección nunca aparece escrita en el HTML. Se compone al cargar la página a partir de
dos variables, de modo que los rastreadores de spam no la encuentran con una búsqueda de
patrón, pero el enlace `mailto:` funciona con normalidad.

### Procesado de imágenes con criterio de privacidad

Las fotos de las obras no se suben tal cual. `herramientas/procesar-fotos.py` las prepara
en este orden, y cada paso está ahí por un motivo:

| Paso | Por qué |
|---|---|
| Aplicar la rotación EXIF | Si se borran los metadatos sin aplicarla, las verticales salen tumbadas |
| Convertir a sRGB | En obra plástica, una desviación de color no es un detalle |
| 1400 px el lado largo | Se ve perfecta en pantalla y da ~12 cm impresos: limita la reproducción |
| WebP con calidad variable | Ningún archivo supera los 300 KB; la galería entera pesa 1 MB |
| Eliminar EXIF y GPS | Las fotos se hacen en el estudio: las coordenadas son el domicilio de la autora |
| Añadir © en XMP | Autoría incrustada, que viaja con el archivo si alguien lo descarga |

Conviene no confundir las dos últimas: **los metadatos no impiden copiar nada**. Lo que
limita de verdad la reproducción impresa es la resolución. El © es prueba de autoría, no
un candado.

Los originales a resolución completa se quedan fuera del repositorio.

### Detalles de uso

- **Barra fija** con resaltado de la sección visible mediante `IntersectionObserver`, no
  con un listener de `scroll`.
- **Ampliación de obra** (*lightbox*) propia, sin librerías: se cierra con ✕, con `Esc` y
  tocando fuera, y devuelve el foco a la obra desde la que se abrió.
- **Accesibilidad**: navegación por teclado, zonas de toque de 44 px, texto alternativo,
  decoración marcada como `aria-hidden` y respeto a `prefers-reduced-motion`.
- **Carga**: la primera obra entra de inmediato y el resto en diferido; las imágenes
  declaran sus medidas para que la página no dé saltos al cargar.

## Estructura

```
index.html                     La página entera: HTML, CSS, JS y gráficos del fondo
imagenes/                      Las obras ya procesadas y listas para publicar
herramientas/
  └── procesar-fotos.py        Originales → versiones web limpias de metadatos
```

## Añadir obras nuevas

```bash
# 1. dejar los originales en "fotos originales/" (no se publica)
py herramientas/procesar-fotos.py
# 2. copiar un bloque <figure class="obra"> en index.html y apuntar al archivo nuevo
```

El script informa de cada foto: medidas de origen y destino, peso final y si traía
coordenadas GPS que se hayan eliminado.

## Pendiente

- [ ] Biografía y subtítulo de la artista
- [ ] Título, año y técnica de cada obra
- [ ] Paleta y tipografía definitivas
- [ ] Generar el QR definitivo con la URL final

## Créditos

Las imágenes de las obras son **© Cecilia Quignón**, publicadas con su autorización.
No pueden reutilizarse sin su permiso.

El código de la página está escrito por [@ArgimiroMF](https://github.com/ArgimiroMF).
