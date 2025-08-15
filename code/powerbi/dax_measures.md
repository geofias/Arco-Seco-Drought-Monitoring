# Power BI DAX Measures — Drought Monitoring Project

This file lists DAX measures used for color formatting, category labeling, and percentage calculations for SPI, NDVI anomaly, and VCI.

---

## SPI

```DAX
SPI_Med =
    MEDIAN ( 'public zonalstats_powerbi'[spi_1] )

SPI_Color_Hex =
VAR v = [SPI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= -2, "#8B0000",       -- Dark Red
    v <= -1.5, "#FF0000",     -- Red
    v <= -1, "#FFA500",       -- Orange
    v <= 1, "#FFFF00",        -- Yellow
    v <= 1.5, "#90EE90",      -- Light Green
    v <= 2, "#008000",        -- Green
    "#0000FF"                 -- Blue
)

SPI_Color_Label =
VAR v = [SPI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= -2, "Extreme drought",
    v <= -1.5, "Severe drought",
    v <= -1, "Moderate drought",
    v <= 1, "Near normal",
    v <= 1.5, "Moderately wet",
    v <= 2, "Very wet",
    "Extremely wet"
)

SPI_Percentage =
VAR total = CALCULATE ( COUNTROWS ( 'public zonalstats_powerbi' ), ALL ( 'public zonalstats_powerbi' ) )
VAR thisCat = COUNTROWS ( 'public zonalstats_powerbi' )
RETURN
DIVIDE ( thisCat, total, 0 )
```
---

## NDVI Anomaly

```DAX
NDVI_Med =
    MEDIAN ( 'public zonalstats_powerbi'[ndvi_anom] )

NDVI_Color_Hex =
VAR v = [NDVI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= -0.5, "#8B0000",       -- Dark Red (very low vegetation)
    v <= -0.25, "#FF0000",      -- Red
    v < 0, "#FFA500",           -- Orange
    v <= 0.25, "#FFFF00",       -- Yellow
    v <= 0.5, "#90EE90",        -- Light Green
    v <= 1, "#008000",          -- Green
    "#0000FF"                   -- Blue (unusually high vegetation)
)

NDVI_Color_Label =
VAR v = [NDVI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= -0.5, "Severe vegetation loss",
    v <= -0.25, "Moderate vegetation loss",
    v < 0, "Slight vegetation loss",
    v <= 0.25, "Near normal vegetation",
    v <= 0.5, "Moderately green",
    v <= 1, "Very green",
    "Extremely green"
)
```
---

## VCI

```DAX
VCI_Med =
    MEDIAN ( 'public zonalstats_powerbi'[vci] )

VCI_Color_Hex =
VAR v = [VCI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= 35, "#8B0000",        -- Extreme drought
    v <= 50, "#FF0000",        -- Severe drought
    v <= 65, "#FFA500",        -- Moderate drought
    v <= 75, "#FFFF00",        -- Near normal
    v <= 85, "#90EE90",        -- Moderately wet
    v <= 100, "#008000",       -- Very wet
    "#0000FF"                  -- Extremely wet
)

VCI_Color_Label =
VAR v = [VCI_Med]
RETURN
SWITCH(
    TRUE(),
    ISBLANK(v), BLANK(),
    v <= 35, "Extreme drought",
    v <= 50, "Severe drought",
    v <= 65, "Moderate drought",
    v <= 75, "Near normal",
    v <= 85, "Moderately wet",
    v <= 100, "Very wet",
    "Extremely wet"
)
```
