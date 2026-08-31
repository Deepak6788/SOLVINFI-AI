import os

from datetime import datetime, timezone


# ============================================================
# DJANGO SETUP
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()


# ============================================================
# FASTAPI
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


# ============================================================
# DATABASE MODELS
# ============================================================

from services.models import (
    Event,
    IncidentRecord
)


# ============================================================
# INCIDENT DETECTION
# ============================================================

from incidents.detector import (
    detect_incident,
    get_solution
)


# ============================================================
# RESPONSE ENGINE
# ============================================================

from response_engine.response_engine import (
    generate_response
)


# ============================================================
# INCIDENT ORCHESTRATOR
# ============================================================

from incident_orchestrator.orchestrator import (
    build_incident
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SOLVINFI Event Engine",
    description="SOLVINFI Intelligent Incident Management API",
    version="1.0.0"
)


# ============================================================
# CORS
#
# Allows the dashboard running through VS Code Live Server
# to communicate with FastAPI.
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# ============================================================
# GET /dashboard
#
# Allows FastAPI to serve the dashboard directly.
# ============================================================

@app.get("/dashboard")
def dashboard():

    dashboard_path = os.path.join(
        BASE_DIR,
        "dashboard",
        "index.html"
    )

    if not os.path.exists(
        dashboard_path
    ):

        raise HTTPException(
            status_code=404,
            detail="Dashboard file not found."
        )

    return FileResponse(
        dashboard_path
    )


# ============================================================
# POST /events
#
# Receive and process a new monitoring event.
# ============================================================

@app.post("/events")
def receive_event(event: dict):

    print("\n" + "=" * 60)
    print("SOLVINFI RECEIVED EVENT")
    print("=" * 60)

    print(event)


    # ========================================================
    # 1. INCIDENT DETECTION
    # ========================================================

    incident = detect_incident(
        event
    )

    print("\nIncident analysis:")
    print(incident)


    # ========================================================
    # 2. RESPONSE GENERATION
    # ========================================================

    response = generate_response(
        incident
    )

    print("\nImmediate response:")
    print(response)


    # ========================================================
    # 3. EVENT-SPECIFIC SOLUTION
    # ========================================================

    solution = get_solution(
        event.get(
            "event_type"
        )
    )

    response["solution"] = solution


    # ========================================================
    # 4. STORE EVENT
    # ========================================================

    saved_event = Event.objects.create(

        service=event.get(
            "service"
        ),

        service_type=event.get(
            "service_type"
        ),

        event_type=event.get(
            "event_type"
        ),

        message=event.get(
            "message"
        ),

        severity=event.get(
            "severity"
        ),

        timestamp=event.get(
            "timestamp"
        ),

        incident=incident.get(
            "is_incident",
            False
        ),

        priority=incident.get(
            "priority",
            "LOW"
        ),

        incident_reason=incident.get(
            "reason",
            ""
        ),

        response_action=response.get(
            "action",
            ""
        ),

        solution=response.get(
            "solution",
            ""
        ),

        incident_status=(
            "DETECTED"
            if incident.get(
                "is_incident",
                False
            )
            else "CLOSED"
        ),

        escalation_level="NONE"
    )


    # ========================================================
    # 5. RUN COMPLETE SOLVINFI PIPELINE
    # ========================================================

    intelligence = build_incident()

    print("\nSOLVINFI Intelligence:")
    print(intelligence)


    # ========================================================
    # 6. GET INCIDENT INTELLIGENCE
    # ========================================================

    intelligence_incident = intelligence.get(
        "incident",
        {}
    )


    escalation_level = (
        intelligence_incident.get(
            "escalation_level",
            "NONE"
        )
    )


    # ========================================================
    # 7. UPDATE INCIDENT LIFECYCLE
    # ========================================================

    if intelligence.get(
        "status"
    ) == "INCIDENT_DETECTED":

        if escalation_level in [
            "IMMEDIATE",
            "URGENT"
        ]:

            saved_event.incident_status = (
                "ESCALATED"
            )

        else:

            saved_event.incident_status = (
                "INVESTIGATING"
            )

        saved_event.escalation_level = (
            escalation_level
        )

        saved_event.save(
            update_fields=[
                "incident_status",
                "escalation_level"
            ]
        )


    # ========================================================
    # 8. RETURN RESULT
    # ========================================================

    return {

        "status":
            "stored",

        "event_id":
            saved_event.id,

        "incident":
            incident,

        "response":
            response,

        "intelligence":
            intelligence,

        "lifecycle": {

            "incident_status":
                saved_event.incident_status,

            "escalation_level":
                saved_event.escalation_level,

            "resolved_at": (

                saved_event.resolved_at.isoformat()

                if saved_event.resolved_at

                else None
            )
        }
    }


