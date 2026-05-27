import os
from datetime import datetime
from typing import Dict

import sentry_sdk

class AlertFormatter:
    """
    Formats alert data into a markdown message using the template stored at
    `/opt/axentx/dram-sentry/templates/alert_message.md`.

    Features:
    - Loads template from disk (validates existence).
    - Substitutes placeholders with alert data.
    - Auto-injects timestamp if missing.
    - Logs formatted payload to Sentry for auditability.
    """

    TEMPLATE_PATH = "/opt/axentx/dram-sentry/templates/alert_message.md"

    def __init__(self) -> None:
        self._template = self._load_template()

    def _load_template(self) -> str:
        """Load and validate the template file."""
        if not os.path.isfile(self.TEMPLATE_PATH):
            raise FileNotFoundError(
                f"Alert template not found at {self.TEMPLATE_PATH}. "
                "Ensure the file exists or update TEMPLATE_PATH."
            )
        with open(self.TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def format(self, alert_data: Dict[str, str]) -> str:
        """
        Populate the template with values from `alert_data`.

        Args:
            alert_data: Dict with keys:
                - impact_per_gb (str): e.g., "0.45"
                - estimated_total_cost (str): e.g., "12,300"
                - historical_context (str)
                - recommended_actions (str)
                - snooze_options (str): e.g., "24h / 72h"
                - timestamp (str, optional): ISO timestamp; defaults to UTC now.

        Returns:
            str: Fully formatted markdown alert.

        Raises:
            ValueError: If required keys are missing.
        """
        # Validate required keys
        required_keys = {
            "impact_per_gb", "estimated_total_cost",
            "historical_context", "recommended_actions", "snooze_options"
        }
        missing_keys = required_keys - set(alert_data.keys())
        if missing_keys:
            raise ValueError(f"Missing required alert data keys: {missing_keys}")

        # Inject timestamp if missing
        data = alert_data.copy()
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Substitute placeholders
        message = self._template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))

        # Log to Sentry for auditability
        sentry_sdk.capture_message(
            "DRAM alert formatted",
            level="info",
            hint={"alert_payload": message},
        )
        return message