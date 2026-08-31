from detector import detect_incident


events = [
    {
        "service": "Deres",
        "event_type": "DATABASE_TIMEOUT",
        "severity": "ERROR"
    },
    {
        "service": "Deres",
        "event_type": "LOGIN_FAILED",
        "severity": "WARNING"
    },
    {
        "service": "Deres",
        "event_type": "LOGIN_SUCCESS",
        "severity": "INFO"
    }
]


for event in events:
    result = detect_incident(event)

    print("Event:", event["event_type"])
    print("Result:", result)
    print()