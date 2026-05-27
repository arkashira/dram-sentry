import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

class VolumeCalculator:
    """Calculates optimal volume recommendations based on historical usage data."""

    def __init__(self, usage_data: List[Dict], window_days: int = 30):
        """
        Initialize with usage data and optional time window.

        Args:
            usage_data: List of dictionaries containing 'date' and 'usage' keys
            window_days: Number of days to consider for average calculation (default: 30)
        """
        self.usage_data = usage_data
        self.window_days = window_days
        self.logger = logging.getLogger(__name__)

    def calculate_volume(self) -> int:
        """Calculate average usage over the specified time window."""
        if not self.usage_data:
            self.logger.warning("No usage data provided")
            return 0

        try:
            df = pd.DataFrame(self.usage_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date')

            if len(df) == 0:
                self.logger.warning("Empty DataFrame after date conversion")
                return 0

            cutoff_date = df['date'].max() - timedelta(days=self.window_days)
            recent_data = df[df['date'] > cutoff_date]

            if len(recent_data) == 0:
                self.logger.warning(f"No data in the last {self.window_days} days")
                return 0

            average_usage = recent_data['usage'].mean()
            return max(0, int(round(average_usage)))  # Ensure non-negative

        except Exception as e:
            self.logger.error(f"Error calculating volume: {str(e)}")
            return 0

    def get_recommendation(self, threshold: int = 5) -> Dict:
        """
        Get volume recommendation based on calculated usage.

        Args:
            threshold: Minimum volume to trigger a 'buy' action (default: 5)

        Returns:
            Dictionary with 'volume', 'action', and 'confidence' keys
        """
        volume = self.calculate_volume()
        action = 'buy' if volume >= threshold else 'hold'
        confidence = min(100, volume * 10)  # Simple confidence metric

        return {
            'volume': volume,
            'action': action,
            'confidence': confidence,
            'threshold': threshold
        }