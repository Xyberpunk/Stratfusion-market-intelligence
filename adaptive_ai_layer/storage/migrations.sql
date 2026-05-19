CREATE TABLE IF NOT EXISTS ml_features (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    feature_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS training_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(80) NOT NULL UNIQUE,
    model_name VARCHAR(150) NOT NULL,
    target_kind VARCHAR(80) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_registry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    target_kind VARCHAR(80) NOT NULL,
    path TEXT,
    metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    prediction VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    probabilities JSON,
    features_used JSON,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS regime_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    regime VARCHAR(80) NOT NULL,
    confidence FLOAT NOT NULL,
    features JSON,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_regime (regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS anomaly_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    anomaly_type VARCHAR(120) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    score FLOAT NOT NULL,
    features JSON,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_anomaly_type (anomaly_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sentiment_outputs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50),
    timestamp DATETIME NOT NULL,
    sentiment VARCHAR(30) NOT NULL,
    confidence FLOAT NOT NULL,
    raw_scores JSON,
    event_type VARCHAR(120),
    text_hash CHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS strategy_performance_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_name VARCHAR(150) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    sector VARCHAR(100),
    regime VARCHAR(80) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    volatility_bucket VARCHAR(50),
    accuracy FLOAT NOT NULL,
    win_rate FLOAT NOT NULL,
    avg_return FLOAT NOT NULL,
    max_drawdown FLOAT NOT NULL,
    sample_size INT NOT NULL,
    last_updated DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_regime (regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dynamic_weight_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    weights JSON NOT NULL,
    reason TEXT,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS adaptive_rewards (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_name VARCHAR(150) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    regime VARCHAR(80) NOT NULL,
    reward FLOAT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_regime (regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS paper_feedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    strategy_name VARCHAR(150) NOT NULL,
    regime VARCHAR(80) NOT NULL,
    timestamp DATETIME NOT NULL,
    signal VARCHAR(30) NOT NULL,
    realized_return FLOAT NOT NULL,
    max_adverse_excursion FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_regime (regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
