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
# DJANGO SETUP
# ============================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()


# ============================================================
# SOLVINFI MODULES
# ============================================================

from correlation.correlation_engine import (
    correlate_recent_events
)

from root_cause.analyzer import (
    analyze_root_cause
)

from response_engine.response_engine import (
    generate_response
)

from anomaly_detection.detector import (
    detect_anomaly
)

from escalation.escalation_engine import (
    evaluate_escalation
)

from remediation.remediation_engine import (
    run_remediation
)

from remediation.remediation_outcome import (
    calculate_post_remediation_health
)

from verification.verification_engine import (
    verify_remediation
)

from health_monitoring.health_snapshot import (
    capture_health
)

from services.models import (
    IncidentRecord
)


# ============================================================
# SAVE INCIDENT RECORD
# ============================================================

def save_incident_record(incident):

    before_health = incident.get(
        "before_health",
        {}
    )

    after_health = incident.get(
        "after_health",
        {}
    )

    remediation = incident.get(
        "remediation",
        {}
    )

    remediation_execution = incident.get(
        "remediation_execution",
        {}
    )

    verification = incident.get(
        "verification",
        {}
    )

    record = IncidentRecord.objects.create(

        # ====================================================
        # Basic incident information
        # ====================================================

        service=incident.get(
            "service",
            ""
        ),

        root_cause=incident.get(
            "root_cause",
            ""
        ),

        root_cause_confidence=incident.get(
            "root_cause_confidence",
            0
        ),

        root_cause_reason=incident.get(
            "root_cause_reason",
            ""
        ),

        # ====================================================
        # Incident classification
        # ====================================================

        priority=incident.get(
            "priority",
            "LOW"
        ),

        correlation_score=incident.get(
            "correlation_score",
            0
        ),

        highest_severity=incident.get(
            "highest_severity",
            "INFO"
        ),

        # ====================================================
        # Escalation
        # ====================================================

        escalation_required=incident.get(
            "escalation_required",
            False
        ),

        escalation_score=incident.get(
            "escalation_score",
            0
        ),

        escalation_level=incident.get(
            "escalation_level",
            "NONE"
        ),

        # ====================================================
        # Remediation
        # ====================================================

        remediation_action=remediation.get(
            "action",
            ""
        ),

        remediation_status=remediation_execution.get(
            "status",
            "NOT_EXECUTED"
        ),

        # ====================================================
        # Verification
        # ====================================================

        verification_status=verification.get(
            "status",
            "PENDING"
        ),

        final_status=incident.get(
            "final_status",
            "OPEN"
        ),

        # ====================================================
        # Health measurements
        # ====================================================

        before_anomaly_score=before_health.get(
            "anomaly_score",
            0
        ),

        after_anomaly_score=after_health.get(
            "anomaly_score",
            0
        ),

        before_failure_rate=before_health.get(
            "failure_rate",
            0
        ),

        after_failure_rate=after_health.get(
            "failure_rate",
            0
        )
    )

    return record


# ============================================================
# BUILD INCIDENT
# ============================================================

