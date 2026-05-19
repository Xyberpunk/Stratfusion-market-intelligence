CREATE TABLE IF NOT EXISTS event_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    correlation_id VARCHAR(120) NOT NULL,
    event_type VARCHAR(120) NOT NULL,
    service VARCHAR(120) NOT NULL,
    payload JSON,
    timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dead_letter_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(120) NOT NULL,
    correlation_id VARCHAR(120) NOT NULL,
    event_type VARCHAR(120) NOT NULL,
    original_topic VARCHAR(150),
    error TEXT,
    retryable TINYINT DEFAULT 0,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pipeline_state (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    correlation_id VARCHAR(120) NOT NULL UNIQUE,
    symbol VARCHAR(50) NOT NULL,
    state VARCHAR(60) NOT NULL,
    required_states JSON,
    completed_states JSON,
    error TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_symbol (symbol),
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pipeline_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    correlation_id VARCHAR(120) NOT NULL,
    state VARCHAR(60) NOT NULL,
    event_type VARCHAR(120) NOT NULL,
    payload JSON,
    timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS service_health_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(120) NOT NULL,
    status VARCHAR(40) NOT NULL,
    detail TEXT,
    checked_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
