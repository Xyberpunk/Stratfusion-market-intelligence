CREATE TABLE IF NOT EXISTS model_registry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    active_version VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    path TEXT,
    metrics JSON,
    active TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS training_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(120) NOT NULL UNIQUE,
    model_name VARCHAR(150) NOT NULL,
    model_version VARCHAR(120),
    status VARCHAR(40) NOT NULL,
    metrics JSON,
    started_at DATETIME NOT NULL,
    finished_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_evaluations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    dataset_name VARCHAR(120),
    metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS prediction_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    prediction JSON NOT NULL,
    confidence FLOAT NOT NULL,
    features_version VARCHAR(120) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_model_name (model_name),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
