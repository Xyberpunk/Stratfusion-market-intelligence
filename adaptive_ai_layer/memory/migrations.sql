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
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_symbol (symbol),
    INDEX idx_regime (regime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS regime_outcome_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    regime VARCHAR(80) NOT NULL,
    timestamp DATETIME NOT NULL,
    realized_return FLOAT,
    max_drawdown FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_regime (regime),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sentiment_outcome_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    sentiment VARCHAR(40) NOT NULL,
    confidence FLOAT NOT NULL,
    realized_return FLOAT NOT NULL,
    accurate TINYINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS anomaly_outcome_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    anomaly_type VARCHAR(120) NOT NULL,
    severity VARCHAR(40) NOT NULL,
    timestamp DATETIME NOT NULL,
    realized_move FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_anomaly_type (anomaly_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS signal_feedback_memory (
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
    INDEX idx_strategy_name (strategy_name),
    INDEX idx_regime (regime),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
