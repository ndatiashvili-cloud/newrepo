CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    full_name VARCHAR(150),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    organization_id UUID,
    is_superuser BOOLEAN DEFAULT TRUE,
    region VARCHAR(100),
    branches JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now(),
    last_login TIMESTAMP,
    theme_preference VARCHAR(50) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    dashboard_layout JSON
);
