CREATE TABLE roles (
    role_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES roles(role_id),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE categories (
    category_id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE bulk_lots (
    bulk_lot_id BIGSERIAL PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(category_id),
    note_from_source TEXT DEFAULT '',
    acquired_at TIMESTAMPTZ NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0),
    remarks TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(category_id),
    product_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    image TEXT DEFAULT '',
    specs TEXT DEFAULT '',
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE bulk_lot_items (
    bulk_lot_item_id BIGSERIAL PRIMARY KEY,
    bulk_lot_id BIGINT NOT NULL REFERENCES bulk_lots(bulk_lot_id) ON DELETE CASCADE,
    discovered_name VARCHAR(100) DEFAULT '',
    brand VARCHAR(100) DEFAULT '',
    model VARCHAR(100) DEFAULT '',
    serial_number VARCHAR(100) DEFAULT '',
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'for_inspection',
            'approved_for_sale',
            'for_repair',
            'disposed',
            'hold'
        )
    ),
    product_id BIGINT UNIQUE REFERENCES products(product_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE item_inspections (
	item_inspection_id BIGSERIAL PRIMARY KEY,
	bulk_lot_item_id  BIGINT NOT NULL REFERENCES bulk_lot_items(bulk_lot_item_id), 
	inspected_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
	condition_grade VARCHAR(30) NOT NULL CHECK (
	condition_grade IN (
		'A (New)',
		'B (Good/Open Box)',
		'C (Fair/Refurbished)',
		'D (Poor/Damaged)',
		'E (Scrap/Obsolete)'
		)
    ),
	decision VARCHAR(50) NOT NULL CHECK (
	decision IN (
		'for_sale', 
		'for_repair', 
		'dispose', 
		'hold')
	),
	notes TEXT DEFAULT '',
	inspected_at TIMESTAMPTZ NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE disposal_records (
	disposal_record_id BIGSERIAL PRIMARY KEY,
	bulk_lot_item_id  BIGINT UNIQUE NOT NULL REFERENCES bulk_lot_items(bulk_lot_item_id), 
	disposal_reason TEXT NOT NULL,
	disposed_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
	disposed_at TIMESTAMPTZ NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE stocks (
	stock_id BIGSERIAL PRIMARY KEY,
	product_id BIGINT UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
	current_quantity INT NOT NULL DEFAULT 0 CHECK (current_quantity >= 0),
	reorder_level INT NOT NULL DEFAULT 5 CHECK (reorder_level >= 0),
	location VARCHAR(50) NOT NULL DEFAULT '',
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



CREATE TABLE stock_movements (
	stock_movement_id BIGSERIAL PRIMARY KEY,
	product_id BIGINT NOT NULL REFERENCES products(product_id),
	movement_type VARCHAR(50) NOT NULL CHECK (
	movement_type IN ( 
		'in', 
		'out',
		'adjustment',
		'disposal',
		'sale'
		)
	),
	quantity INT NOT NULL CHECK( quantity > 0),
	reference_id BIGINT, 
	reference_type VARCHAR(50) DEFAULT '',
	notes TEXT DEFAULT '',
	user_id BIGINT NOT NULL REFERENCES users(user_id),
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE sales (
	sale_id BIGSERIAL PRIMARY KEY,
	user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
	sale_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (total_amount >=0),
	status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (
	status IN (
		'pending',
		'completed',
		'cancelled'
		)
	),
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



CREATE TABLE sale_items (
	sale_item_id BIGSERIAL PRIMARY KEY,
	sale_id BIGINT NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
	product_id BIGINT NOT NULL REFERENCES products(product_id),
	quantity INT NOT NULL CHECK(quantity >0),
	unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK(unit_price >=0) ,
	subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK(subtotal >=0)
);



CREATE TABLE payments (
	payment_id BIGSERIAL PRIMARY KEY,
	sale_id BIGINT NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
	payment_method VARCHAR(50) NOT NULL DEFAULT 'cash' CHECK (
	payment_method IN (
		'cash',
		'gcash',
		'card',
		'bank_transfer',
		'mixed'
		)
	), 
	amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK(amount >=0) ,
	paid_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



