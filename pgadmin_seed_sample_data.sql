-- Reload sample data into the schema from pgadmin_import_bulk_pos.sql
-- Run this in pgAdmin Query Tool (or psql) against pos_database AFTER tables exist.
-- Clears all rows in these tables and resets sequences, then inserts the dataset below.

BEGIN;

TRUNCATE TABLE
    payments,
    sale_items,
    stock_movements,
    sales,
    stocks,
    disposal_records,
    item_inspections,
    bulk_lot_items,
    products,
    bulk_lots,
    categories,
    users,
    roles
RESTART IDENTITY;

-- roles
INSERT INTO roles (name)
VALUES
    ('admin'),
    ('cashier'),
    ('inspector');

-- users
INSERT INTO users (
    role_id,
    full_name,
    email,
    password_hash,
    is_active
)
VALUES
    (1, 'Maria Santos', 'maria@japansurplus.com', 'hashed_password_1', TRUE),
    (2, 'Juan Dela Cruz', 'juan@japansurplus.com', 'hashed_password_2', TRUE),
    (3, 'Ana Reyes', 'ana@japansurplus.com', 'hashed_password_3', TRUE),
    (4, 'Carlo Mendoza', 'carlo@japansurplus.com', 'hashed_password_4', TRUE),
    (5, 'Rosa Lim', 'rosa@japansurplus.com', 'hashed_password_5', FALSE);

-- categories
INSERT INTO categories (category_name, description)
VALUES
    ('Computers', 'Laptops, desktops, and computer peripherals'),
    ('Glassware', 'Cups, plates, bowls, and glass items'),
    ('Linens', 'Pillows, bedsheets, blankets, and similar items'),
    ('Miscellaneous', 'Random surplus items of various kinds');

-- bulk_lots
INSERT INTO bulk_lots (
    category_id,
    note_from_source,
    acquired_at,
    total_cost,
    remarks
)
VALUES
    (1, 'Lot from Osaka electronics dealer', '2025-01-10 09:00:00+08', 45000.00, 'Mixed laptops and desktops'),
    (2, 'Lot from Tokyo kitchenware supplier', '2025-01-15 10:00:00+08', 12000.00, 'Assorted glassware sets'),
    (3, 'Lot from Kyoto textile supplier', '2025-02-01 08:00:00+08', 8000.00, 'Bedsheets and pillowcases'),
    (4, 'Random lot from Nagoya auction', '2025-02-10 14:00:00+08', 5000.00, 'Mixed random items'),
    (1, 'Second computer lot from Fukuoka', '2025-03-01 09:00:00+08', 38000.00, 'Mostly laptops');

-- products
INSERT INTO products (
    category_id,
    product_name,
    description,
    image,
    specs,
    price
)
VALUES
    (1, 'Fujitsu Lifebook A574', 'Used business laptop', '', 'Intel Core i5, 4GB RAM, 320GB HDD', 3500.00),
    (1, 'NEC VersaPro VK26', 'Refurbished office laptop', '', 'Intel Core i5, 8GB RAM, 256GB SSD', 5500.00),
    (1, 'Panasonic CF-D1', 'Rugged toughbook tablet', '', 'Intel Core i5, 4GB RAM, 128GB SSD', 7000.00),
    (2, 'Noritake Glass Set', 'Set of 6 drinking glasses', '', 'Clear glass, 250ml capacity', 450.00),
    (2, 'Iwaki Heat Resistant Bowl', 'Microwave safe glass bowl', '', 'Borosilicate glass, 1.5L', 350.00),
    (3, 'Nishikawa Pillow', 'Japanese quality pillow', '', 'Cotton cover, medium firmness', 600.00),
    (3, 'Senshu Bedsheet Set', 'Double bed sheet set', '', '100% cotton, white', 850.00),
    (4, 'Assorted Stationery Bundle', 'Mixed Japanese stationery', '', 'Various brands', 200.00);

-- bulk_lot_items
INSERT INTO bulk_lot_items (
    bulk_lot_id,
    discovered_name,
    brand,
    model,
    serial_number,
    status,
    product_id
)
VALUES
    (1, 'Laptop unit 1', 'Fujitsu', 'Lifebook A574', 'FJ-001-2025', 'approved_for_sale', 1),
    (1, 'Laptop unit 2', 'NEC', 'VersaPro VK26', 'NEC-002-2025', 'approved_for_sale', 2),
    (1, 'Laptop unit 3', 'Panasonic', 'CF-D1', 'PAN-003-2025', 'approved_for_sale', 3),
    (1, 'Laptop unit 4', 'Toshiba', 'Dynabook B55', 'TOSH-004-2025', 'for_repair', NULL),
    (1, 'Laptop unit 5', 'Sony', 'VAIO Pro 13', 'SONY-005-2025', 'disposed', NULL),
    (2, 'Glass set 1', 'Noritake', 'Classic Series', 'NOR-001-2025', 'approved_for_sale', 4),
    (2, 'Glass bowl 1', 'Iwaki', 'Heat Series', 'IWK-002-2025', 'approved_for_sale', 5),
    (2, 'Broken glass set', 'Unknown', 'Unknown', 'UNK-003-2025', 'disposed', NULL),
    (3, 'Pillow unit 1', 'Nishikawa', 'Standard', 'NSK-001-2025', 'approved_for_sale', 6),
    (3, 'Bedsheet set 1', 'Senshu', 'Double Set', 'SNS-002-2025', 'approved_for_sale', 7),
    (4, 'Stationery bundle 1', 'Various', 'Mixed', 'MISC-001-2025', 'approved_for_sale', 8),
    (4, 'Unknown item 1', 'Unknown', 'Unknown', 'MISC-002-2025', 'hold', NULL),
    (5, 'Laptop unit 6', 'Fujitsu', 'Lifebook E744', 'FJ-006-2025', 'for_inspection', NULL);

