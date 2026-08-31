def detect_incident(event):

    severity = event.get("severity")
    event_type = event.get("event_type")

    if severity == "ERROR":
        return {
            "event_type": event_type,
            "is_incident": True,
            "priority": "HIGH",
            "reason": "An error event was detected."
        }

    elif severity == "WARNING":
        return {
            "event_type": event_type,
            "is_incident": True,
            "priority": "MEDIUM",
            "reason": "A warning event was detected."
        }

    else:
        return {
            "event_type": event_type,
            "is_incident": False,
            "priority": "LOW",
            "reason": "Informational event."
        }


def get_solution(event_type):

    solutions = {
        "LOGIN_FAILED": "Check authentication logs, verify user credentials and account status, and investigate repeated failed login attempts.",

        "LOGIN_SUCCESS": "Review the event details and investigate the underlying cause.",

        "DATABASE_TIMEOUT": "Check database availability, connection health, connection pool usage, and slow-running queries.",

        "TOKEN_EXPIRED": "Verify token expiration settings and refresh or renew the authentication token."
    }

    return solutions.get(
        event_type,
        "Review the event details and investigate the underlying cause."
    )