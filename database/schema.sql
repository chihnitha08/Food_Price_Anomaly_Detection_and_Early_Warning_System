CREATE DATABASE IF NOT EXISTS food_security;
USE food_security;

CREATE TABLE IF NOT EXISTS daily_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(50) NOT NULL,
    commodity VARCHAR(50) NOT NULL,
    price_date DATE NOT NULL,
    modal_price DECIMAL(10,2) NOT NULL,
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    num_records INT,
    UNIQUE KEY uq_day (state, commodity, price_date)
);