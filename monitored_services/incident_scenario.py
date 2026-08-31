import requests
import time
from datetime import datetime, timezone, timedelta


API_URL = "http://127.0.0.1:9000/events"

SERVICE_NAME = "Deres"
SERVICE_TYPE = "Authentication & Identity"


def send_event(event_type, message, severity, timestamp):

    event = {
        "service": SERVICE_NAME,
        "service_type": SERVICE_TYPE,
        "event_type": event_type,
        "message": message,
        "severity": severity,
        "timestamp": timestamp
    }

    print("\nSending event:")
    print(event)

    response = requests.post(
        API_URL,
        json=event
    )

    print("Response:")
    print(response.json())


def generate_incident_scenario():

    start_time = datetime.now(timezone.utc)

    events = [
        {
            "event_type": "LOGIN_FAILED",
            "message": "User authentication failed.",
            "severity": "WARNING"
        },
        {
            "event_type": "LOGIN_FAILED",
            "message": "User authentication failed.",
            "severity": "WARNING"
        },
        {
            "event_type": "LOGIN_FAILED",
            "message": "User authentication failed.",
            "severity": "WARNING"
        },
        {
            "event_type": "DATABASE_TIMEOUT",
            "message": "Authentication database request timed out.",
            "severity": "ERROR"
        },
        {
            "event_type": "SERVICE_DOWN",
            "message": "Authentication service is unavailable.",
            "severity": "ERROR"
        }
    ]

    for index, event in enumerate(events):

        timestamp = (
            start_time + timedelta(seconds=index * 10)
        ).isoformat()

        send_event(
            event["event_type"],
            event["message"],
            event["severity"],
            timestamp
        )

        time.sleep(1)


if __name__ == "__main__":

    print("=" * 60)
    print("SOLVINFI INCIDENT SCENARIO")
    print("=" * 60)

    print("\nGenerating authentication failure scenario...")

    generate_incident_scenario()

    print("\n" + "=" * 60)
    print("SCENARIO COMPLETE")
    print("=" * 60)