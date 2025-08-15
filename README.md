# Drought Monitoring in Panamá’s Arco Seco (Cocle) — Multi-Index Analysis (2013–2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)
![Status](https://img.shields.io/badge/Status-Completed-blue)
![Made with: ArcGIS | PostGIS | Power BI](https://img.shields.io/badge/Tools-ArcGIS%20%7C%20PostGIS%20%7C%20Power%20BI-informational)

**Objective.** Build an operational pipeline to monitor drought and vegetation condition at **corregimiento** level in **Cocle, Panama**, using **NDVI anomaly** (MODIS), **VCI**, and **SPI-1** (CHIRPS) with reproducible GIS/DB/BI steps.

---

## Overview

- **Study area:** Cocle Province (Panama)  
- **Period:** 2013–2025; 2023–2025 for SPI-1, NDVI anomaly & VCI dashboards  
- **Spatial unit:** Corregimientos (53)  
- **Indicators:**
  - **NDVI anomaly:** Current NDVI vs historical baseline (2013–2022)
  - **VCI:** NDVI normalized to historical min–max (0–100)
  - **SPI-1:** 1-month Standardized Precipitation Index from CHIRPS

This repo includes **scripts**, **schema**, and **images** of the **Power BI** dashboards and **infographic**.

---

## Repository map

- `data/` — metadata, sample rasters, and demo `zonalstats` subset  
- `code/` — ArcGIS geoprocessing scripts, PostGIS SQL, and Power BI DAX notes  
- `reports/` — infographic (16:9), dashboard screenshots, Panama map highlighting Coclé  

---

## Method (condensed)

1. **Data ingestion**
   - MODIS NDVI (250 m); CHIRPS (~5 km resampled to 250 m).
2. **Preprocessing**
   - Reprojection, resampling (CHIRPS → 250 m), and clipping to AOI.
3. **Indices**
   - **NDVI anomaly:** z-score vs 2013–2022 baseline (σ>0.1 mask to ensure stability).
   - **VCI:** `(NDVI − NDVI_min)/(NDVI_max − NDVI_min) × 100`.
   - **SPI-1:** Fitted gamma → standardized (monthly).
4. **Zonal statistics**
   - Mean per corregimiento per month for NDVI anomaly, VCI, SPI-1.
5. **Database**
   - PostGIS table with **duplicated geometries per month** → time-enabled exports.
6. **BI**
   - Power BI model with measures:
     - **Color hex** and **labels** for SPI/NDVI/VCI
     - **Composite index** + label for the overview page
   - Pages: SPI, NDVI anomaly, VCI, and **front page** integration.

---

## Data dictionary (zonalstats)

| Field          | Type    | Description                                |
|----------------|---------|--------------------------------------------|
| corregimie     | text    | Corregimiento name                         |
| fecha          | date    | Year-month (YYYY-MM-01)                    |
| spi_1          | float   | Standardized Precipitation Index (1-month) |
| ndvi_anom      | float   | NDVI anomaly (clamped to [−1, +1])         |
| vci            | float   | Vegetation Condition Index (0–100)         |

See `data/metadata/dictionary_zonalstats.csv` for full details.

---

## Key visuals

> All images are in `reports/images/`. Use alt text for accessibility.

- **Infographic (16:9):** `infographic_16x9.png`  
- **Front page (composite):** `dashboard_frontpage.png`  
- **SPI page:** `dashboard_spi_page.png`  
- **NDVI anomaly page:** `dashboard_ndvi_page.png`  
- **VCI page:** `dashboard_vci_page.png`  
- **Panamá (Coclé highlighted):** `panama_cocle_highlight.png`

<details>
<summary>Preview</summary>

![Infographic overview](reports/images/infographic_16x9.png "Infographic: objectives, data, methods, and findings")

</details>

---

## Reproducibility (scripts)

- **ArcGIS** (`code/arcgis/`): clipping, resampling, zonal statistics.
- **PostGIS** (`code/postgis/`): schema, loading, geometry join per month.
- **Power BI** (`code/powerbi/dax_measures.md`): SPI/NDVI/VCI color hex, labels, composite index.

> Note: Large rasters are not tracked here. Use the sample files in `data/samples/`.

---

## How to cite

If you reference this repository:

```bibtex
@misc{tamir_arco_seco_2025,
  title   = {Drought Monitoring in Panamá’s Arco Seco (Cocle) — Multi-Index Analysis (2013–2025)},
  author  = {Tamir, Chong},
  year    = {2025},
  url     = {https://github.com/<your-user>/arco-seco-drought-monitoring}
}
```
