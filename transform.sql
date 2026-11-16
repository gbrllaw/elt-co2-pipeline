DROP TABLE IF EXISTS fact_co2;
DROP TABLE IF EXISTS dim_country;

CREATE TABLE dim_country AS
SELECT DISTINCT iso_code, country 
FROM raw_co2 
WHERE iso_code IS NOT NULL 
    AND LEFT(iso_code, 4) <> 'OWID';

ALTER TABLE dim_country
ADD PRIMARY KEY(iso_code);

CREATE TABLE fact_co2 AS 
SELECT
    r.iso_code,
    r.year::int AS year, 
    r.population::bigint AS population, 
    r.gdp,
    r.co2,
    r.co2_per_capita
FROM raw_co2 r 
JOIN dim_country d 
    ON r.iso_code = d.iso_code
WHERE r.co2 IS NOT NULL; 

ALTER TABLE fact_co2 ADD PRIMARY KEY(iso_code,year);
ALTER TABLE fact_co2 ADD FOREIGN KEY(iso_code) REFERENCES dim_country(iso_code);
