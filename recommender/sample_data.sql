-- Create Tables
CREATE TABLE customer_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    city VARCHAR(100)
);

CREATE TABLE product_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(100),
    price DECIMAL(10,2),
    description TEXT
);

CREATE TABLE taxinvoice_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    invoice_date DATE,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customer_details(id)
);

CREATE TABLE taxinvoiceitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT,
    product_id INT,
    quantity INT,
    subtotal DECIMAL(10,2),
    FOREIGN KEY (invoice_id) REFERENCES taxinvoice_details(id),
    FOREIGN KEY (product_id) REFERENCES product_details(id)
);

-- Insert Data
INSERT INTO customer_details (id, name, email, phone, city)
VALUES
(1, 'Ravi Sharma', 'ravi.sharma@example.com', '9876543210', 'Pune'),
(2, 'Neha Verma', 'neha.verma@example.com', '9823456789', 'Mumbai'),
(3, 'Amit Singh', 'amit.singh@example.com', '9812233445', 'Nagpur'),
(4, 'Priya Nair', 'priya.nair@example.com', '9901122334', 'Bengaluru'),
(5, 'Rohan Patil', 'rohan.patil@example.com', '9765432109', 'Hyderabad'),
(6, 'Sneha Iyer', 'sneha.iyer@example.com', '9988776655', 'Chennai'),
(7, 'Vikram Mehta', 'vikram.mehta@example.com', '9876501234', 'Delhi'),
(8, 'Divya Kulkarni', 'divya.kulkarni@example.com', '9810098765', 'Ahmedabad'),
(9, 'Karan Jain', 'karan.jain@example.com', '9898989898', 'Jaipur'),
(10, 'Anjali Deshmukh', 'anjali.deshmukh@example.com', '9777712345', 'Pune');

INSERT INTO product_details (id, product_name, category, price, description)
VALUES
(1, 'Cockroach Control Service', 'Home Pest Control', 799.00, 'Gel and spray treatment for cockroach elimination'),
(2, 'Termite Control Service', 'Wood Protection', 1499.00, 'Anti-termite drilling and chemical treatment'),
(3, 'Mosquito Fogging Service', 'Outdoor Pest Control', 999.00, 'Thermal fogging and residual spraying'),
(4, 'Rodent Control Service', 'Rodent Management', 1299.00, 'Bait and trap method for rodent control'),
(5, 'Bed Bug Treatment', 'Home Pest Control', 899.00, 'Steam and chemical treatment for bed bugs'),
(6, 'Ant Control Service', 'Home Pest Control', 699.00, 'Spray treatment to eliminate ants'),
(7, 'General Pest Control Combo', 'Combo Offer', 1999.00, 'Full home combo – cockroach, ant, and spider control'),
(8, 'Disinfection & Sanitization', 'Health & Hygiene', 599.00, 'Kills germs and viruses on all surfaces'),
(9, 'Garden Pest Control', 'Outdoor Pest Control', 1199.00, 'Pest control for lawns and gardens'),
(10, 'Annual Maintenance Contract (AMC)', 'Subscription', 3999.00, 'Full-year coverage for all pest control services');

INSERT INTO taxinvoice_details (id, customer_id, invoice_date, total_amount)
VALUES
(1, 1, '2025-09-01', 2298.00),
(2, 2, '2025-09-10', 999.00),
(3, 3, '2025-09-15', 1499.00),
(4, 4, '2025-09-20', 2698.00),
(5, 5, '2025-09-22', 3999.00),
(6, 6, '2025-09-25', 1598.00),
(7, 7, '2025-09-27', 999.00),
(8, 8, '2025-09-29', 1798.00),
(9, 9, '2025-10-02', 1299.00),
(10, 10, '2025-10-05', 2498.00);

INSERT INTO taxinvoiceitem (id, invoice_id, product_id, quantity, subtotal)
VALUES
(1, 1, 1, 1, 799.00),
(2, 1, 7, 1, 1499.00),
(3, 2, 3, 1, 999.00),
(4, 3, 2, 1, 1499.00),
(5, 4, 1, 1, 799.00),
(6, 4, 4, 1, 1299.00),
(7, 5, 10, 1, 3999.00),
(8, 6, 1, 1, 799.00),
(9, 6, 6, 1, 799.00),
(10, 7, 5, 1, 999.00),
(11, 8, 9, 1, 1199.00),
(12, 8, 8, 1, 599.00),
(13, 9, 4, 1, 1299.00),
(14, 10, 2, 1, 1499.00),
(15, 10, 5, 1, 999.00);

CREATE TABLE pest_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    base_product_id INT NOT NULL,
    recommended_product_id INT NOT NULL,
    recommendation_type ENUM('upsell', 'cross-sell') NOT NULL,
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_details(id),
    FOREIGN KEY (base_product_id) REFERENCES product_details(id),
    FOREIGN KEY (recommended_product_id) REFERENCES product_details(id)
);

INSERT INTO pest_recommendations (customer_id, base_product_id, recommended_product_id, recommendation_type, confidence_score)
VALUES
(1, 1, 4, 'upsell', 0.92),
(2, 3, 5, 'cross-sell', 0.85),
(3, 2, 1, 'upsell', 0.78),
(4, 4, 3, 'cross-sell', 0.80),
(5, 5, 2, 'upsell', 0.76),
(6, 7, 10, 'upsell', 0.88),
(7, 8, 9, 'cross-sell', 0.74),
(8, 9, 1, 'cross-sell', 0.70),
(9, 10, 7, 'cross-sell', 0.81),
(10, 6, 5, 'upsell', 0.79);
