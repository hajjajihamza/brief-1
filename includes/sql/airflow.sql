-- 1 user owner de base de donner
CREATE USER airflow WITH PASSWORD 'airflow';

-- 2 creé base de donner de airflow
CREATE DATABASE brif_1_airflow OWNER airflow;