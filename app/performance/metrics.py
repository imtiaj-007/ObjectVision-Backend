from prometheus_client import Counter, Histogram

class LogMetrics:
    log_storage_duration = Histogram(
        'log_storage_duration_seconds',
        'Time spent storing logs'
    )
    log_storage_failures = Counter(
        'log_storage_failures_total',
        'Number of log storage failures'
    )
    logs_processed = Counter(
        'logs_processed_total',
        'Number of logs processed',
        ['level']
    )

metrics = LogMetrics()