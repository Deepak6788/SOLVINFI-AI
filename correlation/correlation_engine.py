import os
import sys

from collections import Counter
from datetime import datetime


# ============================================================
# DJANGO SETUP
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
# SEVERITY SCORES
# ============================================================

SEVERITY_SCORE = {

    "INFO": 1,

    "WARNING": 2,

    "ERROR": 3
}


# ============================================================
# TIMESTAMP PARSER
# ============================================================

def parse_timestamp(timestamp):

    if not timestamp:

        return datetime.min

    if isinstance(
        timestamp,
        datetime
    ):

        return timestamp

    return datetime.fromisoformat(

        timestamp.replace(
            "Z",
            "+00:00"
        )
    )


# ============================================================
# CORRELATE EVENTS
# ============================================================

def correlate_events(
    events,
    time_window_seconds=60
):

    # --------------------------------------------------------
    # No events
    # --------------------------------------------------------

    if not events:

        return {

            "correlated": False,

            "incident_relevant": False,

            "message":
                "No events available for correlation."
        }


    # --------------------------------------------------------
    # Sort newest first
    # --------------------------------------------------------

    sorted_events = sorted(

        events,

        key=lambda event:
            parse_timestamp(
                event["timestamp"]
            ),

        reverse=True
    )


    # --------------------------------------------------------
    # Newest event becomes reference
    # --------------------------------------------------------

    reference_event = (
        sorted_events[0]
    )

    reference_time = parse_timestamp(

        reference_event[
            "timestamp"
        ]
    )

    reference_service = (
        reference_event.get(
            "service"
        )
    )


    # --------------------------------------------------------
    # Find events belonging to same
    # service and time window
    # --------------------------------------------------------

    related_events = []


    for event in sorted_events:

        # ----------------------------------------------------
        # Same service only
        # ----------------------------------------------------

        if (
            event.get("service")
            != reference_service
        ):

            continue


        event_time = parse_timestamp(

            event[
                "timestamp"
            ]
        )


        # ----------------------------------------------------
        # Calculate time difference
        # ----------------------------------------------------

        difference = abs(

            (
                reference_time
                - event_time
            ).total_seconds()
        )


        # ----------------------------------------------------
        # Add event if inside window
        # ----------------------------------------------------

        if (
            difference
            <= time_window_seconds
        ):

            related_events.append(
                event
            )


    # --------------------------------------------------------
    # Not enough related events
    # --------------------------------------------------------

    if len(
        related_events
    ) < 2:

        return {

            "correlated": False,

            "incident_relevant": False,

            "service":
                reference_service,

            "event_count":
                len(related_events),

            "event_counts":
                dict(
                    Counter(
                        event[
                            "event_type"
                        ]
                        for event
                        in related_events
                    )
                ),

            "message":
                "Not enough related events.",

            "related_events":
                related_events
        }


    # ========================================================
    # EVENT COUNTS
    # ========================================================

    event_counts = Counter(

        event[
            "event_type"
        ]

        for event
        in related_events
    )


    # ========================================================
    # SEVERITY
    # ========================================================

    highest_severity_event = max(

        related_events,

        key=lambda event:
            SEVERITY_SCORE.get(

                event.get(
                    "severity",
                    "INFO"
                ),

                1
            )
    )


    highest_severity = (

        highest_severity_event.get(

            "severity",

            "INFO"
        )
    )


    # ========================================================
    # WARNING COUNT
    # ========================================================

    warning_count = sum(

        1

        for event
        in related_events

        if event.get(
            "severity"
        ) == "WARNING"
    )


    # ========================================================
    # ERROR COUNT
    # ========================================================

    error_count = sum(

        1

        for event
        in related_events

        if event.get(
            "severity"
        ) == "ERROR"
    )


    # ========================================================
    # INCIDENT RELEVANCE
    # ========================================================

    incident_relevant = False


    # --------------------------------------------------------
    # Any ERROR
    # --------------------------------------------------------

    if error_count >= 1:

        incident_relevant = True


    # --------------------------------------------------------
    # Three or more WARNING events
    # --------------------------------------------------------

    elif warning_count >= 3:

        incident_relevant = True


    # --------------------------------------------------------
    # Multiple failed logins
    # --------------------------------------------------------

    login_failed_count = (

        event_counts.get(
            "LOGIN_FAILED",
            0
        )
    )


    if login_failed_count >= 3:

        incident_relevant = True


    # --------------------------------------------------------
    # Multiple database timeouts
    # --------------------------------------------------------

    database_timeout_count = (

        event_counts.get(
            "DATABASE_TIMEOUT",
            0
        )
    )


    if database_timeout_count >= 2:

        incident_relevant = True


    # --------------------------------------------------------
    # Service down
    # --------------------------------------------------------

    service_down_count = (

        event_counts.get(
            "SERVICE_DOWN",
            0
        )
    )


    if service_down_count >= 1:

        incident_relevant = True


    # --------------------------------------------------------
    # System crash
    # --------------------------------------------------------

    system_crash_count = (

        event_counts.get(
            "SYSTEM_CRASH",
            0
        )
    )


    if system_crash_count >= 1:

        incident_relevant = True


    # ========================================================
    # CORRELATION SCORE
    # ========================================================

    event_score = min(

        len(
            related_events
        ) * 10,

        50
    )


    severity_score = (

        SEVERITY_SCORE.get(

            highest_severity,

            1
        )

        * 15
    )


    correlation_score = min(

        event_score
        + severity_score,

        100
    )


    # --------------------------------------------------------
    # Keep normal activity low
    # --------------------------------------------------------

    if not incident_relevant:

        correlation_score = min(

            correlation_score,

            30
        )


    # ========================================================
    # RETURN CORRELATION RESULT
    # ========================================================

    return {

        "correlated":
            True,

        "incident_relevant":
            incident_relevant,

        "service":
            reference_service,

        "event_count":
            len(
                related_events
            ),

        "event_counts":
            dict(
                event_counts
            ),

        "root_event":
            highest_severity_event[
                "event_type"
            ],

        "highest_severity":
            highest_severity,

        "correlation_score":
            correlation_score,

        "related_events":
            related_events
    }


# ============================================================
# CORRELATE RECENT DATABASE EVENTS
# ============================================================

def correlate_recent_events(
    time_window_seconds=60
):

    # --------------------------------------------------------
    # Get recent events.
    #
    # We deliberately use ID ordering as well as timestamp
    # ordering so newly inserted events are not accidentally
    # hidden when several events have identical timestamps.
    # --------------------------------------------------------

    events = Event.objects.order_by(
        "-id"
    )[:100]


    # --------------------------------------------------------
    # No events
    # --------------------------------------------------------

    if not events:

        return {

            "correlated": False,

            "incident_relevant": False,

            "message":
                "No events found in database."
        }


    # --------------------------------------------------------
    # Convert database objects to dictionaries
    # --------------------------------------------------------

    database_events = []


    for event in events:

        database_events.append({

            "id":
                event.id,

            "service":
                event.service,

            "event_type":
                event.event_type,

            "severity":
                event.severity,

            "timestamp":
                event.timestamp.isoformat()
        })


    # --------------------------------------------------------
    # Run correlation
    # --------------------------------------------------------

    return correlate_events(

        database_events,

        time_window_seconds
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "SOLVINFI CORRELATION ENGINE"
    )

    print("=" * 60)


    result = (
        correlate_recent_events()
    )


    print(
        "\nDatabase Correlation Result:\n"
    )


    print(result)


    print(
        "\n" + "=" * 60
    )