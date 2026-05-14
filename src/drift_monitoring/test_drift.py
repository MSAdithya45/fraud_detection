from src.drift_monitoring.drift_aggregate import aggregate_drift
from src.drift_monitoring.severity_router import determine_severity

result = aggregate_drift()

severity = determine_severity(
    result["final_drift_score"]
)

print(result)
print("Severity:", severity)