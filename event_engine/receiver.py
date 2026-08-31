import os
import sys
from datetime import datetime, timezone


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
# DJANGO SETUP
# ============================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()


# ============================================================
# DATABASE MODEL
# ============================================================

from services.models import Event


# ============================================================
# RECEIVE EVENT
# ============================================================

def receive_event(event):

    print("=" * 60)
    print("SOLVINFI EVENT RECEIVER")
    print("=" * 60)

    print("\nIncoming event:")
    print(event)

    # --------------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------------

    timestamp = event.get(
        "timestamp"
    )

    if isinstance(timestamp, str):

        timestamp = timestamp.replace(
            "Z",
            "+00:00"
        )

        timestamp = datetime.fromisoformat(
            timestamp
        )

    # --------------------------------------------------------
    # Make timestamp timezone-aware
    # --------------------------------------------------------

    if timestamp.tzinfo is None:

        timestamp = timestamp.replace(
            tzinfo=timezone.utc
        )

    # --------------------------------------------------------
    # Save event to database
    # --------------------------------------------------------

    saved_event = Event.objects.create(

        service=event.get(
            "service",
            ""
        ),

        service_type=event.get(
            "service_type",
            ""
        ),

        event_type=event.get(
            "event_type",
            ""
        ),

        message=event.get(
            "message",
            ""
        ),

        severity=event.get(
            "severity",
            "INFO"
        ),

        timestamp=timestamp
    )

    # --------------------------------------------------------
    # Confirmation
    # --------------------------------------------------------

    print("\nEvent saved successfully!")

    print(
        "Database Event ID:",
        saved_event.id
    )

    print(
        "Service:",
        saved_event.service
    )

    print(
        "Event Type:",
        saved_event.event_type
    )

    print(
        "Severity:",
        saved_event.severity
    )

    print(
        "Timestamp:",
        saved_event.timestamp
    )

    print("=" * 60)

    return saved_event


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_event = {

        "service": "Deres",

        "service_type":
            "Authentication & Identity",

        "event_type":
            "LOGIN_FAILED",

        "message":
            "User authentication failed.",

        "severity":
            "WARNING",

        "timestamp":
            "2026-08-29T14:30:00+00:00"
    }

    receive_event(
        test_event
    )