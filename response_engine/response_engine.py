def generate_response(incident):

    priority = incident.get("priority")
    event_type = incident.get("event_type")

    if event_type == "DATABASE_TIMEOUT":
        action = "Immediate investigation required."
        solution = (
            "Check database availability, connection health, "
            "connection pool usage, and slow-running queries."
        )

    elif event_type == "LOGIN_FAILED":
        action = "Review the incident and investigate if repeated."
        solution = (
            "Check authentication logs, verify user credentials and account status, "
            "and investigate repeated failed login attempts."
        )

    elif event_type == "TOKEN_EXPIRED":
        action = "Monitor the event."
        solution = (
            "Refresh the authentication token or ask the user to authenticate again "
            "if the expiration is unexpected."
        )

    elif event_type == "SERVICE_DOWN":
        action = "Immediate investigation required."
        solution = (
            "Check service health, application logs, server availability, "
            "and restart the service if necessary."
        )

    elif event_type == "SYSTEM_CRASH":
        action = "Immediate investigation required."
        solution = (
            "Check system logs, crash reports, resource usage, "
            "and recent application or configuration changes."
        )

    elif event_type == "UNAUTHORIZED_ACCESS":
        action = "Immediate security investigation required."
        solution = (
            "Review authentication and access logs, identify the source "
            "of the unauthorized access, and verify affected accounts."
        )

    elif event_type == "ACCOUNT_LOCKED":
        action = "Review the incident and investigate if repeated."
        solution = (
            "Verify the reason for account lockout, review authentication "
            "attempts, and unlock the account if the activity is legitimate."
        )

    elif event_type == "PERMISSION_DENIED":
        action = "Review the incident and investigate if repeated."
        solution = (
            "Check user permissions, access policies, and resource authorization "
            "settings to determine why access was denied."
        )

    else:
        if priority == "HIGH":
            action = "Immediate investigation required."
        elif priority == "MEDIUM":
            action = "Review the incident and investigate if repeated."
        else:
            action = "Monitor the event."

        solution = "Review the event details and investigate the underlying cause."

    return {
        "event_type": event_type,
        "priority": priority,
        "action": action,
        "solution": solution
    }


if __name__ == "__main__":

    test_incidents = [
    {
        "event_type": "DATABASE_TIMEOUT",
        "priority": "HIGH"
    },
    {
        "event_type": "LOGIN_FAILED",
        "priority": "MEDIUM"
    },
    {
        "event_type": "TOKEN_EXPIRED",
        "priority": "LOW"
    },
    {
        "event_type": "SERVICE_DOWN",
        "priority": "HIGH"
    },
    {
        "event_type": "SYSTEM_CRASH",
        "priority": "HIGH"
    },
    {
        "event_type": "UNAUTHORIZED_ACCESS",
        "priority": "HIGH"
    },
    {
        "event_type": "ACCOUNT_LOCKED",
        "priority": "MEDIUM"
    },
    {
        "event_type": "PERMISSION_DENIED",
        "priority": "MEDIUM"
    }
]

    for incident in test_incidents:

        response = generate_response(incident)

        print("Incident:")
        print(incident)

        print("Response:")
        print(response)

        print("-" * 50)