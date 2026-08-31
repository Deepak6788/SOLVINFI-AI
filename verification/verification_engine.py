class VerificationEngine:

    def compare(self, before, after):
        """
        Compare system health before and after remediation.
        """

        before_score = before.get(
            "anomaly_score",
            0
        )

        after_score = after.get(
            "anomaly_score",
            0
        )

        before_failure_rate = before.get(
            "failure_rate",
            0
        )

        after_failure_rate = after.get(
            "failure_rate",
            0
        )

        before_error_count = before.get(
            "error_count",
            0
        )

        after_error_count = after.get(
            "error_count",
            0
        )

        before_warning_count = before.get(
            "warning_count",
            0
        )

        after_warning_count = after.get(
            "warning_count",
            0
        )

        # ==================================================
        # Calculate improvements
        # ==================================================

        anomaly_improvement = (
            before_score - after_score
        )

        failure_rate_improvement = (
            before_failure_rate
            - after_failure_rate
        )

        error_improvement = (
            before_error_count
            - after_error_count
        )

        warning_improvement = (
            before_warning_count
            - after_warning_count
        )

        # ==================================================
        # Determine verification status
        # ==================================================

        improvements = 0

        if anomaly_improvement > 0:
            improvements += 1

        if failure_rate_improvement > 0:
            improvements += 1

        if error_improvement > 0:
            improvements += 1

        if warning_improvement > 0:
            improvements += 1

        # ==================================================
        # Effective
        # ==================================================

        if improvements >= 3:

            status = "REMEDIATION_EFFECTIVE"

            message = (
                "System health improved significantly "
                "after the remediation action."
            )

        # ==================================================
        # Partially effective
        # ==================================================

        elif improvements >= 1:

            status = "PARTIALLY_EFFECTIVE"

            message = (
                "Some system health indicators improved, "
                "but the incident may still require "
                "investigation."
            )

        # ==================================================
        # Failed
        # ==================================================

        else:

            status = "REMEDIATION_FAILED"

            message = (
                "No meaningful improvement was detected "
                "after the remediation action."
            )

        return {

            "status": status,

            "message": message,

            "before": {

                "anomaly_score": before_score,

                "failure_rate": before_failure_rate,

                "error_count": before_error_count,

                "warning_count": before_warning_count
            },

            "after": {

                "anomaly_score": after_score,

                "failure_rate": after_failure_rate,

                "error_count": after_error_count,

                "warning_count": after_warning_count
            },

            "improvement": {

                "anomaly_score":
                    anomaly_improvement,

                "failure_rate":
                    failure_rate_improvement,

                "error_count":
                    error_improvement,

                "warning_count":
                    warning_improvement
            }
        }


def verify_remediation(before, after):

    engine = VerificationEngine()

    return engine.compare(
        before,
        after
    )


# ============================================================
# Standalone demonstration
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "SOLVINFI REMEDIATION VERIFICATION"
    )

    print("=" * 60)

    before = {

        "anomaly_score": 100,

        "failure_rate": 95.0,

        "error_count": 11,

        "warning_count": 8
    }

    after = {

        "anomaly_score": 30,

        "failure_rate": 20.0,

        "error_count": 2,

        "warning_count": 3
    }

    result = verify_remediation(
        before,
        after
    )

    print("\nVerification Result:\n")

    print(result)

    print("\n" + "=" * 60)