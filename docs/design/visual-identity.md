# Identidad Visual del Sistema Propio 2026 — AromaPacífico (E7-07)

> **Especificación de la identidad visual de las tres aplicaciones del piloto.**
> **Proyecto:** AromaPacífico – DevOps & IoT Platform (Cauca, Huila, Tolima, Buenaventura).
> **Issue:** [`aromapacifico-devops-docs#56`](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/56) · **Épica:** E7 (Costo y Sistema de Diseño) · **Responsable:** Daniel Mejía (`Dearxia1`, Senior).
> **Desbloquea a:** [`aromapacifico-devops-docs#57`](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/57) (`[E7-08] Definir tokens y aplicar sistema a las tres vistas`, Isabella Hernández).
> **Figma:** [AromaPacifico](https://www.figma.com/design/sFAlRb7c5pxXKsQK7ZRub0/AromaPacifico) · **PDFs en el repo:** `docs/design/`.

---

## 1. Contexto y objetivos

El manual de marca de 2020 quedó obsoleto: no consideraba la telemetría en tiempo real, la inspección con drones, la custodia de sacos ni el trabajo en campo de 2026.

La identidad responde a tres canales:
1. **App del caficultor.** Se usa en fincas a plena luz del día. Exige contraste alto, frases cortas y números un toque más abajo, para quien confía más en su cuaderno que en una aplicación.
2. **App del transportador.** Se usa en carretera y junto al camión, con una mano. Pide botones grandes en la zona del pulgar, lectura rápida del avance de la carga y funcionamiento sin datos.
3. **Consulta pública del comprador.** Se abre al escanear el QR del saco, sin cuenta, sobre todo desde el teléfono. Transmite origen, fechas del recorrido y secado, y nada más.

## 2. La marca

### 2.1. Isotipo y logotipo

La marca vigente es la que está dibujada en el archivo de Figma (slide `Slide 16:9 - 1`):

- **Isotipo:** tres llamas de vapor entrelazadas que suben como el aroma de una taza. Los colores son rojo (`#8C0303`), azul (`#0378A6`) y dorado (`#F29F05`).
- **Logotipo:** la palabra **AROMA PACIFICO** en dos líneas, en Outfit Black y en negro, junto al isotipo.

| Llama | Color | Significado |
|---|---|---|
| Roja | `#8C0303` | Tueste y tierra de origen |
| Dorada | `#F29F05` | Sol andino y sello de calidad del grano |
| Azul | `#0378A6` | Mar de Buenaventura y señal de telemetría |

La versión con ondas (rojo, naranja y azul al pie del slide) es el motivo gráfico de la marca. Aparece en la cabecera del portal del comprador como una franja de tres colores.

### 2.2. Versiones del logotipo

| Versión | Regla | Estado |
|---|---|---|
| **Principal (color)** | Isotipo en sus tres colores y palabra en negro, sobre fondo blanco o `surface/canvas`. Componente `Logo/Principal` | Hecha en Figma |
| **Una tinta** | Isotipo y palabra en negro `#111111`, sin semitonos. Para costales de fique, recibos térmicos de báscula y sellos de acopio. Componente `Logo/Una tinta` | Hecha en Figma |
| **Negativa** | Isotipo y palabra en blanco sobre fondo oscuro `#161412`. El rojo `#8C0303` sobre ese fondo solo da cerca de 2:1, así que las llamas no conservan sus colores. Componente `Logo/Negativo` | Hecha en Figma |

Las tres están en el slide `Branding 7 — Versiones del logotipo`. Los SVG se exportan desde cada componente en Figma.

### 2.3. Área de reserva y tamaños mínimos

- **Área de reserva:** un margen libre alrededor del logotipo igual a la altura de una llama del isotipo. Ningún elemento puede invadirla.
- **Isotipo:** 20 × 20 px en teléfono y 16 × 16 px como favicon.
- **Logotipo completo:** 110 px de ancho en pantalla y 40 mm en impresión sobre sacos.

## 3. Sistema cromático

Bajo sol directo el reflejo reduce el contraste percibido, así que el texto de las aplicaciones usa tintas de contraste AAA (7:1 o más). Los ratios de esta nota se calcularon con la fórmula WCAG 2.2.

### 3.1. Marca y acción

| Token | HEX | Contraste sobre blanco | Uso |
|---|---|---|---|
| `brand/red` | `#8C0303` | 9.9:1 (AAA) | Marca. **No se usa como color de botón**, para no confundirse con la alerta |
| `brand/pacific` | `#0378A6` | 5.0:1 (AA) | Telemetría y conectividad |
| `brand/sun` | `#F29F05` | 2.2:1 | Acento y sello de calidad. **Solo gráfico**, nunca texto |
| `action/primary` | alias de `brand/pacific` | 5.0:1 con texto blanco | Botones primarios, enlaces y foco |

### 3.2. Superficies y texto

| Token | HEX | Contraste sobre `surface/canvas` | Función |
|---|---|---|---|
| `surface/canvas` | `#FBF9F5` | Base | Fondo diurno cálido, anti-reflejo |
| `surface/card` | `#FFFFFF` | Base | Tarjetas, con borde de 1 px |
| `surface/muted` | `#F5F2EB` | Base | Secciones secundarias y barras de estado |
| `surface/border` | `#E7E5E4` | — | Divisores y bordes |
| `text/primary` | `#161412` | 17.5:1 (AAA) | Texto principal |
| `text/secondary` | `#44403C` | 9.8:1 (AAA) | Etiquetas y metadatos |
| `text/muted` | `#78716C` | 4.6:1 (AA) | Microcopia. No para información crítica |
| `text/inverse` | `#FFFFFF` | — | Texto sobre fondos oscuros o de acción |

**Regla 95/5.** Los neutros cálidos ocupan casi toda la pantalla. El color de marca y los colores semánticos solo señalan.

### 3.3. Estados del saco

Los 7 estados lógicos del saco (ver `docs/traceability/sack-states.md`) se agrupan en 4 badges:

| Estado lógico | Badge | Fondo | Borde | Texto |
|---|---|---|---|---|
| `in_preparation` | En preparación | `#F5F5F4` | `#D6D3D1` | `#44403C` |
| `in_transit_to_center`, `in_transit_to_port` | En tránsito | `#E0F2FE` | `#BAE6FD` | `#0369A1` |
| `at_center_accepted`, `delivered_accepted` | Aceptado | `#DCFCE7` | `#BBF7D0` | `#15803D` |
| `at_center_rejected`, `delivered_rejected` | Rechazado | `#FEE2E2` | `#FECACA` | `#991B1B` |

### 3.4. Alertas de cultivo y secado

| Nivel | Fondo | Borde | Texto | Comportamiento |
|---|---|---|---|---|
| Normal | `#F0FDF4` | `#86EFAC` | `#166534` | "Tu cultivo está dentro del rango" |
| Preventiva | `#FFFBEB` | `#FCD34D` | `#92400E` | Lectura fuera de rango agronómico |
| Urgente | `#FEF2F2` | `#DC2626` (2 px) | `#991B1B` | Grano sobre 40 °C: "Actúa ahora". Banda de alta prioridad, visible al sol |

El rojo de alerta (`#DC2626` y `#991B1B`) está reservado a la alerta urgente y al badge Rechazado.

## 4. Sistema tipográfico

- **Familia de marca:** **Outfit**, para las tres aplicaciones y la consulta web. Va incluida en las aplicaciones y no depende de la red. Si no carga, la respaldan `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`.
- **Monoespaciada:** **Roboto Mono**, con respaldo `ui-monospace, "SF Mono", Menlo, Consolas, monospace` y cifras tabulares. Todo código de saco, peso, temperatura, humedad o coordenada la lleva.
- **Pesos:** Black para el nombre de marca y los titulares de origen, SemiBold para títulos, Medium para etiquetas y Regular para el cuerpo.

| Estilo en Figma | Fuente | Tamaño / interlineado | Tracking | Uso |
|---|---|---|---|---|
| `text/display-origin` | Outfit Black | 38 / 44 | −2 % | Origen en la consulta del comprador |
| `text/title-screen` | Outfit SemiBold | 24 / 32 | −2 % | Título de pantalla |
| `text/title-card` | Outfit SemiBold | 18 / 24 | −1 % | Encabezado de tarjeta o lote |
| `text/body-base` | Outfit Regular | 16 / 24 | 0 | Frases descriptivas |
| `text/body-bold` | Outfit SemiBold | 16 / 24 | 0 | Datos de selección táctil |
| `text/caption` | Outfit Medium | 13 / 18 | +2 % | Marcas de tiempo relativas |
| `text/data-mono` | Roboto Mono Bold | 15 / 20 | +4 % | Código de saco: `AP-7K3M-Q29X-TDHB-6` |

Texto mínimo: 16 px en el cuerpo y 13 px solo en marcas de tiempo.

## 5. Tokens (`tokens.json`)

Están definidos como variables en Figma (colecciones **Color**, **Espaciado** y **Radio**). Este JSON sirve para Tokens Studio o para generar variables en código.

```json
{
  "color": {
    "brand": {
      "red": { "value": "#8C0303", "type": "color", "description": "Tueste y tierra de origen" },
      "pacific": { "value": "#0378A6", "type": "color", "description": "Pacífico y telemetría" },
      "sun": { "value": "#F29F05", "type": "color", "description": "Sol andino, solo gráfico" }
    },
    "action": {
      "primary": { "value": "{color.brand.pacific}", "type": "color", "description": "Acción primaria" }
    },
    "surface": {
      "canvas": { "value": "#FBF9F5", "type": "color" },
      "card": { "value": "#FFFFFF", "type": "color" },
      "muted": { "value": "#F5F2EB", "type": "color" },
      "border": { "value": "#E7E5E4", "type": "color" }
    },
    "text": {
      "primary": { "value": "#161412", "type": "color", "description": "17.5:1 sobre canvas" },
      "secondary": { "value": "#44403C", "type": "color", "description": "9.8:1 sobre canvas" },
      "muted": { "value": "#78716C", "type": "color", "description": "4.6:1 sobre canvas" },
      "inverse": { "value": "#FFFFFF", "type": "color" }
    },
    "status": {
      "in-preparation": { "bg": { "value": "#F5F5F4", "type": "color" }, "border": { "value": "#D6D3D1", "type": "color" }, "text": { "value": "#44403C", "type": "color" } },
      "in-transit": { "bg": { "value": "#E0F2FE", "type": "color" }, "border": { "value": "#BAE6FD", "type": "color" }, "text": { "value": "#0369A1", "type": "color" } },
      "accepted": { "bg": { "value": "#DCFCE7", "type": "color" }, "border": { "value": "#BBF7D0", "type": "color" }, "text": { "value": "#15803D", "type": "color" } },
      "rejected": { "bg": { "value": "#FEE2E2", "type": "color" }, "border": { "value": "#FECACA", "type": "color" }, "text": { "value": "#991B1B", "type": "color" } }
    },
    "alert": {
      "normal": { "bg": { "value": "#F0FDF4", "type": "color" }, "border": { "value": "#86EFAC", "type": "color" }, "text": { "value": "#166534", "type": "color" } },
      "warning": { "bg": { "value": "#FFFBEB", "type": "color" }, "border": { "value": "#FCD34D", "type": "color" }, "text": { "value": "#92400E", "type": "color" } },
      "urgent": { "bg": { "value": "#FEF2F2", "type": "color" }, "border": { "value": "#DC2626", "type": "color" }, "text": { "value": "#991B1B", "type": "color" } }
    }
  },
  "space": {
    "xs": { "value": "4", "type": "spacing" },
    "sm": { "value": "8", "type": "spacing" },
    "md": { "value": "16", "type": "spacing" },
    "lg": { "value": "24", "type": "spacing" },
    "xl": { "value": "32", "type": "spacing" }
  },
  "radius": {
    "sm": { "value": "6", "type": "borderRadius" },
    "md": { "value": "10", "type": "borderRadius" },
    "lg": { "value": "14", "type": "borderRadius" },
    "full": { "value": "9999", "type": "borderRadius" }
  }
}
```

## 6. Componentes y pantallas

### 6.1. Reglas comunes

- **Móvil:** 390 × 844 y debe funcionar igual en 360 × 800. **Web del comprador:** móvil primero y escritorio 1440.
- **Área táctil mínima:** 48 × 48 px. Las acciones principales del transportador van en el tercio inferior.
- **Cards:** fondo `surface/card`, borde `surface/border` de 1 px y radio 14 (`radius/lg`). Los badges, en píldora (`radius/full`).
- **Botón primario:** `action/primary` con texto blanco. **Botón destructivo** ("Terminar secado"): borde `#991B1B` sobre blanco y siempre con confirmación.
- **Sin conexión:** toda pantalla muestra una barra fija con "Actualizado el martes a las 6:10" o "Se enviará cuando el teléfono tenga datos".
- **Hora:** Colombia (UTC−5), en formato humano ("Hace 40 min").

### 6.2. Componentes en Figma

`Badge/Estado` (4 variantes), `Botón` (primario, secundario y destructivo), `Alerta` (normal, preventiva y urgente), `Barra/Pestañas` (4 variantes), `Barra/Sin datos` (3 variantes) y `Fila/Saco`.

### 6.3. Pantallas

| Vista | Pantallas | Fuente funcional |
|---|---|---|
| **Caficultor** | C1 Finca · C2 Finca con variable fuera de rango · C3 Los números · C4 Secado sin lote · C5 Secado con alerta urgente · C6 Confirmar terminar secado · C7 Alertas · C8 Registrar saco | `docs/iot/farmer-history.md` |
| **Transportador** | T1 Viaje abierto · T2 Escáner · T3 Llegada al centro · T4 Entrega en puerto (3 pasos) · T5 Recordatorio de 10 h · T6 Sin datos y tareas · T7 Viaje en pausa | `docs/traceability/carrier-application-contract.md` |
| **Comprador** | B1 Resultado móvil · B2 Resultado en escritorio · B3 Rechazado · B3 Código no registrado · B4 Escribir el código | `docs/traceability/actor-views.md`, `public-query.md` |

Los valores de las pantallas (lote, receptor, recibo, códigos de saco y lecturas) son ejemplos.

## 7. Entregables

| Entregable | Dónde |
|---|---|
| Archivo de diseño | Figma `sFAlRb7c5pxXKsQK7ZRub0` |
| Slides de branding (7) | Página 1: portada, racional, paleta, estados del saco, alertas y tipografía, tres vistas, versiones del logotipo |
| Mockups, componentes y tokens | Página "Mockups — tres vistas", y colecciones de variables y estilos de texto del archivo |
| PDFs | `docs/design/aroma-pacifico-branding.pdf`, `farmer-views.pdf`, `carrier-views.pdf`, `buyer-views.pdf` |

## 8. Pendientes y decisiones

| Pendiente | Responsable |
|---|---|
| Confirmar `action/primary` en azul y que el rojo queda solo para marca y peligro | Isabella (E7-08) |
| Enlazar las pantallas a las variables de Figma | Isabella (E7-08) |
| Elegir el set de iconos. Los mockups usan trazos de 2 px, estilo Lucide | Isabella (E7-08) |
| Consulta del comprador en español e inglés, con conmutador ES / EN | Federación |
