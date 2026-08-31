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

from correlation.correlation_engine import correlate_recent_events


def analyze_root_cause(correlation):

    if not correlation.get("correlated"):
        return {
            "root_cause_detected": False,
            "root_cause": None,
            "confidence": 0,
            "reason": "No correlated event group was found."
        }

    if not correlation.get("incident_relevant"):
        return {
            "root_cause_detected": False,
            "root_cause": None,
            "confidence": correlation.get(
                "correlation_score",
                0
            ),
            "reason": "The correlated events appear to represent normal activity."
        }

    event_counts = correlation.get(
        "event_counts",
        {}
    )

    highest_severity = correlation.get(
        "highest_severity"
    )

    root_event = correlation.get(
        "root_event"
    )

    # Start with the correlation score
    confidence = correlation.get(
        "correlation_score",
        0
    )

    # Repeated database failures are strong evidence
    database_timeout_count = event_counts.get(
        "DATABASE_TIMEOUT",
        0
    )

    login_failed_count = event_counts.get(
        "LOGIN_FAILED",
        0
    )

    service_down_count = event_counts.get(
        "SERVICE_DOWN",
        0
    )

    # Determine likely root cause
    if database_timeout_count >= 2:

        root_cause = "DATABASE_TIMEOUT"

        reason = (
            "Repeated authentication database timeouts were detected "
            "within the correlated event window. This indicates that "
            "the authentication database may be the primary source "
            "of the observed failures."
        )

        confidence = min(
            confidence + 10,
            100
        )

    elif database_timeout_count >= 1 and login_failed_count >= 1:

        root_cause = "DATABASE_TIMEOUT"

        reason = (
            "A database timeout occurred alongside authentication "
            "failures. The database timeout is a likely underlying "
            "cause of the authentication problems."
        )

        confidence = min(
            confidence + 5,
            100
        )

    elif service_down_count >= 1:

        root_cause = "SERVICE_DOWN"

        reason = (
            "The service became unavailable during the correlated "
            "event window, making service unavailability a likely "
            "primary cause."
        )

    elif login_failed_count >= 3:

        root_cause = "LOGIN_FAILED"

        reason = (
            "Multiple authentication failures occurred within a "
            "short period, indicating a possible authentication "
            "failure pattern."
        )

    else:

        root_cause = root_event

        reason = (
            "The highest-severity event was selected as the most "
            "likely root cause because insufficient evidence was "
            "available to identify a more specific cause."
        )

    return {
        "root_cause_detected": True,
        "root_cause": root_cause,
        "confidence": confidence,
        "highest_severity": highest_severity,
        "event_counts": event_counts,
        "reason": reason
    }


if __name__ == "__main__":

    print("=" * 60)
    print("SOLVINFI ROOT-CAUSE ANALYSIS")
    print("=" * 60)

    correlation = correlate_recent_events()

    print("\nCorrelation:")
    print(correlation)

    analysis = analyze_root_cause(
        correlation
    )

    print("\nRoot-Cause Analysis:")
    print(analysis)

    print("\n" + "=" * 60)