# ============================================================
# GET /events
#
# Return all stored events.
# ============================================================

@app.get("/events")
def get_events():

    events = Event.objects.all().order_by(
        "-timestamp"
    )

    return [

        {
            "id":
                event.id,

            "service":
                event.service,

            "service_type":
                event.service_type,

            "event_type":
                event.event_type,

            "message":
                event.message,

            "severity":
                event.severity,

            "timestamp":
                event.timestamp.isoformat(),

            "incident":
                event.incident,

            "priority":
                event.priority,

            "incident_reason":
                event.incident_reason,

            "response_action":
                event.response_action,

            "solution":
                event.solution,

            "incident_status":
                event.incident_status,

            "escalation_level":
                event.escalation_level,

            "resolved_at": (

                event.resolved_at.isoformat()

                if event.resolved_at

                else None
            )
        }

        for event in events
    ]


# ============================================================
# GET /events/latest
#
# Return the latest event.
# ============================================================

@app.get("/events/latest")
def get_latest_event():

    event = Event.objects.order_by(
        "-id"
    ).first()


    if not event:

        return {
            "message":
                "No events found"
        }


    return {

        "id":
            event.id,

        "service":
            event.service,

        "service_type":
            event.service_type,

        "event_type":
            event.event_type,

        "message":
            event.message,

        "severity":
            event.severity,

        "timestamp":
            event.timestamp.isoformat(),

        "incident":
            event.incident,

        "priority":
            event.priority,

        "incident_reason":
            event.incident_reason,

        "response_action":
            event.response_action,

        "solution":
            event.solution,

        "incident_status":
            event.incident_status,

        "escalation_level":
            event.escalation_level,

        "resolved_at": (

            event.resolved_at.isoformat()

            if event.resolved_at

            else None
        )
    }


# ============================================================
# GET /incidents
#
# Return event-level incidents.
# ============================================================

@app.get("/incidents")
def get_incidents():

    incidents = Event.objects.filter(
        incident=True
    ).order_by(
        "-timestamp"
    )

    return [

        {
            "id":
                event.id,

            "service":
                event.service,

            "service_type":
                event.service_type,

            "event_type":
                event.event_type,

            "message":
                event.message,

            "severity":
                event.severity,

            "priority":
                event.priority,

            "incident_reason":
                event.incident_reason,

            "response_action":
                event.response_action,

            "solution":
                event.solution,

            "incident_status":
                event.incident_status,

            "escalation_level":
                event.escalation_level,

            "resolved_at": (

                event.resolved_at.isoformat()

                if event.resolved_at

                else None
            ),

            "timestamp":
                event.timestamp.isoformat()
        }

        for event in incidents
    ]


# ============================================================
# GET /incidents/history
#
# Return saved SOLVINFI incident records.
# ============================================================

