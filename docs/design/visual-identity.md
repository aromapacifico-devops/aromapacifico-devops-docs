# Visual identity of the three applications

This document defines the visual identity of the three applications of the pilot, the farmer application, the carrier application and the public lookup of a sack. It sets the brand, its versions, the colors, the type and the tokens that the [design system](design-system.md) applies to every screen. The source is the design file [AromaPacifico in Figma](https://www.figma.com/design/sFAlRb7c5pxXKsQK7ZRub0/AromaPacifico), and the PDF files of this folder are exports of it.

## Contents

1. Context and goals
2. The brand
3. Color system
4. Type system
5. Tokens
6. Components and screens
7. Deliverables
8. Pending confirmations

## 1. Context and goals

The brand manual of 2020 is outdated. It did not consider real-time telemetry, drone inspection, sack custody or the field work of 2026, so the pilot gets an identity of its own.

The identity serves three channels.

1. The farmer application is used on farms in full daylight. It needs high contrast, short sentences and few figures, for a farmer who trusts the notebook more than an application.
2. The carrier application is used on the road and next to the truck, with one hand. It needs large buttons within reach of the thumb, a quick reading of the progress of the load, and work with no data.
3. The public lookup of the buyer opens when the QR code of the sack is scanned, with no account and mostly from a phone. It shows origin, the dates of the journey and the drying, and nothing more.

## 2. The brand

### 2.1. Isotype and logotype

The current brand is the one drawn in the design file, on the slide `Slide 16:9 - 1`.

- The isotype is three intertwined flames of steam that rise like the aroma of a cup, in red `#8C0303`, blue `#0378A6` and gold `#F29F05`.
- The logotype is the word AROMA PACIFICO on two lines, in Outfit Black and in black, beside the isotype.

| Flame | Color | Meaning |
|---|---|---|
| Red | `#8C0303` | Roast and land of origin |
| Gold | `#F29F05` | Andean sun and the quality seal of the bean |
| Blue | `#0378A6` | Sea of Buenaventura and telemetry signal |

The version with waves, red, orange and blue at the foot of the slide, is the graphic motif of the brand. It appears in the header of the buyer lookup as a band of three colors.

### 2.2. Versions of the logo

| Version | Rule | Component in the design file |
|---|---|---|
| Main, in color | Isotype in its three colors and the word in black, on white or on `surface/canvas` | `Logo/Principal` |
| One ink | Isotype and word in black `#111111`, with no halftones. For fique sacks, thermal scale receipts and stamps of the collection centers | `Logo/Una tinta` |
| Negative | Isotype and word in white on the dark background `#161412`. The red `#8C0303` on that background gives about 2 to 1, so the flames do not keep their colors | `Logo/Negativo` |

The three versions live on the slide of logo versions of the design file, and the SVG of each one is exported from its component.

### 2.3. Clear space and minimum sizes

| Element | Rule |
|---|---|
| Clear space | A free margin around the logo equal to the height of one flame of the isotype. No element enters it |
| Isotype | 20 by 20 pixels on a phone and 16 by 16 pixels as a favicon |
| Full logo | 110 pixels wide on screen and 40 mm in print on sacks |

## 3. Color system

Direct sunlight reduces the perceived contrast, so the text of the applications uses inks of AAA contrast, 7 to 1 or more. The ratios of this document come from the WCAG 2.2 formula.

### 3.1. Brand and action

| Token | Hexadecimal | Contrast on white | Use |
|---|---|---|---|
| `brand/red` | `#8C0303` | 9.9 to 1, AAA | Brand. It is never a button color, so it is never confused with an alert |
| `brand/pacific` | `#0378A6` | 5.0 to 1, AA | Telemetry and connectivity |
| `brand/sun` | `#F29F05` | 2.2 to 1 | Accent and quality seal. Graphic only, never text |
| `action/primary` | Alias of `brand/pacific` | 5.0 to 1 with white text | Primary buttons, links and focus |

### 3.2. Surfaces and text

| Token | Hexadecimal | Contrast on `surface/canvas` | Use |
|---|---|---|---|
| `surface/canvas` | `#FBF9F5` | Base | Warm daytime background that reduces glare |
| `surface/card` | `#FFFFFF` | Base | Cards, with a 1 pixel border |
| `surface/muted` | `#F5F2EB` | Base | Secondary sections and status bars |
| `surface/border` | `#E7E5E4` | Does not apply | Dividers and borders |
| `text/primary` | `#161412` | 17.5 to 1, AAA | Main text |
| `text/secondary` | `#44403C` | 9.8 to 1, AAA | Labels and metadata |
| `text/muted` | `#78716C` | 4.6 to 1, AA | Microcopy. Never for critical information |
| `text/inverse` | `#FFFFFF` | Does not apply | Text on dark or action backgrounds |

Warm neutrals fill almost the whole screen, about 95 percent, and the brand and semantic colors only signal, about 5 percent.

### 3.3. Sack states

The seven states of a sack, defined in `docs/traceability/sack-states.md`, group into four badges.

| State | Badge | Fill | Border | Text |
|---|---|---|---|---|
| `in_preparation` | In preparation | `#F5F5F4` | `#D6D3D1` | `#44403C` |
| `in_transit_to_center`, `in_transit_to_port` | In transit | `#E0F2FE` | `#BAE6FD` | `#0369A1` |
| `at_center_accepted`, `delivered_accepted` | Accepted | `#DCFCE7` | `#BBF7D0` | `#15803D` |
| `at_center_rejected`, `delivered_rejected` | Rejected | `#FEE2E2` | `#FECACA` | `#991B1B` |

### 3.4. Crop and drying alerts

| Level | Fill | Border | Text | Behavior |
|---|---|---|---|---|
| Normal | `#F0FDF4` | `#86EFAC` | `#166534` | "Tu cultivo está dentro del rango", the crop is within range |
| Preventive | `#FFFBEB` | `#FCD34D` | `#92400E` | A reading outside the agronomic range |
| Urgent | `#FEF2F2` | `#DC2626`, 2 pixels | `#991B1B` | Grain above 40 degrees, "Actúa ahora". A high priority band that stays visible in the sun |

The alert red, `#DC2626` and `#991B1B`, is reserved for the urgent alert and the rejected badge.

## 4. Type system

| Role | Family | Fallback |
|---|---|---|
| Brand and interface, in the three applications and the web lookup | Outfit, bundled with the applications so it does not depend on the network | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` |
| Codes and figures, such as sack codes, weights, temperatures, humidity and coordinates | Roboto Mono with tabular figures | `ui-monospace, "SF Mono", Menlo, Consolas, monospace` |

Weights are Black for the brand name and the origin headings, SemiBold for titles, Medium for labels and Regular for body text.

| Style in the design file | Font | Size and line height | Tracking | Use |
|---|---|---|---|---|
| `text/display-origin` | Outfit Black | 38 / 44 | minus 2 percent | Origin in the buyer lookup |
| `text/title-screen` | Outfit SemiBold | 24 / 32 | minus 2 percent | Screen title |
| `text/title-card` | Outfit SemiBold | 18 / 24 | minus 1 percent | Heading of a card or lot |
| `text/body-base` | Outfit Regular | 16 / 24 | 0 | Descriptive sentences |
| `text/body-bold` | Outfit SemiBold | 16 / 24 | 0 | Data chosen by touch |
| `text/caption` | Outfit Medium | 13 / 18 | plus 2 percent | Relative time stamps |
| `text/data-mono` | Roboto Mono Bold | 15 / 20 | plus 4 percent | Sack code, such as `AP-7K3M-Q29X-TDHB-6` |

The minimum text size is 16 pixels in the body and 13 pixels only for time stamps.

## 5. Tokens

The tokens are variables of the design file, in the collections Color, Espaciado and Radio. The block below serves Tokens Studio or the generation of variables in code, and `tools/design_system.py` reads it to check the design system.

```json
{
  "color": {
    "brand": {
      "red": { "value": "#8C0303", "type": "color", "description": "Roast and land of origin" },
      "pacific": { "value": "#0378A6", "type": "color", "description": "Pacific and telemetry" },
      "sun": { "value": "#F29F05", "type": "color", "description": "Andean sun, graphic only" }
    },
    "action": {
      "primary": { "value": "{color.brand.pacific}", "type": "color", "description": "Primary action" }
    },
    "surface": {
      "canvas": { "value": "#FBF9F5", "type": "color" },
      "card": { "value": "#FFFFFF", "type": "color" },
      "muted": { "value": "#F5F2EB", "type": "color" },
      "border": { "value": "#E7E5E4", "type": "color" }
    },
    "text": {
      "primary": { "value": "#161412", "type": "color", "description": "17.5:1 on canvas" },
      "secondary": { "value": "#44403C", "type": "color", "description": "9.8:1 on canvas" },
      "muted": { "value": "#78716C", "type": "color", "description": "4.6:1 on canvas" },
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

## 6. Components and screens

### 6.1. Common rules

| Subject | Rule |
|---|---|
| Size | Phone at 390 by 844, and the same layout at 360 by 800. The buyer web is phone first, with a desktop layout at 1440 |
| Touch area | At least 48 by 48 pixels. The main actions of the carrier sit in the lower third |
| Cards | Fill `surface/card`, 1 pixel border `surface/border` and radius 14 (`radius/lg`). Badges are pills (`radius/full`) |
| Buttons | The primary button uses `action/primary` with white text. The destructive button, such as ending a drying, has a `#991B1B` border on white and always asks for a confirmation |
| No connection | Every screen shows a fixed bar with the last update, such as "Actualizado el martes a las 6:10", or the pending send, "Se enviará cuando el teléfono tenga datos" |
| Time | Colombia time, UTC minus 5, in a human form such as "Hace 40 min" |

### 6.2. Components in the design file

`Badge/Estado` with 4 variants, `Botón` with primary, secondary and destructive, `Alerta` with normal, preventive and urgent, `Barra/Pestañas` with 4 variants, `Barra/Sin datos` with 3 variants, and `Fila/Saco`. The design system adds the field component.

### 6.3. Screens

| View | Screens | Functional source |
|---|---|---|
| Farmer | Farm, farm with a variable out of range, the numbers, drying with no lot, drying with an urgent alert, confirm the end of drying, alerts, register a sack | `docs/iot/farmer-history.md` |
| Carrier | Open trip, scanner, arrival at the center, delivery at the port in three steps, reminder after 10 hours, no data and tasks, paused trip | `docs/traceability/carrier-application-contract.md` |
| Buyer | Result on a phone, result on a desktop, rejected, code not registered, write the code | `docs/traceability/actor-views.md`, `docs/traceability/public-query.md` |

The values on the screens, such as lots, receivers, receipts, sack codes and readings, are examples. The copy of the screens is in Spanish, the language of the applications.

## 7. Deliverables

| Deliverable | Where |
|---|---|
| Design file | Figma file `sFAlRb7c5pxXKsQK7ZRub0` |
| Branding slides | The first page of the design file, with cover, rationale, palette, sack states, alerts and type, the three views, and the logo versions |
| Mockups, components and tokens | The page of mockups of the three views, and the collections of variables and text styles of the design file |
| PDF exports | `docs/design/aroma-pacifico-branding.pdf`, `farmer-views.pdf`, `carrier-views.pdf` and `buyer-views.pdf` |

## 8. Pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The screens of the design file link to its variables, since the mockups still hold fixed values | Design owner | A change of a token must be repeated by hand on each screen |
| The buyer lookup in Spanish and English, with an ES and EN switch | Federation | The switch is removed and the lookup stays in Spanish |
