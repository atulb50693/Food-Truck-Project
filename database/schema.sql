-- This file should contain table definitions for the database.

USE tul_abuelhia;

DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Payment_Method;
DROP TABLE IF EXISTS DIM_Truck;

CREATE TABLE DIM_Payment_Method (
    payment_method_id SMALLINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    payment_method VARCHAR(10) NOT NULL   
);

CREATE TABLE DIM_Truck (
    truck_id SMALLINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    truck_name VARCHAR(255) NOT NULL,
    truck_description TEXT,
    has_card_reader BOOLEAN NOT NULL,
    fsa_rating SMALLINT NOT NULL
    
);

CREATE TABLE FACT_Transaction (
    transaction_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    truck_id SMALLINT NOT NULL,
    payment_method_id SMALLINT NOT NULL,
    total_price FLOAT NOT NULL,
    event_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method(payment_method_id),
    CONSTRAINT check_total_price_not_zero CHECK (total_price > 0.0)
);

INSERT INTO DIM_Truck (truck_name, truck_description, has_card_reader, fsa_rating) VALUES
('Burrito Madness', 'An authentic taste of Mexico.', TRUE, 4),
('Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', FALSE, 2),
('Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', TRUE, 5),
('Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', TRUE, 4),
('Yoghurt Heaven', 'All the great tastes, but only some of the calories!', TRUE, 4),
('SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', FALSE, 3);


INSERT INTO DIM_Payment_Method (payment_method) VALUES 
('cash'), ('card');