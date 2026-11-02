# Contratos de prueba (golden cases)

Tres pares de imágenes: contrato original + enmienda. Cada par incluye la lista de
**cambios esperados**, que sirve como referencia para evaluar el sistema.

Fuente: material de prueba del proyecto (Henry, M4). Las enmiendas son **versiones
completas** del contrato con los cambios incorporados, no anexos parciales.

| Caso                        | Archivos                                                  | Tipo de prueba | Cambios esperados |
| --------------------------- | --------------------------------------------------------- | -------------- | ----------------- |
| 1. Licencia de Software     | `documento_1__original.jpg` / `documento_1__enmienda.jpg` | Complejo       | 6                 |
| 2. Servicios de Consultoría | `documento_2__original.jpg` / `documento_2__enmienda.jpg` | Complejo       | 5                 |
| 3. Servicio SaaS            | `documento_3__original.jpg` / `documento_3__enmienda.jpg` | Simple         | 3                 |

---

## Caso 1: Contrato de Licencia de Software

TechNova S.A. (Licenciante) y DataBridge Soluciones S.R.L. (Licenciatario).

| Sección                     | Tipo         | Antes → Después                                                                                                  |
| --------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------- |
| 1. Otorgamiento de Licencia | Modificación | Se elimina "e intransferible" y "únicamente"; "fines internos de la empresa" → "operaciones internas de negocio" |
| 2. Plazo                    | Modificación | 12 meses → 24 meses                                                                                              |
| 3. Pago                     | Modificación | USD 12.000 → USD 15.000                                                                                          |
| 4. Soporte                  | Modificación | Correo electrónico → correo electrónico y chat                                                                   |
| 5. Terminación              | Modificación | 30 días → 60 días de anticipación                                                                                |
| 7. Protección de Datos      | Adición      | Cláusula nueva                                                                                                   |

Sin cambios: 6. Confidencialidad.

> **Nota:** la lista de referencia original no incluía el cambio de la cláusula 1.
> El sistema lo detectó y se verificó contra las imágenes: la licencia deja de ser
> intransferible, un cambio con impacto legal.

## Caso 2: Contrato de Servicios de Consultoría

Orion Consulting Group (Consultor) y GreenWave Energía S.A. (Cliente).

| Sección                  | Tipo         | Antes → Después                    |
| ------------------------ | ------------ | ---------------------------------- |
| 1. Alcance del Servicio  | Modificación | Se agrega "y análisis regulatorio" |
| 2. Duración              | Modificación | 6 meses → 9 meses                  |
| 3. Honorarios            | Modificación | USD 8.000 → USD 9.500 mensuales    |
| 4. Entregables           | Modificación | Reportes mensuales → quincenales   |
| 7. Propiedad Intelectual | Adición      | Cláusula nueva                     |

Sin cambios: 5. Confidencialidad, 6. Legislación Aplicable.

## Caso 3: Contrato de Servicio SaaS

CloudMetrics Ltd. (Proveedor) y RetailPulse S.A. (Cliente).

| Sección                        | Tipo         | Antes → Después                                                       |
| ------------------------------ | ------------ | --------------------------------------------------------------------- |
| 3. Precio                      | Modificación | USD 1.200 → USD 1.250 mensuales                                       |
| 4. Disponibilidad del Servicio | Modificación | 99,5% → 99,9%                                                         |
| 5. Soporte                     | Modificación | Correo electrónico → correo electrónico y sistema de tickets en línea |

Sin cambios: 1. Servicio, 2. Plazo de Suscripción.
Además, la enmienda cambia el título ("Versión actualizada") y el formato (negritas):
el sistema **no** debe reportarlos como cambios.

---

## Resultados de la evaluación

| Caso      | Cambios reales | Detectados    | Falsos positivos |
| --------- | -------------- | ------------- | ---------------- |
| 1         | 6              | 6             | 0                |
| 2         | 5              | 5             | 0                |
| 3         | 3              | 3             | 0                |
| **Total** | **14**         | **14 (100%)** | **0**            |

En los tres casos, `sections_changed` coincidió exactamente con las secciones esperadas.

## Cómo ejecutar un caso

```bash
python -m src.main data/test_contracts/documento_3__original.jpg data/test_contracts/documento_3__enmienda.jpg
```
