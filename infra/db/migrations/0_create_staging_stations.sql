CREATE TABLE staging.stations (
    id SERIAL PRIMARY KEY,
    station_id INT NOT NULL,
    station_code VARCHAR(255) NOT NULL,
    station_name VARCHAR(255) NOT NULL,
    wgs84_n VARCHAR(255) NOT NULL,
    wgs84_e VARCHAR(255) NOT NULL,
    city_id INT NOT NULL,
    city_name VARCHAR(255) NOT NULL,
    municipality VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    province VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    ingestion_timestamp TIMESTAMPTZ NOT NULL
);
