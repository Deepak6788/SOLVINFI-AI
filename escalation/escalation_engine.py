def evaluate_escalation(incident):

    priority = incident.get(
        "priority",
        "LOW"
    )

    severity = incident.get(
        "highest_severity",
        "INFO"
    )

    correlation_score = incident.get(
        "correlation_score",
        0
    )

    root_cause_confidence = incident.get(
        "root_cause_confidence",
        0
    )

    anomaly_score = incident.get(
        "anomaly_score",
        0
    )

    anomaly_risk = incident.get(
        "anomaly_risk",
        "LOW"
    )

    escalation_score = 0

    reasons = []

    # --------------------------------------------------
    # Severity
    # --------------------------------------------------

    if severity == "ERROR":

        escalation_score += 30

        reasons.append(
            "ERROR severity detected"
        )

    elif severity == "WARNING":

        escalation_score += 15

        reasons.append(
            "WARNING severity detected"
        )

    # --------------------------------------------------
    # Priority
    # --------------------------------------------------

    if priority == "HIGH":

        escalation_score += 25

        reasons.append(
            "Incident has HIGH priority"
        )

    elif priority == "MEDIUM":

        escalation_score += 10

    # --------------------------------------------------
    # Correlation strength
    # --------------------------------------------------

    if correlation_score >= 80:

        escalation_score += 20

        reasons.append(
            "Strong correlation between related events"
        )

    elif correlation_score >= 60:

        escalation_score += 10

    # --------------------------------------------------
    # Root-cause confidence
    # --------------------------------------------------

    if root_cause_confidence >= 90:

        escalation_score += 15

        reasons.append(
            "Root cause identified with high confidence"
        )

    elif root_cause_confidence >= 70:

        escalation_score += 8

    # --------------------------------------------------
    # Anomaly risk
    # --------------------------------------------------

    if anomaly_risk == "CRITICAL":

        escalation_score += 25

        reasons.append(
            "Critical anomalous behavior detected"
        )

    elif anomaly_risk == "HIGH":

        escalation_score += 15

        reasons.append(
            "High anomalous behavior detected"
        )

    elif anomaly_score >= 50:

        escalation_score += 10

        reasons.append(
            "Unusual event pattern detected"
        )

    # --------------------------------------------------
    # Cap score
    # --------------------------------------------------

    escalation_score = min(
        escalation_score,
        100
    )

    # --------------------------------------------------
    # Determine escalation level
    # --------------------------------------------------

    if escalation_score >= 80:

        escalation_level = "IMMEDIATE"

    elif escalation_score >= 60:

        escalation_level = "URGENT"

    elif escalation_score >= 40:

        escalation_level = "REVIEW"

    else:

        escalation_level = "NONE"

    # --------------------------------------------------
    # Determine whether escalation is required
    # --------------------------------------------------

    escalation_required = (
        escalation_level != "NONE"
    )

    # --------------------------------------------------
    # Generate recommendation
    # --------------------------------------------------

    if escalation_level == "IMMEDIATE":

        recommendation = (
            "Immediately notify the responsible "
            "operations team and begin incident response."
        )

    elif escalation_level == "URGENT":

        recommendation = (
            "Notify the responsible operations team "
            "and investigate the incident promptly."
        )

    elif escalation_level == "REVIEW":

        recommendation = (
            "Add the incident to the operations review queue."
        )

    else:

        recommendation = (
            "No escalation required. Continue monitoring."
        )

    return {

        "escalation_required":
            escalation_required,

        "escalation_score":
            escalation_score,

        "escalation_level":
            escalation_level,

        "reasons":
            reasons,

        "recommendation":
            recommendation
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SOLVINFI ESCALATION ENGINE")
    print("=" * 70)

    test_incident = {

        "priority": "HIGH",

        "highest_severity": "ERROR",

        "correlation_score": 85,

        "root_cause_confidence": 95,

        "anomaly_score": 80,

        "anomaly_risk": "CRITICAL"
    }

    result = evaluate_escalation(
        test_incident
    )

    print("\nEscalation Decision:\n")

    print(result)

    print("\n" + "=" * 70)