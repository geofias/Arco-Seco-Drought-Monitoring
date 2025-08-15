-- Schema for zonal statistics table
CREATE TABLE public.zonalstats (
    corregimie TEXT NOT NULL,
    fecha DATE NOT NULL,
    spi_1 DOUBLE PRECISION,
    ndvi_anom DOUBLE PRECISION,
    vci DOUBLE PRECISION
);
