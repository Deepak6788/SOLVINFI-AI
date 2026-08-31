from django.db import models


# ============================================================
# EVENT MODEL
# ============================================================

class Event(models.Model):

    # ============================================================
    # Basic event information
    # ============================================================

    service = models.CharField(
        max_length=100
    )

    service_type = models.CharField(
        max_length=100
    )

    event_type = models.CharField(
        max_length=100
    )

    message = models.TextField()

    severity = models.CharField(
        max_length=20
    )

    timestamp = models.DateTimeField()

    # ============================================================
    # Incident information
    # ============================================================

    incident = models.BooleanField(
        default=False
    )

    priority = models.CharField(
        max_length=20,
        default="LOW"
    )

    incident_reason = models.TextField(
        blank=True,
        default=""
    )

    # ============================================================
    # Response information
    # ============================================================

    response_action = models.TextField(
        blank=True,
        default=""
    )

    solution = models.TextField(
        blank=True,
        default=""
    )

    # ============================================================
    # Incident lifecycle
    # ============================================================

    incident_status = models.CharField(
        max_length=30,
        default="DETECTED"
    )

    escalation_level = models.CharField(
        max_length=30,
        default="NONE"
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ============================================================
    # String representation
    # ============================================================

    def __str__(self):

        return (
            f"{self.service} - "
            f"{self.event_type} - "
            f"{self.severity}"
        )


# ============================================================
# INCIDENT RECORD MODEL
# ============================================================

class IncidentRecord(models.Model):

    # ============================================================
    # Basic incident information
    # ============================================================

    service = models.CharField(
        max_length=100
    )

    root_cause = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    root_cause_confidence = models.IntegerField(
        default=0
    )

    root_cause_reason = models.TextField(
        blank=True,
        default=""
    )

    # ============================================================
    # Incident classification
    # ============================================================

    priority = models.CharField(
        max_length=20,
        default="LOW"
    )

    correlation_score = models.IntegerField(
        default=0
    )

    highest_severity = models.CharField(
        max_length=20,
        default="INFO"
    )

    # ============================================================
    # Escalation
    # ============================================================

    escalation_required = models.BooleanField(
        default=False
    )

    escalation_score = models.IntegerField(
        default=0
    )

    escalation_level = models.CharField(
        max_length=30,
        default="NONE"
    )

    # ============================================================
    # Remediation
    # ============================================================

    remediation_action = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    remediation_status = models.CharField(
        max_length=30,
        default="NOT_EXECUTED"
    )

    # ============================================================
    # Verification
    # ============================================================

    verification_status = models.CharField(
        max_length=50,
        default="PENDING"
    )

    final_status = models.CharField(
        max_length=50,
        default="OPEN"
    )

    # ============================================================
    # Health measurements
    # ============================================================

    before_anomaly_score = models.IntegerField(
        default=0
    )

    after_anomaly_score = models.IntegerField(
        default=0
    )

    before_failure_rate = models.FloatField(
        default=0
    )

    after_failure_rate = models.FloatField(
        default=0
    )

    # ============================================================
    # Timestamps
    # ============================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ============================================================
    # String representation
    # ============================================================

    def __str__(self):

        return (
            f"{self.service} - "
            f"{self.root_cause} - "
            f"{self.final_status}"
        )