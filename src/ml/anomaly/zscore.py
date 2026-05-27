import numpy as np
from typing import Union, List, Optional
from dataclasses import dataclass

@dataclass
class AnomalyDetectionResult:
    """Structured output for anomaly detection results."""
    anomalies: np.ndarray
    z_scores: np.ndarray
    mean: float
    std_dev: float
    threshold: float

class ZScoreAnomalyDetector:
    """Robust Z-score anomaly detector with configurable threshold and validation."""

    def __init__(self, threshold: float = 3.5, min_std_dev: float = 1e-6):
        """
        Initialize the detector with a threshold and minimum standard deviation.

        Args:
            threshold (float): Z-score threshold for anomaly detection (default: 3.5).
            min_std_dev (float): Minimum standard deviation to avoid division by zero (default: 1e-6).
        """
        self.threshold = threshold
        self.min_std_dev = min_std_dev

    def detect_anomalies(self, data: Union[List[float], np.ndarray]) -> AnomalyDetectionResult:
        """
        Detect anomalies using Z-score method.

        Args:
            data (Union[List[float], np.ndarray]): Input data for anomaly detection.

        Returns:
            AnomalyDetectionResult: Structured output containing anomalies, z-scores, mean, std_dev, and threshold.

        Raises:
            ValueError: If input data is empty or has insufficient variance.
        """
        data = np.asarray(data)
        if len(data) == 0:
            raise ValueError("Input data cannot be empty.")

        mean = np.mean(data)
        std_dev = max(np.std(data), self.min_std_dev)  # Avoid division by zero

        if std_dev < self.min_std_dev:
            raise ValueError("Insufficient variance in data (std_dev too low).")

        z_scores = np.abs((data - mean) / std_dev)
        anomalies = data[z_scores > self.threshold]

        return AnomalyDetectionResult(
            anomalies=anomalies,
            z_scores=z_scores,
            mean=mean,
            std_dev=std_dev,
            threshold=self.threshold
        )

    def update_threshold(self, new_threshold: float) -> None:
        """Update the Z-score threshold for anomaly detection."""
        if new_threshold <= 0:
            raise ValueError("Threshold must be a positive number.")
        self.threshold = new_threshold