@app.get("/incidents/history")
def get_incident_history():

    records = IncidentRecord.objects.all().order_by(
        "-created_at"
    )

    return [

        {
            "id":
                record.id,

            "service":
                record.service,

            "root_cause":
                record.root_cause,

            "root_cause_confidence":
                record.root_cause_confidence,

            "root_cause_reason":
                record.root_cause_reason,

            "priority":
                record.priority,

            "correlation_score":
                record.correlation_score,

            "highest_severity":
                record.highest_severity,

            "escalation_required":
                record.escalation_required,

            "escalation_score":
                record.escalation_score,

            "escalation_level":
                record.escalation_level,

            "remediation_action":
                record.remediation_action,

            "remediation_status":
                record.remediation_status,

            "verification_status":
                record.verification_status,

            "final_status":
                record.final_status,

            "before_anomaly_score":
                record.before_anomaly_score,

            "after_anomaly_score":
                record.after_anomaly_score,

            "before_failure_rate":
                record.before_failure_rate,

            "after_failure_rate":
                record.after_failure_rate,

            "created_at":
                record.created_at.isoformat(),

            "updated_at":
                record.updated_at.isoformat()
        }

        for record in records
    ]


# ============================================================
# GET /incidents/history/{incident_id}
#
# Return one saved incident.
# ============================================================

@app.get(
    "/incidents/history/{incident_id}"
)
def get_incident_history_by_id(
    incident_id: int
):

    try:

        record = IncidentRecord.objects.get(
            id=incident_id
        )

    except IncidentRecord.DoesNotExist:

        raise HTTPException(
            status_code=404,
            detail="Incident record not found."
        )


    return {

        "id":
            record.id,

        "service":
            record.service,

        "root_cause":
            record.root_cause,

        "root_cause_confidence":
            record.root_cause_confidence,

        "root_cause_reason":
            record.root_cause_reason,

        "priority":
            record.priority,

        "correlation_score":
            record.correlation_score,

        "highest_severity":
            record.highest_severity,

        "escalation_required":
            record.escalation_required,

        "escalation_score":
            record.escalation_score,

        "escalation_level":
            record.escalation_level,

        "remediation_action":
            record.remediation_action,

        "remediation_status":
            record.remediation_status,

        "verification_status":
            record.verification_status,

        "final_status":
            record.final_status,

        "before_health": {

            "anomaly_score":
                record.before_anomaly_score,

            "failure_rate":
                record.before_failure_rate
        },

        "after_health": {

            "anomaly_score":
                record.after_anomaly_score,

            "failure_rate":
                record.after_failure_rate
        },

        "created_at":
            record.created_at.isoformat(),

        "updated_at":
            record.updated_at.isoformat()
    }


# ============================================================
# PATCH /incidents/{incident_id}/status
#
# Update the saved SOLVINFI incident status.
#
# IMPORTANT:
# /incidents/history uses IncidentRecord.
# Therefore this endpoint also updates IncidentRecord.
# ============================================================

@app.patch(
    "/incidents/{incident_id}/status"
)
def update_incident_status(
    incident_id: int,
    status: str
):

    allowed_statuses = [

        "DETECTED",

        "INVESTIGATING",

        "ESCALATED",

        "RESOLVED",

        "CLOSED"
    ]


    # --------------------------------------------------------
    # Convert status to uppercase
    # --------------------------------------------------------

    status = status.upper()


    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Allowed values: "
                + ", ".join(
                    allowed_statuses
                )
            )
        )


    # --------------------------------------------------------
    # Find the IncidentRecord
    #
    # THIS IS THE IMPORTANT FIX.
    #
    # Previously this endpoint searched Event.
    # The dashboard/history uses IncidentRecord.
    # --------------------------------------------------------

    try:

        record = IncidentRecord.objects.get(
            id=incident_id
        )

    except IncidentRecord.DoesNotExist:

        raise HTTPException(
            status_code=404,
            detail="Incident record not found."
        )


    # --------------------------------------------------------
    # Update final status
    # --------------------------------------------------------

    record.final_status = status


    # --------------------------------------------------------
    # Save record
    #
    # updated_at is automatically updated by Django
    # because the model uses auto_now=True.
    # --------------------------------------------------------

    record.save()


    # --------------------------------------------------------
    # Return updated result
    # --------------------------------------------------------

    return {

        "status":
            "updated",

        "incident_id":
            record.id,

        "incident_status":
            record.final_status,

        "escalation_level":
            record.escalation_level,

        "verification_status":
            record.verification_status,

        "updated_at":
            record.updated_at.isoformat()
    }