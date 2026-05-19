CREATE TABLE IF NOT EXISTS feature_definitions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feature_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    owner VARCHAR(100),
    version VARCHAR(50),
    dtype VARCHAR(40),
    active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_feature_name (feature_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feature_values (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    feature_name VARCHAR(150) NOT NULL,
    feature_value DOUBLE NOT NULL,
    feature_version VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    freshness_status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_feature_name (feature_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feature_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    features_json JSON NOT NULL,
    feature_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feature_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    feature_name VARCHAR(150) NOT NULL,
    feature_version VARCHAR(50) NOT NULL,
    logic_signature VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_feature_name (feature_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feature_quality_checks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    feature_name VARCHAR(150),
    quality_status VARCHAR(30) NOT NULL,
    issues JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
