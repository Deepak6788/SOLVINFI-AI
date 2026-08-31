import os
import sys

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

from collections import Counter
from services.models import Event


def detect_anomaly(service_name=None, window_size=20):

    # --------------------------------------------------
    # 1. Get recent events
    # --------------------------------------------------

    events_query = Event.objects.all().order_by("-timestamp")

    if service_name:
        events_query = events_query.filter(
            service=service_name
        )

    events = list(
        events_query[:window_size]
    )

    if not events:

        return {
            "anomaly_detected": False,
            "anomaly_score": 0,
            "message": "Not enough event data."
        }

    # --------------------------------------------------
    # 2. Count event types
    # --------------------------------------------------

    event_counts = Counter(
        event.event_type
        for event in events
    )

    # --------------------------------------------------
    # 3. Count severities
    # --------------------------------------------------

    severity_counts = Counter(
        event.severity
        for event in events
    )

    error_count = severity_counts.get(
        "ERROR",
        0
    )

    warning_count = severity_counts.get(
        "WARNING",
        0
    )

    # --------------------------------------------------
    # 4. Calculate failure rate
    # --------------------------------------------------

    failure_count = (
        error_count +
        warning_count
    )

    failure_rate = (
        failure_count / len(events)
    ) * 100

    # --------------------------------------------------
    # 5. Detect repeated event patterns
    # --------------------------------------------------

    repeated_event = None
    repeated_count = 0

    for event_type, count in event_counts.items():

        if count > repeated_count:

            repeated_event = event_type
            repeated_count = count

    # --------------------------------------------------
    # 6. Calculate anomaly score
    # --------------------------------------------------

    anomaly_score = 0

    # High error concentration
    if error_count >= 3:

        anomaly_score += 40

    elif error_count >= 2:

        anomaly_score += 25

    elif error_count >= 1:

        anomaly_score += 10

    # High warning concentration
    if warning_count >= 5:

        anomaly_score += 25

    elif warning_count >= 3:

        anomaly_score += 15

    # Repeated event pattern
    if repeated_count >= 5:

        anomaly_score += 25

    elif repeated_count >= 3:

        anomaly_score += 15

    # High overall failure rate
    if failure_rate >= 60:

        anomaly_score += 20

    elif failure_rate >= 40:

        anomaly_score += 10

    anomaly_score = min(
        anomaly_score,
        100
    )

    # --------------------------------------------------
    # 7. Determine anomaly
    # --------------------------------------------------

    anomaly_detected = (
        anomaly_score >= 50
    )

    # --------------------------------------------------
    # 8. Determine risk level
    # --------------------------------------------------

    if anomaly_score >= 80:

        risk_level = "CRITICAL"

    elif anomaly_score >= 60:

        risk_level = "HIGH"

    elif anomaly_score >= 50:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    # --------------------------------------------------
    # 9. Generate explanation
    # --------------------------------------------------

    if anomaly_detected:

        reasons = []

        if error_count >= 2:

            reasons.append(
                "multiple ERROR events"
            )

        if warning_count >= 3:

            reasons.append(
                "multiple WARNING events"
            )

        if repeated_count >= 3:

            reasons.append(
                f"repeated {repeated_event} events"
            )

        if failure_rate >= 40:

            reasons.append(
                "elevated failure rate"
            )

        reason = (
            "Unusual activity detected due to "
            + ", ".join(reasons)
            + "."
        )

    else:

        reason = (
            "Recent event activity does not "
            "show a significant anomaly."
        )

    # --------------------------------------------------
    # 10. Return anomaly intelligence
    # --------------------------------------------------

    return {

        "anomaly_detected": anomaly_detected,

        "anomaly_score": anomaly_score,

        "risk_level": risk_level,

        "service": service_name,

        "events_analyzed": len(events),

        "failure_rate": round(
            failure_rate,
            2
        ),

        "error_count": error_count,

        "warning_count": warning_count,

        "dominant_event": repeated_event,

        "dominant_event_count": repeated_count,

        "event_counts": dict(
            event_counts
        ),

        "reason": reason
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SOLVINFI ANOMALY DETECTION")
    print("=" * 70)

    result = detect_anomaly(
        service_name="Deres"
    )

    print("\nAnomaly Analysis:\n")

    print(result)

    print("\n" + "=" * 70)