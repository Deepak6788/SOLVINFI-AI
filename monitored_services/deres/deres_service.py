import random
import time
import requests
from datetime import datetime, timezone


SERVICE_NAME = "Deres"
SERVICE_TYPE = "Authentication & Identity"


EVENTS = [
    (
        "LOGIN_SUCCESS",
        "User authentication completed successfully.",
        "INFO"
    ),
    (
        "LOGIN_FAILED",
        "User authentication failed.",
        "WARNING"
    ),
    (
        "TOKEN_EXPIRED",
        "User authentication token expired.",
        "INFO"
    ),
    (
        "DATABASE_TIMEOUT",
        "Authentication database request timed out.",
        "ERROR"
    ),
    (
        "SERVICE_DOWN",
        "Authentication service is unavailable.",
        "ERROR"
    ),
    (
        "SYSTEM_CRASH",
        "Authentication service encountered a system crash.",
        "ERROR"
    ),
    (
        "UNAUTHORIZED_ACCESS",
        "Unauthorized access attempt detected.",
        "ERROR"
    ),
    (
        "ACCOUNT_LOCKED",
        "User account has been locked.",
        "WARNING"
    ),
    (
        "PERMISSION_DENIED",
        "User attempted to access a restricted resource.",
        "WARNING"
    )
]


def generate_event():

    event_type, message, severity = random.choice(EVENTS)

    return {
        "service": SERVICE_NAME,
        "service_type": SERVICE_TYPE,
        "event_type": event_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":

    while True:

        event = generate_event()

        print("Generated event:")
        print(event)

        try:
            response = requests.post(
                "http://127.0.0.1:9000/events",
                json=event
            )

            print("Server response:")
            print(response.json())

        except requests.exceptions.RequestException as error:

            print("Failed to send event:")
            print(error)

        print("-" * 60)

        time.sleep(2)