import os
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    BASE_DIR
)


# ============================================================
# IMPORT ANOMALY DETECTOR
# ============================================================

from anomaly_detection.detector import (
    detect_anomaly
)


# ============================================================
# HEALTH SNAPSHOT
# ============================================================

class HealthSnapshot:

    def capture(self, service_name=None):

        anomaly = detect_anomaly(
            service_name=service_name
        )

        return {

            "anomaly_score": anomaly.get(
                "anomaly_score",
                0
            ),

            "failure_rate": anomaly.get(
                "failure_rate",
                0
            ),

            "error_count": anomaly.get(
                "error_count",
                0
            ),

            "warning_count": anomaly.get(
                "warning_count",
                0
            ),

            "anomaly_detected": anomaly.get(
                "anomaly_detected",
                False
            ),

            "risk_level": anomaly.get(
                "risk_level",
                "LOW"
            ),

            "dominant_event": anomaly.get(
                "dominant_event"
            ),

            "dominant_event_count": anomaly.get(
                "dominant_event_count",
                0
            ),

            "events_analyzed": anomaly.get(
                "events_analyzed",
                0
            ),

            "reason": anomaly.get(
                "reason",
                ""
            )
        }


# ============================================================
# HELPER FUNCTION
# ============================================================

def capture_health(service_name=None):

    monitor = HealthSnapshot()

    return monitor.capture(
        service_name=service_name
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("SOLVINFI HEALTH SNAPSHOT")
    print("=" * 65)

    snapshot = capture_health()

    print("\nCurrent System Health:\n")

    print(snapshot)

    print("\n" + "=" * 65)