# Estimación de campañas y costo operativo de drones

Este documento construye el modelo económico verificable de los cinco servicios de drones del piloto AromaPacífico. Separa las decisiones aprobadas de los precios públicos, las estimaciones propias y los valores que requieren cotización. Los totales son presupuestos hipotéticos, no ofertas comerciales. Todos los importes están en USD antes de impuestos y se reproducen con [`tools/campaign_cost.py`](tools/campaign_cost.py).

## 1. Contexto

La historia [E7-04](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/53) pide el costo de una campaña con los cinco servicios, el operador, el desplazamiento y el almacenamiento, además de la cadencia en cosecha y fuera de cosecha. Depende de las decisiones de roles y campañas de [E4-02](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/30), la estimación de cosecha de [E4-07](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/35) y la base de precios de [E7-01](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/50).

El servicio usa tres brigadas de un operador certificado, una por departamento. La Federación conserva la plataforma, los datos y la autorización humana. Una campaña es la ronda programada de una brigada por las fincas de un departamento. Las misiones de confirmación, fumigación y verificación nacen de alertas y no esperan a una campaña.

## 2. Alcance y exclusiones

El total incluye:

- operación del operador certificado, piloto, apoyo de brigada, equipo, mantenimiento, seguros, permisos y consumibles no químicos;
- distancia, vehículo/combustible, viáticos, transporte de equipo, movilización de campaña y visitas adicionales esperadas;
- S3, solicitudes de objetos, transición de clase y Lambda para comprobación de evidencia y ortomosaico;
- los cinco servicios: delimitación, confirmación, fumigación autorizada, verificación y estimación de cosecha.

El total no incluye:

- inferencia o filtro de personas: pertenece a E7-05 y se muestra por separado;
- producto agroquímico, dosis, agua y disposición de sobrantes: faltan producto, área tratada y receta agronómica;
- IVA, aranceles, financiación, descuentos, créditos o reservas;
- costo de supervisores de la Federación, que ya son personal de la organización y no tiene costo incremental aprobado;
- conectividad general, VPN y endpoints ya contabilizados en el costo de plataforma, para evitar doble conteo.

## 3. Auditoría y fuentes

### 3.1 Evidencias revisadas