-- item_inspections
INSERT INTO item_inspections (
    bulk_lot_item_id,
    inspected_by,
    condition_grade,
    decision,
    notes,
    inspected_at
)
VALUES
    (1, 3, 'B (Good/Open Box)', 'for_sale', 'Minor scratches on lid', '2025-01-12 10:00:00+08'),
    (2, 3, 'B (Good/Open Box)', 'for_sale', 'Good condition, tested working', '2025-01-12 11:00:00+08'),
    (3, 5, 'A (New)', 'for_sale', 'Excellent condition', '2025-01-12 12:00:00+08'),
    (4, 3, 'D (Poor/Damaged)', 'for_repair', 'Keyboard not working', '2025-01-12 13:00:00+08'),
    (5, 5, 'E (Scrap/Obsolete)', 'dispose', 'Screen cracked, motherboard damaged', '2025-01-12 14:00:00+08'),
    (6, 3, 'B (Good/Open Box)', 'for_sale', 'Complete set, no chips', '2025-01-17 09:00:00+08'),
    (7, 5, 'A (New)', 'for_sale', 'Still in original packaging', '2025-01-17 10:00:00+08'),
    (8, 3, 'E (Scrap/Obsolete)', 'dispose', 'Multiple broken pieces', '2025-01-17 11:00:00+08'),
    (9, 5, 'B (Good/Open Box)', 'for_sale', 'Clean and good condition', '2025-02-03 09:00:00+08'),
    (10, 3, 'A (New)', 'for_sale', 'Still sealed in packaging', '2025-02-03 10:00:00+08'),
    (11, 5, 'C (Fair/Refurbished)', 'for_sale', 'Mixed quality items', '2025-02-12 09:00:00+08');

-- disposal_records
INSERT INTO disposal_records (
    bulk_lot_item_id,
    disposal_reason,
    disposed_by,
    disposed_at
)
VALUES
    (5, 'Screen cracked and motherboard damaged beyond repair', 1, '2025-01-13 09:00:00+08'),
    (8, 'Multiple broken glass pieces, unsafe to sell', 1, '2025-01-18 09:00:00+08');

-- stocks
INSERT INTO stocks (
    product_id,
    current_quantity,
    reorder_level,
    location
)
VALUES
    (1, 3, 2, 'Shelf A1'),
    (2, 2, 2, 'Shelf A2'),
    (3, 1, 1, 'Shelf A3'),
    (4, 5, 3, 'Shelf B1'),
    (5, 4, 2, 'Shelf B2'),
    (6, 6, 3, 'Shelf C1'),
    (7, 4, 2, 'Shelf C2'),
    (8, 10, 5, 'Shelf D1');

-- stock_movements
INSERT INTO stock_movements (
    product_id,
    movement_type,
    quantity,
    reference_type,
    reference_id,
    notes,
    user_id
)
VALUES
    (1, 'in', 3, 'bulk_lot', 1, 'Initial stock from bulk lot 1', 1),
    (2, 'in', 2, 'bulk_lot', 1, 'Initial stock from bulk lot 1', 1),
    (3, 'in', 1, 'bulk_lot', 1, 'Initial stock from bulk lot 1', 1),
    (4, 'in', 5, 'bulk_lot', 2, 'Initial stock from bulk lot 2', 1),
    (5, 'in', 4, 'bulk_lot', 2, 'Initial stock from bulk lot 2', 1),
    (6, 'in', 6, 'bulk_lot', 3, 'Initial stock from bulk lot 3', 1),
    (7, 'in', 4, 'bulk_lot', 3, 'Initial stock from bulk lot 3', 1),
    (8, 'in', 10, 'bulk_lot', 4, 'Initial stock from bulk lot 4', 1),
    (1, 'sale', 1, 'sale', 1, 'Sold 1 unit', 2),
    (2, 'sale', 1, 'sale', 1, 'Sold 1 unit', 2);

-- sales
INSERT INTO sales (user_id, sale_date, total_amount, status)
VALUES
    (2, '2025-02-01 10:30:00+08', 9000.00, 'completed'),
    (2, '2025-02-05 14:00:00+08', 800.00, 'completed'),
    (4, '2025-02-10 11:00:00+08', 1200.00, 'completed'),
    (2, '2025-02-15 15:00:00+08', 350.00, 'cancelled'),
    (4, '2025-03-01 09:30:00+08', 6350.00, 'completed');

-- sale_items
INSERT INTO sale_items (
    sale_id,
    product_id,
    quantity,
    unit_price,
    subtotal
)
VALUES
    (1, 1, 1, 3500.00, 3500.00),
    (1, 2, 1, 5500.00, 5500.00),
    (2, 6, 1, 600.00, 600.00),
    (2, 8, 1, 200.00, 200.00),
    (3, 4, 2, 450.00, 900.00),
    (3, 7, 1, 850.00, 850.00),
    (4, 5, 1, 350.00, 350.00),
    (5, 3, 1, 7000.00, 7000.00),
    (5, 8, 3, 200.00, 600.00),
    (5, 6, 1, 600.00, 600.00);

-- payments
INSERT INTO payments (sale_id, payment_method, amount, paid_at)
VALUES
    (1, 'cash', 9000.00, '2025-02-01 10:35:00+08'),
    (2, 'gcash', 800.00, '2025-02-05 14:05:00+08'),
    (3, 'cash', 700.00, '2025-02-10 11:05:00+08'),
    (3, 'gcash', 500.00, '2025-02-10 11:06:00+08'),
    (5, 'card', 6350.00, '2025-03-01 09:35:00+08');

COMMIT;
