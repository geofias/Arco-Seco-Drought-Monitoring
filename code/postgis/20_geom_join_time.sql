-- Join corregimientos geometry to zonalstats by name, duplicating geometries per month
CREATE TABLE public.zonalstats_geom AS
SELECT
    z.*,
    g.geom
FROM
    public.zonalstats z
JOIN
    public.corregimientos g
ON
    z.corregimie = g.corregimie;
