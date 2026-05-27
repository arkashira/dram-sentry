import unittest
import numpy as np
from src.ml.anomaly.zscore import ZScoreAnomalyDetector, AnomalyDetectionResult

class TestZScoreAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ZScoreAnomalyDetector(threshold=3.0)
        self.normal_data = np.array([1, 2, 3, 4, 5])
        self.anomalous_data = np.array([1, 2, 3, 4, 100])

    def test_detect_anomalies_normal_data(self):
        result = self.detector.detect_anomalies(self.normal_data)
        self.assertEqual(len(result.anomalies), 0)
        self.assertTrue(isinstance(result, AnomalyDetectionResult))

    def test_detect_anomalies_with_anomalies(self):
        result = self.detector.detect_anomalies(self.anomalous_data)
        self.assertEqual(len(result.anomalies), 1)
        self.assertEqual(result.anomalies[0], 100)
        self.assertGreater(result.z_scores[-1], self.detector.threshold)

    def test_update_threshold(self):
        self.detector.update_threshold(2.5)
        self.assertEqual(self.detector.threshold, 2.5)

    def test_empty_data_raises_error(self):
        with self.assertRaises(ValueError):
            self.detector.detect_anomalies([])

    def test_insufficient_variance_raises_error(self):
        with self.assertRaises(ValueError):
            self.detector.detect_anomalies([5, 5, 5, 5])

if __name__ == '__main__':
    unittest.main()