def build_incident():

    # ========================================================
    # 1. CORRELATION
    # ========================================================

    correlation = correlate_recent_events()

    # ========================================================
    # 2. ANOMALY DETECTION
    # ========================================================

    anomaly = detect_anomaly(
        service_name=correlation.get(
            "service"
        )
    )

    # ========================================================
    # 3. BEFORE HEALTH SNAPSHOT
    # ========================================================

    before_health = capture_health(
        service_name=correlation.get(
            "service"
        )
    )

    # ========================================================
    # 4. NO CORRELATED ACTIVITY
    # ========================================================

    if not correlation.get(
        "correlated"
    ):

        return {

            "status":
                "NO_CORRELATED_ACTIVITY",

            "message":
                correlation.get(
                    "message",
                    "No correlated events found."
                ),

            "anomaly":
                anomaly,

            "before_health":
                before_health
        }

    # ========================================================
    # 5. NORMAL ACTIVITY
    # ========================================================

    if not correlation.get(
        "incident_relevant"
    ):

        return {

            "status":
                "NORMAL_ACTIVITY",

            "service":
                correlation.get(
                    "service"
                ),

            "event_count":
                correlation.get(
                    "event_count"
                ),

            "event_counts":
                correlation.get(
                    "event_counts"
                ),

            "correlation_score":
                correlation.get(
                    "correlation_score"
                ),

            "anomaly":
                anomaly,

            "before_health":
                before_health,

            "message": (
                "Events were correlated, but "
                "the activity does not currently "
                "indicate a significant incident."
            )
        }

    # ========================================================
    # 6. ROOT CAUSE ANALYSIS
    # ========================================================

    root_cause = analyze_root_cause(
        correlation
    )

    # ========================================================
    # 7. BUILD INCIDENT
    # ========================================================

    incident = {

        "service":
            correlation.get(
                "service"
            ),

        "incident_relevant":
            True,

        "event_count":
            correlation.get(
                "event_count"
            ),

        "event_counts":
            correlation.get(
                "event_counts"
            ),

        "correlation_score":
            correlation.get(
                "correlation_score"
            ),

        "root_cause":
            root_cause.get(
                "root_cause"
            ),

        "root_cause_confidence":
            root_cause.get(
                "confidence"
            ),

        "root_cause_reason":
            root_cause.get(
                "reason"
            ),

        "highest_severity":
            correlation.get(
                "highest_severity"
            ),

        # ====================================================
        # Anomaly information
        # ====================================================

        "anomaly_detected":
            anomaly.get(
                "anomaly_detected",
                False
            ),

        "anomaly_score":
            anomaly.get(
                "anomaly_score",
                0
            ),

        "anomaly_risk":
            anomaly.get(
                "risk_level",
                "LOW"
            ),

        "anomaly_reason":
            anomaly.get(
                "reason",
                ""
            ),

        # ====================================================
        # Before health
        # ====================================================

        "before_health":
            before_health
    }

    # ========================================================
    # 8. DETERMINE PRIORITY
    # ========================================================

    if (
        incident[
            "highest_severity"
        ] == "ERROR"

        or

        incident[
            "anomaly_risk"
        ] == "CRITICAL"
    ):

        priority = "HIGH"

    elif (
        incident[
            "highest_severity"
        ] == "WARNING"

        or

        incident[
            "anomaly_risk"
        ] == "HIGH"
    ):

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # ========================================================
    # 9. RESPONSE GENERATION
    # ========================================================

    response_input = {

        "event_type":
            incident[
                "root_cause"
            ],

        "priority":
            priority
    }

    response = generate_response(
        response_input
    )

    # ========================================================
    # 10. ADD RESPONSE
    # ========================================================

    incident[
        "priority"
    ] = response.get(
        "priority",
        priority
    )

    incident[
        "response_action"
    ] = response.get(
        "action",
        ""
    )

    incident[
        "solution"
    ] = response.get(
        "solution",
        ""
    )

    # ========================================================
    # 11. ESCALATION
    # ========================================================

    escalation = evaluate_escalation(
        incident
    )

    incident[
        "escalation_required"
    ] = escalation.get(
        "escalation_required",
        False
    )

    incident[
        "escalation_score"
    ] = escalation.get(
        "escalation_score",
        0
    )

    incident[
        "escalation_level"
    ] = escalation.get(
        "escalation_level",
        "NONE"
    )

    incident[
        "escalation_reasons"
    ] = escalation.get(
        "reasons",
        []
    )

    incident[
        "escalation_recommendation"
    ] = escalation.get(
        "recommendation",
        ""
    )

    # ========================================================
    # 12. REMEDIATION
    # ========================================================

    remediation_result = run_remediation(

        root_cause=incident.get(
            "root_cause",
            ""
        ),

        severity=incident.get(
            "highest_severity",
            "INFO"
        ),

        priority=incident.get(
            "priority",
            "LOW"
        )
    )

    # ========================================================
    # 13. REMEDIATION INFORMATION
    # ========================================================

    remediation = remediation_result.get(
        "remediation",
        {}
    )

    execution = remediation_result.get(
        "execution",
        {}
    )

    incident[
        "remediation"
    ] = {

        "action":
            remediation.get(
                "action",
                "MANUAL_INVESTIGATION"
            ),

        "description":
            remediation.get(
                "description",
                ""
            ),

        "risk":
            remediation.get(
                "risk",
                "LOW"
            ),

        "requires_approval":
            remediation.get(
                "requires_approval",
                True
            )
    }

    incident[
        "remediation_execution"
    ] = {

        "status":
            execution.get(
                "status",
                "NOT_EXECUTED"
            ),

        "message":
            execution.get(
                "message",
                ""
            )
    }

    # ========================================================
    # 14. AFTER HEALTH
    # ========================================================

    after_health = calculate_post_remediation_health(

        before_health,

        remediation_result
    )

    incident[
        "after_health"
    ] = after_health

    # ========================================================
    # 15. VERIFY REMEDIATION
    # ========================================================

    verification = verify_remediation(

        before_health,

        after_health
    )

    incident[
        "verification"
    ] = verification

    # ========================================================
    # 16. FINAL DECISION
    # ========================================================

    verification_status = verification.get(
        "status"
    )

    if (
        verification_status
        == "REMEDIATION_EFFECTIVE"
    ):

        incident[
            "final_status"
        ] = "RESOLVED"

    elif (
        verification_status
        == "PARTIALLY_EFFECTIVE"
    ):

        incident[
            "final_status"
        ] = "MONITOR"

    else:

        incident[
            "final_status"
        ] = "ESCALATION_REQUIRED"

    # ========================================================
    # 17. SAVE INCIDENT TO DATABASE
    # ========================================================

    saved_record = save_incident_record(
        incident
    )

    # ========================================================
    # 18. ADD DATABASE RECORD ID
    # ========================================================

    incident[
        "incident_record_id"
    ] = saved_record.id

    # ========================================================
    # 19. FINAL SOLVINFI INTELLIGENCE
    # ========================================================

    return {

        "status":
            "INCIDENT_DETECTED",

        "incident":
            incident
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)

    print(
        "SOLVINFI INCIDENT ORCHESTRATOR"
    )

    print("=" * 70)

    result = build_incident()

    print(
        "\nFINAL INCIDENT INTELLIGENCE:\n"
    )

    print(result)

    print(
        "\n" + "=" * 70
    )