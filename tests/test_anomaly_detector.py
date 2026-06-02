import pytest

from src.anomaly_detector import ZScoreDetector, detect_anomalies

def test_zscore_detector_basic():
    detector = ZScoreDetector(window_size=5, threshold=2.0)
    normal = [10, 11, 9, 10.5, 10.2]
    for v in normal:
        is_anom, _ = detector.is_anomalous(v)
        assert not is_anom

    # Inject a clear outlier (Z-score >> 2.0)
    outlier = 30.0
    is_anom, z = detector.is_anomalous(outlier)
    assert is_anom
    assert abs(z) > 2.0

def test_detect_anomalies_returns_correct_indices():
    detector = ZScoreDetector(window_size=4, threshold=1.5)
    samples = [100, 102, 101, 99, 150, 98, 97]
    result = detect_anomalies(samples, detector)
    assert result == [(4, 150, pytest.approx(4.472))]  # Only index 4 is anomalous

def test_detector_requires_minimum_window():
    with pytest.raises(ValueError):
        ZScoreDetector(window_size=1, threshold=2.0)

def test_detector_requires_positive_threshold():
    with pytest.raises(ValueError):
        ZScoreDetector(window_size=5, threshold=0)

def test_empty_samples():
    detector = ZScoreDetector()
    assert detect_anomalies([], detector) == []

def test_single_sample_never_anomalous():
    detector = ZScoreDetector(window_size=5, threshold=1.0)
    assert detect_anomalies([100], detector) == []