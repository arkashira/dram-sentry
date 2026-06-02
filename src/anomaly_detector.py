import math
from typing import List, Tuple, Optional

from prometheus_client import Counter, Gauge

# Prometheus metrics
ANOMALY_DETECTIONS_TOTAL = Counter(
    "dram_sentry_anomaly_detections_total",
    "Total number of anomaly detections performed",
)
ANOMALY_COUNT = Counter(
    "dram_sentry_anomalies_total",
    "Total number of anomalies detected",
)
CURRENT_ZSCORE = Gauge(
    "dram_sentry_current_zscore",
    "Current Z-score of the latest DRAM usage sample",
)

class ZScoreDetector:
    """
    Z-score based anomaly detector with a sliding window.

    Features:
    - Rolling window for mean/std computation (avoids bias from fixed-size windows).
    - Early rejection for insufficient data (window_size < 2).
    - Absolute Z-score thresholding for anomaly detection.
    - Prometheus metrics integration for observability.
    """

    def __init__(self, window_size: int = 20, threshold: float = 3.0):
        if window_size <= 1:
            raise ValueError("window_size must be > 1")
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.window_size = window_size
        self.threshold = threshold
        self._values: List[float] = []

    def _update_window(self, value: float) -> None:
        """Add a new value and enforce window size."""
        self._values.append(value)
        if len(self._values) > self.window_size:
            self._values.pop(0)

    def _mean(self) -> float:
        """Compute mean of the current window."""
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)

    def _std(self) -> float:
        """Compute standard deviation of the current window (sample std)."""
        if len(self._values) < 2:
            return 0.0
        mean = self._mean()
        variance = sum((x - mean) ** 2 for x in self._values) / (len(self._values) - 1)
        return math.sqrt(variance)

    def is_anomalous(self, value: float) -> Tuple[bool, float]:
        """
        Check if a value is anomalous using Z-score.

        Returns:
            Tuple[bool, float]: (is_anomaly, z_score)
                - is_anomaly: True if |z_score| > threshold.
                - z_score: (value - mean) / std (0 if std=0).
        """
        # Early exit: insufficient data to compute Z-score
        if len(self._values) < 2:
            self._update_window(value)
            CURRENT_ZSCORE.set(0.0)
            return False, 0.0

        mean = self._mean()
        std = self._std()
        z = 0.0 if std == 0 else (value - mean) / std
        CURRENT_ZSCORE.set(abs(z))

        is_anomaly = abs(z) > self.threshold
        if is_anomaly:
            ANOMALY_COUNT.inc()
        self._update_window(value)
        ANOMALY_DETECTIONS_TOTAL.inc()  # Track every detection attempt
        return is_anomaly, z

def detect_anomalies(
    samples: List[float],
    detector: Optional[ZScoreDetector] = None,
) -> List[Tuple[int, float, float]]:
    """
    Scan samples for anomalies using a ZScoreDetector.

    Args:
        samples: List of DRAM usage measurements (e.g., percentages).
        detector: Optional pre-configured detector. If None, uses defaults.

    Returns:
        List[Tuple[int, float, float]]: Anomalies as (index, value, z_score).
    """
    detector = detector or ZScoreDetector()
    anomalies: List[Tuple[int, float, float]] = []

    for idx, value in enumerate(samples):
        is_anomaly, z = detector.is_anomalous(value)
        if is_anomaly:
            anomalies.append((idx, value, z))

    return anomalies