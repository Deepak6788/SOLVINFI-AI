def generate_alert(incident):

    if not incident.get("is_incident", False):
        return {
            "alert": False,
            "level": "NONE",
            "message": "No alert required."
        }

    priority = incident.get("priority")
    event_type = incident.get("event_type")

    if priority == "HIGH":
        return {
            "alert": True,
            "level": "CRITICAL",
            "message": f"Critical incident detected: {event_type}. Immediate attention required."
        }

    elif priority == "MEDIUM":
        return {
            "alert": True,
            "level": "WARNING",
            "message": f"Warning incident detected: {event_type}. Investigation recommended."
        }

    else:
        return {
            "alert": True,
            "level": "INFO",
            "message": f"Incident detected: {event_type}. Monitor the event."
        }


if __name__ == "__main__":

    test_incidents = [
        {
            "event_type": "DATABASE_TIMEOUT",
            "is_incident": True,
            "priority": "HIGH"
        },
        {
            "event_type": "LOGIN_FAILED",
            "is_incident": True,
            "priority": "MEDIUM"
        },
        {
            "event_type": "LOGIN_SUCCESS",
            "is_incident": False,
            "priority": "LOW"
        }
    ]

    for incident in test_incidents:

        alert = generate_alert(incident)

        print("Incident:")
        print(incident)

        print("Alert:")
        print(alert)

        print("-" * 50)