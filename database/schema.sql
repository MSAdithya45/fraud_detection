CREATE TABLE IF NOT EXISTS drift_analysis_log (

    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_start_id INT,
    batch_end_id INT,

    psi_score FLOAT,
    ks_score FLOAT,

    final_drift_score FLOAT,

    severity VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS medium_severity_watchlist (

    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_start_id INT,
    batch_end_id INT,

    psi_score FLOAT,
    ks_score FLOAT,

    final_drift_score FLOAT,

    monitoring_status VARCHAR(20) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS feedback_queue (

    id INT AUTO_INCREMENT PRIMARY KEY,

    batch_start_id INT,
    batch_end_id INT,

    psi_score FLOAT,
    ks_score FLOAT,

    final_drift_score FLOAT,

    feedback_status VARCHAR(20) DEFAULT 'PENDING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);