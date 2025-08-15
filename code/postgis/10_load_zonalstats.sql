-- Example load command (adjust file path)
\COPY public.zonalstats(corregimie, fecha, spi_1, ndvi_anom, vci)
FROM '/path/to/zonalstats.csv' DELIMITER ',' CSV HEADER;
