# Data Sources — Drought Monitoring in Panamá’s Arco Seco

This document lists the datasets used to calculate NDVI anomaly, Vegetation Condition Index (VCI), and Standardized Precipitation Index (SPI-1).

---

## MODIS NDVI (Terra MOD13Q1)

- **Source:** NASA LP DAAC (https://lpdaac.usgs.gov/)
- **Product:** MOD13Q1 (16-day composite)
- **Resolution:** 250 m
- **Bands used:** NDVI
- **Temporal coverage:** 2013-02 to 2025-07
- **Processing:**
  - Reprojected to WGS 84 / UTM Zone 17N
  - Clipped to Coclé Province boundary
  - Aggregated to monthly NDVI composites
- **Use in project:**
  - Baseline mean and standard deviation for NDVI anomaly
  - Min–max values for VCI calculation

---

## CHIRPS Precipitation

- **Source:** Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS)  
  https://www.chc.ucsb.edu/data/chirps
- **Product:** CHIRPS v2.0 daily
- **Resolution:** ~0.05° (~5 km)
- **Temporal coverage:** 2013-02 to 2025-06
- **Processing:**
  - Aggregated to monthly totals
  - Resampled to 250 m to match NDVI grid
  - Clipped to Coclé Province boundary
- **Use in project:**
  - Input to SPI-1 calculation

---

## Administrative Boundaries

- **Source:** Instituto Geográfico Nacional Tommy Guardia (IGNTG)
- **Layer:** Corregimientos (sub-districts)
- **Features:** 53 corregimientos in Coclé Province
- **Projection:** WGS 84 / UTM Zone 17N
- **Use in project:**
  - Zonal statistics for NDVI anomaly, VCI, SPI-1

---

## Data Integration

- Zonal statistics generated for **each month** in the study period, producing a time-series dataset (`zonalstats` table) with one record per corregimiento per month.
- Database: PostGIS
- BI tool: Power BI