| Evidencia | Resultado de la revisión |
|---|---|
| PR [#144](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/pull/144), E4-02 | Aprobó operador contratado, tres brigadas, 18 campañas ordinarias/año, 936 misiones el primer año y 756 después. Sin revisiones ni comentarios de PR; fusionado el 10-11-2026. |
| PR [#109](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/pull/109), E4-07 | Aprobó una misión de estimación por finca y cosecha, 100 imágenes/finca como supuesto y resultado sin orden de empaque. Sin revisiones ni comentarios de PR; fusionado el 10-11-2026. |
| PR [#135](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/pull/135), E7-01 | Aprobó USD, `us-east-1`, precios on-demand y valores antes de IVA. Dejó expresamente sin verificar el dron y otros equipos. Sin revisiones ni comentarios de PR; fusionado el 10-11-2026. |
| [`operating-mode.md`](operating-mode.md) | Define los cinco servicios y contiene los antecedentes de USD 5.640/año y USD 1.980/mes de cosecha, sin desglose reproducible. |
| [`roles-permits-and-campaigns.md`](roles-permits-and-campaigns.md) | Fuente aprobada de roles, permisos, campaña frente a alerta y volúmenes. Resuelve quién posee el certificado que `operating-mode.md` aún presenta como pendiente. |
| [`harvest-estimation.md`](harvest-estimation.md) | Fija 200 estimaciones/año, 100 imágenes por misión como supuesto y costos AWS; la inferencia queda fuera de este total. |
| [`tools/flight_frequency.py`](tools/flight_frequency.py) | Fuente ejecutable de frecuencia. Este modelo importa sus constantes y su función `yearly`; no vuelve a escribir los volúmenes. |
| [`fleet-and-harvest-estimates.md`](../adr/fleet-and-harvest-estimates.md) | Decisión aprobada: tres brigadas, cuatro meses de cosecha y unas 9.000 imágenes en cosecha. |
| [`assumptions.md`](../assumptions.md) | Registra TRM, impuestos, brigadas, imágenes y frecuencia como supuestos/decisiones trazables. |
| [`price-basis.md`](../governance/price-basis.md) | Fuente de región, moneda, fecha, impuestos y precios AWS. |
| [`personal-data-and-retention.md`](../security/personal-data-and-retention.md) | Retención aprobada: 90 días en Standard, Glacier Instant Retrieval hasta cinco años y eliminación al quinto año. |

### 3.2 Suficiencia de E7-01

E7-01 sí contiene fuentes oficiales fechadas suficientes para S3 y Lambda, moneda, región y tratamiento fiscal. El 10-11-2026 se volvieron a leer las listas oficiales; sus archivos indican publicación del 09-11-2026 para S3 y del 30-10-2026 para Lambda. E7-01 no es suficiente para valorar la operación física: su criterio de hardware quedó abierto y su cierre dice que el dron requiere cotización de E7-04. Por eso ninguna tarifa de operador, piloto, dron, seguro o permiso se marca como verificada.

### 3.3 Registro de precios y supuestos

Fecha de consulta: **10-11-2026**. Impuestos: **no incluidos**. La tarifa general de IVA del registro aprobado es 19%; se aplica solo como sensibilidad porque no se confirmó qué líneas lo causan.

| Concepto | Cantidad/unidad | Precio unitario, USD | Estado | Fuente y URL | Supuesto usado |
|---|---:|---:|---|---|---|
| S3 Standard, `us-east-1` | GB-mes | 0,023 | Precio verificado | [AWS Price List S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json), publicado 09-11-2026 | Primeros 90 días |
| S3 Glacier Instant Retrieval | GB-mes | 0,004 | Precio verificado | [AWS Price List S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json), publicado 09-11-2026 | Meses 4 a 60 |
| S3 PUT / GET / transición | 1.000 solicitudes | 0,005 / 0,0004 / 0,02 | Precio verificado | [AWS Price List S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json), publicado 09-11-2026 | Un PUT y un GET por imagen; una transición |
| Transferencia de entrada a S3 | GB | 0 | Precio verificado | [Precios de S3](https://aws.amazon.com/s3/pricing/), consulta 10-11-2026 | Egreso no cuantificado; requiere patrón de descarga |
| Lambda | GB-s / millón de solicitudes | 0,0000166667 / 0,20 | Precio verificado | [AWS Price List Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), publicado 30-10-2026 | Sin capa gratuita |
| Imagen | 1 imagen | 3 MB | Decisión aprobada | [`personal-data-and-retention.md`](../security/personal-data-and-retention.md) | Se sustituye por medición del proveedor |
| TRM | COP por USD | 3.269,88 | Decisión aprobada | [Datos abiertos de la Superfinanciera](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3), consulta 10-11-2026 | Solo conversión informativa; el modelo calcula en USD |
| Piloto | hora | 18 / 25 / 35 | Estimación propia | Escenarios conservador/base/alto de este documento | No es salario ni cotización |
| Apoyo de brigada | persona-hora | 12 / 18 / 26 | Estimación propia | Escenarios de este documento | Una persona adicional |
| Uso de equipo | hora de vuelo | 18 / 28 / 42 | Estimación propia | Escenarios de este documento | Amortización operativa, sin afirmar precio de dron |
| Mantenimiento | misión | 8 / 15 / 25 | Estimación propia | Escenarios de este documento | Se suma al uso horario |
| Operador certificado | año, tres brigadas | 6.000 / 9.000 / 13.500 | Estimación propia | Escenarios de este documento | Gestión contractual y cumplimiento, no pilotos |
| Seguros y permisos | año, tres brigadas | 3.000 / 4.500 / 7.000 | Estimación propia | Escenarios de este documento | Se reemplaza con póliza y tasas aplicables |
| Vehículo y combustible | km | 0,18 / 0,25 / 0,35 | Estimación propia | Escenarios de este documento | Distancia media 30 / 45 / 70 km por misión |
| Viático | persona-día | 15 / 25 / 40 | Estimación propia | Escenarios de este documento | Dos personas, prorrateo por horas/8 |
| Transporte de equipo | misión | 5 / 10 / 18 | Estimación propia | Escenarios de este documento | Adicional al costo por km |
| Movilización fija | campaña-departamento | 35 / 60 / 100 | Estimación propia | Escenarios de este documento | Planeación/carga/descarga de la ronda |
| Visita adicional | visita | 35 / 60 / 110 | Estimación propia | Escenarios de este documento | Probabilidad 5% / 10% / 20% |
| Consumibles no químicos | misión | 1 a 12 según servicio | Estimación propia | [`tools/campaign_cost.py`](tools/campaign_cost.py) | Baterías menores, limpieza y material; no agroquímico |
| Operador, dron, póliza y permisos reales | contrato | Pendiente | Valor por cotizar | Proceso de contratación de la Federación | Sustituye las estimaciones anteriores |
| Agroquímico | L o kg tratado | Pendiente | Valor por cotizar | Receta agronómica y proveedor autorizados | Excluido del total |
| Inferencia | imagen | Pendiente E7-05 | Componente separado | E7-05; el antecedente no vinculante es USD 1,75/1.000 imágenes | Excluido del total |

## 4. Supuestos aprobados y decisiones del modelo

| Dato | Valor | Clasificación |
|---|---:|---|
| Fincas / departamentos / brigadas | 200 / 3 / 3 | Definición del piloto y decisión aprobada |
| Cosecha | 4 meses/año | Decisión aprobada |
| Campañas en cosecha | 1 por departamento y mes de cosecha | Definición del piloto |
| Campañas fuera de cosecha | 1 por departamento cada 3 meses | Definición del piloto |
| Campañas ordinarias | 18/año: 6 por departamento | Resultado aprobado |
| Arranque | 1 ronda adicional por departamento durante 2 meses | Decisión aprobada |
| Alertas fuera de cosecha | 25% del ritmo de cosecha | Supuesto de E4-02 |
| Redelimitación posterior | 10% de fincas/año | Supuesto de E4-02 |
| Imágenes en cosecha | 9.000/mes | Decisión aprobada |
| Imagen de área / precisión | 100 / 44,44 | 100 aprobado como supuesto; precisión es el residual reproducible hasta 9.000 |
| Horas por misión | 3 / 1 / 1,5 / 1 / 3,5 | Estimación propia para delimitar/confirmar/fumigar/verificar/estimar |
| Retención | Standard 3 meses; Glacier IR hasta 60 | Decisión aprobada |

## 5. Frecuencia de campañas y misiones

`flight_frequency.py` produce la siguiente frecuencia. La fila fuera de cosecha muestra 24 por redondeo visual; el cálculo anual conserva 2,5 redelimitaciones/mes y por tanto usa 24,5 misiones/mes en años posteriores.

| Servicio | Activación | Mes de cosecha | Mes fuera de cosecha posterior | Primer año | Años posteriores |
|---|---|---:|---:|---:|---:|
| Delimitación geoespacial | Programada | 0 | 2,5 | 200 | 20 |
| Confirmación de focos | Alerta/síntoma | 40 | 10 | 240 | 240 |
| Fumigación autorizada | Alerta confirmada + humano | 25 | 6 | 148 | 148 |
| Verificación posterior | Cierre de fumigación | 25 | 6 | 148 | 148 |
| Estimación de cosecha | Programada | 50 | 0 | 200 | 200 |
| **Total** | | **140** | **24,5** | **936** | **756** |

Una campaña programada transporta delimitaciones, estimaciones y revisión de zonas. Las otras tres clases son misiones por alerta y se ejecutan en el siguiente día de campo disponible. El “periodo económico de campaña” usado en las tablas de costo suma la ronda programada y las alertas atendidas en el mismo departamento/mes, pero esa suma contable no cambia el SLA: las alertas nunca esperan a la campaña.

### Imágenes reconciliadas

| Periodo | Fórmula | Imágenes |
|---|---|---:|
| Mes de cosecha | `50 × 100 + 90 × 44,44` | 9.000 |
| Primer año | cosecha 36.000 + alertas fuera 7.822 + arranque 20.000 | 63.822 |
| Año posterior | cosecha 36.000 + alertas fuera 7.822 + redelimitación 2.000 | 45.822 |

El valor genérico anterior de 1.500 imágenes por mes normal equivale a 12.000 fuera de cosecha. Es un techo razonable en un año posterior, pero no representa los dos meses de arranque, con unas 10.978 imágenes/mes. Este modelo usa las misiones para no ocultar ese pico.

## 6. Modelo de costos

### A. Operación

El operador certificado y seguros/permisos son fijos anuales. Piloto y apoyo de brigada se valoran por horas de cada servicio. Uso de equipo y mantenimiento se separan para mostrar amortización y desgaste. Los consumibles excluyen el producto de fumigación.

### B. Logística

Cada misión consume distancia media por el costo vehículo-km, viáticos prorrateados, transporte de equipo y el valor esperado de una visita adicional. Cada campaña-departamento agrega una movilización fija. No se agrega otro combustible: está incluido en vehículo-km.

### C. Tecnología

Cada imagen genera PUT, GET de verificación, una invocación Lambda de un segundo a 512 MB y almacenamiento por cohorte. Las imágenes pasan a Glacier IR al cuarto mes y vencen al mes 60. Cada estimación agrega cinco minutos de Lambda a 4 GB para el ortomosaico. La entrada de datos cuesta cero; el egreso queda pendiente porque no se conoce cuánto se descarga. VPN, endpoints y KMS ya aparecen en `cloud-cost.md` y no se repiten.

### D. Unidad de costo

El modelo entrega misión por servicio, campaña programada, periodo económico de campaña, departamento, finca, mes y año. “Costo cargado por misión” reparte costos fijos, movilizaciones y tecnología entre todas las misiones del año; no debe sumarse de nuevo al total anual.

## 7. Fórmulas reproducibles

Para servicio `s`, escenario `e`:

```text
operacion_s = horas_s × (piloto_h + apoyo_h + equipo_h)
              + mantenimiento_mision + consumibles_s

logistica_s = distancia_km × vehiculo_km
              + viatico_persona_dia × personas × horas_s / 8
              + transporte_equipo
              + prob_visita_adicional × costo_visita_adicional

costo_variable_s = operacion_s + logistica_s

costo_anual = operador_fijo + seguros_permisos
              + Σ(misiones_s × costo_variable_s)
              + campañas × movilizacion
              + almacenamiento + solicitudes + proceso_evidencia

costo_cargado_s = costo_variable_s
                  + (fijos + movilizaciones + tecnologia) / misiones_anuales
```

El almacenamiento se calcula mes a mes por cohorte:

```text
GB_cohorte = imagenes × 3 / 1024
costo_mes = GB_cohorte × (0,023 si edad < 3 meses; 0,004 si 3 <= edad < 60)
```

La sensibilidad de IVA es `total × 1,19`; COP informativo es `total_USD × 3.269,88`. No se suma inferencia ni agroquímico.

## 8. Escenarios

Los tres escenarios mantienen la frecuencia aprobada y cambian únicamente tarifas, distancia y riesgo de visita adicional. “Conservador” significa menor costo presupuestario, no cotización conservadora de contingencia.

| Entrada | Conservador | Base | Alto |
|---|---:|---:|---:|
| Operador fijo/año | 6.000 | 9.000 | 13.500 |
| Seguros y permisos/año | 3.000 | 4.500 | 7.000 |
| Piloto / apoyo / equipo por hora | 18 / 12 / 18 | 25 / 18 / 28 | 35 / 26 / 42 |
| Mantenimiento/misión | 8 | 15 | 25 |
| Distancia/misión, km | 30 | 45 | 70 |
| Vehículo-km | 0,18 | 0,25 | 0,35 |
| Viático/persona-día | 15 | 25 | 40 |
| Visita adicional | 5% × 35 | 10% × 60 | 20% × 110 |
| Movilización/campaña-departamento | 35 | 60 | 100 |

## 9. Costo por misión, servicio y campaña

### 9.1 Misión base, USD antes de impuestos

| Servicio | Operación | Logística | Variable por misión | Cargado, año posterior |
|---|---:|---:|---:|---:|
| Delimitación | 231,00 | 46,00 | 277,00 | 296,32 |
| Confirmación | 88,00 | 33,50 | 121,50 | 140,82 |
| Fumigación | 129,50 | 36,63 | 166,13 | 185,45 |
| Verificación | 88,00 | 33,50 | 121,50 | 140,82 |
| Estimación | 267,50 | 49,13 | 316,63 | 335,95 |

La fumigación no incluye agroquímico. El costo cargado usa 756 misiones; sirve para precio unitario interno y no para sumar el año otra vez.

### 9.2 Campaña base por departamento

| Tipo | Trabajo programado | Costo directo programado | Periodo económico con alertas y prorrateos |
|---|---|---:|---:|
| Arranque, una ronda de dos meses | 66,67 delimitaciones | 18.526,67 | No comparable con un solo mes |
| Mes de cosecha | 16,67 estimaciones | 5.337,08 | 9.729,71 |
| Fuera de cosecha, año posterior | 3,33 redelimitaciones por ronda | 983,33 | 2.339,34 en el mes de la ronda |

No existe una campaña real con exactamente una misión de cada servicio. Forzar los cinco servicios dentro de cada ronda duplicaría vuelos: delimitación ocurre al inicio o por cambios; confirmación, fumigación y verificación solo ocurren ante alertas. Los cinco sí están costeados en el portafolio anual.

### 9.3 Costo anual base por servicio

| Servicio | Primer año | Año posterior |
|---|---:|---:|
| Delimitación | 55.400,00 | 5.540,00 |
| Confirmación | 29.160,00 | 29.160,00 |
| Fumigación | 24.586,50 | 24.586,50 |
| Verificación | 17.982,00 | 17.982,00 |
| Estimación | 63.325,00 | 63.325,00 |
| Fijos de operador, seguro y permisos | 13.500,00 | 13.500,00 |
| Movilización de campañas | 1.260,00 | 1.080,00 |
| Tecnología sin inferencia | 23,39 | 27,07 |
| **Total** | **205.236,89** | **155.200,57** |

La misma suma clasificada por comportamiento deja USD 13.500,00 fijos en ambos años. El costo variable de misiones es USD 190.453,50 el primer año y USD 140.593,50 después; la movilización variable por campaña es USD 1.260,00 y USD 1.080,00, y la tecnología por uso/retención es USD 23,39 y USD 27,07. No existe otro bloque oculto.

## 10. Proyección mensual, anual y por unidad

### 10.1 Escenario base

| Métrica | Resultado, USD |
|---|---:|
| Mes de arranque, piloto completo | 31.902,70 |
| Mes de arranque por finca | 159,51 |
| Mes de cosecha, piloto completo | 29.189,13 |
| Mes de cosecha por finca | 145,95 |
| Mes fuera de cosecha posterior, promedio | 4.805,51 |
| Mes fuera de cosecha por finca | 24,03 |
| Mes fuera de cosecha del primer año, sin arranque | 4.112,70 |
| Primer año | 205.236,89 |
| Primer año, promedio mensual | 17.103,07 |
| Primer año por departamento | 68.412,30 |
| Primer año por finca | 1.026,18 |
| Año posterior | 155.200,57 |
| Año posterior por departamento | 51.733,52 |
| Año posterior por finca | 776,00 |
| Primer año, COP a TRM aprobada | 671.099.992 COP |
| Año posterior, COP a TRM aprobada | 507.487.249 COP |

Los dos meses de arranque concentran 100 delimitaciones/mes en todo el piloto y por eso se muestran separados del mes normal fuera de cosecha. La suma reproducible es `2 × arranque + 4 × cosecha + 6 × fuera de cosecha = primer año`.

### 10.2 Escenarios anuales

| Escenario | Primer año | Año posterior | Primer año/finca |
|---|---:|---:|---:|
| Conservador | 129.589,29 | 97.555,97 | 647,95 |
| Base | 205.236,89 | 155.200,57 | 1.026,18 |
| Alto | 327.365,39 | 249.039,07 | 1.636,83 |

### 10.3 Tecnología y retención

| Año | Imágenes nuevas | Tecnología anual sin inferencia, USD |
|---|---:|---:|
| 1 | 63.822 | 23,39 |
| 2 | 45.822 | 27,07 |
| 3 | 45.822 | 33,57 |
| 4 | 45.822 | 40,02 |
| 5 | 45.822 | 46,46 |

El crecimiento refleja archivos acumulados, no duplicados. La inferencia pendiente sería `imágenes × tarifa_E7-05` y se reportará al lado, no dentro de estos totales.

## 11. Sensibilidad

### 11.1 Número de misiones, escenario base, año posterior

Los fijos no cambian; los costos variables sí. La campaña y tecnología se mantienen para aislar la sensibilidad operativa.

| Multiplicador | Misiones | Total anual, USD | Cambio frente a base |
|---:|---:|---:|---:|
| 0,75 | 567 | 120.052,20 | -35.148,37 |
| 1,00 | 756 | 155.200,57 | 0 |
| 1,25 | 945 | 190.348,95 | +35.148,38 |
| 1,50 | 1.134 | 225.497,32 | +70.296,75 |

### 11.2 Impuestos y variables pendientes

| Cambio | Efecto |
|---|---|
| IVA de 19% sobre todas las líneas | Base: 244.231,90 primer año y 184.688,68 posterior; es techo, no tratamiento confirmado |
| Duplicar distancia media | Sube `misiones × distancia × vehículo-km`; no cambia operación ni nube |
| Una visita adicional más por cada 10 misiones | Sube `0,10 × costo_visita × misiones` |
| Dos cosechas por finca | Agrega 200 estimaciones, imágenes de área y campañas que la Federación debe calendarizar |
| Más focos | Confirmación escala primero; fumigación/verificación dependen de la tasa de conversión de foco a orden |
| Agroquímico | Suma `área_tratada × dosis × precio_producto`; hoy no cuantificable |

## 12. Reconciliación de cifras anteriores

| Cifra anterior | Comprobación | Decisión |
|---|---|---|
| USD 5.640/año | No tiene desglose ni fórmula. Es menor que `4 × 1.980 = 7.920`, antes de ocho meses fuera de cosecha. | Se rechaza como total operativo. Queda solo como antecedente en `operating-mode.md`. |
| USD 1.980/mes de cosecha | Implica USD 9,90/finca, pero 140 misiones darían USD 14,14 por misión incluyendo brigada, vehículo, equipo, permisos y nube. | No es compatible con los componentes exigidos ni con una tarifa trazable. |
| 1.500 imágenes/mes normal | No proviene de las misiones. En arranque son unas 10.978/mes; luego el promedio modelado es 1.228/mes. | Se usa cálculo por servicio; 1.500 puede conservarse como techo de plataforma posterior. |
| 24 misiones/mes fuera de cosecha | La tabla redondea 2,5 delimitaciones a 2, pero el anual usa 20. | El modelo usa 24,5 y reconcilia 756/año. |
| Quién posee certificado | `operating-mode.md` lo deja abierto; E4-02 posterior elige operador contratado. | Prevalece la decisión fusionada de E4-02. |

## 13. Riesgos y controles

| Riesgo | Consecuencia | Control |
|---|---|---|
| Escenarios confundidos con cotizaciones | Presupuesto usado como compromiso comercial | Etiqueta “estimación propia” y sustitución obligatoria por oferta fechada |
| Un permiso por misión, no por periodo | Más tiempo y costo que el modelo | Validación legal/Aerocivil antes de contratar |
| Distancias rurales mayores | Combustible, viático y días exceden base | Cotizar por departamento con rutas reales |
| Dos cosechas regionales | Estimaciones y campañas adicionales | Confirmar calendario por comité departamental |
| Capacidad inferior a 2,3 misiones/día | Más días, viáticos y retraso | Prueba de ruta durante el arranque |
| Repeticiones por clima, batería o privacidad | Visitas adicionales por encima del 10% base | Medir causal y tasa desde la primera misión |
| Dosis/producto desconocidos | Fumigación subestimada | Mantener el agroquímico fuera del total hasta receta/cotización |
| Descargas desde Glacier | Solicitudes/egreso no modelados | Medir revisiones y agregar costo por recuperación |
| IVA y aranceles | Hasta 19% o más en hardware importado | Validación tributaria y aduanera por línea |

## 14. Criterios de aceptación y verificación

| Criterio de Issue #53 | Evidencia | Estado |
|---|---|---|
| Costo por campaña con cinco servicios, operador, desplazamiento y almacenamiento | Secciones 6, 9 y 10; los cinco se costean sin obligarlos a volar en la misma ronda | Cumplido |
| Cadencia en cosecha y fuera de cosecha | Sección 5, importada del script aprobado | Cumplido |
| Frecuencias reconciliadas | 936 primer año, 756 posteriores, 9.000 imágenes/mes cosecha | Cumplido |
| Sin doble conteo | Inferencia, VPN/endpoints, supervisores y agroquímico se separan | Cumplido |
| Cálculo repetible | Script y pruebas estándar de Python | Cumplido |

Comandos de comprobación:

```powershell
python docs/drones/tools/flight_frequency.py
python docs/drones/tools/campaign_cost.py
python -m unittest discover -s docs/drones/tools -p "test_campaign_cost.py" -v
```

## 15. Decisiones pendientes

| Decisión/dato | Responsable | Sustituye o afecta |
|---|---|---|
| Cotización de operador certificado para tres brigadas, con pilotos, equipos y SLA | Federación / compras | Todos los supuestos de operación |
| Póliza, tasas, alcance y periodicidad real de autorizaciones | Operador y revisión legal | Fijos y tiempo de respuesta |
| Dron elegible, mantenimiento, baterías y vida útil | Operador / proveedor | Equipo por hora y mantenimiento |
| Rutas, km, peajes, noches y viáticos por departamento | Operador / comités | Logística y campañas |
| Producto, dosis, área media tratada e impuestos | Agronomía / proveedor | Costo de fumigación hoy excluido |
| Meses de cosecha y posible cosecha secundaria | Comités departamentales | Estimaciones y campañas |
| Tarifa final de inferencia | E7-05 | Línea separada de procesamiento |
| IVA de AWS, operador y conectividad; aranceles | Federación / asesor tributario | Sensibilidad fiscal |
| Imágenes, tamaños, repetición y descargas reales | Primeras campañas | Nube, visitas y capacidad |

## Fuentes oficiales

- AWS Price List API: [Amazon S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) y [AWS Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), `us-east-1`.
- AWS, [precios de Amazon S3](https://aws.amazon.com/s3/pricing/).
- Aerocivil, [drones y movilidad urbana aérea](https://www.aerocivil.gov.co/preguntas-frecuentes/18/drones-y-movilidad-urbana-aerea/), para categoría específica, certificado de operador y autorización.
- Superintendencia Financiera de Colombia, [TRM en el portal nacional de datos abiertos](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3).
