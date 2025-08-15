-- Clamp NDVI anomaly to [-1, 1]
UPDATE public.zonalstats
SET ndvi_anom =
    CASE
        WHEN ndvi_anom < -1 THEN -1
        WHEN ndvi_anom > 1 THEN 1
        ELSE ndvi_anom
    END;

-- Cast fecha from text to date (if needed)
ALTER TABLE public.zonalstats
ALTER COLUMN fecha TYPE date
USING to_date(fecha, 'YYYY-MM');
