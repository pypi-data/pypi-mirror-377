"""
Test Real-time Data Monitoring Module
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from openmlcrawler.core.monitoring import (
    RealTimeMonitor, AlertManager, AnomalyDetector, PerformanceMonitor,
    AlertLevel, AlertChannel, AlertRule, Alert,
    create_real_time_monitor, setup_email_alerts, setup_slack_alerts, setup_webhook_alerts
)


class TestAlertManager:
    """Test AlertManager functionality"""

    def test_alert_rule_creation(self):
        """Test creating alert rules"""
        manager = AlertManager()

        def test_condition(data):
            return data.get('value', 0) > 10

        rule = AlertRule(
            name="test_rule",
            condition=test_condition,
            level=AlertLevel.WARNING,
            message="Test alert",
            cooldown_minutes=5
        )

        manager.add_rule(rule)
        assert len(manager.rules) == 1  # 1 new rule

    def test_alert_triggering(self):
        """Test alert triggering"""
        manager = AlertManager()

        def test_condition(data):
            return data.get('value', 0) > 5

        rule = AlertRule(
            name="test_rule",
            condition=test_condition,
            level=AlertLevel.WARNING,
            message="Value too high",
            cooldown_minutes=5
        )

        manager.add_rule(rule)

        # Test triggering alert
        alerts = manager.check_alerts({'value': 10})
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.WARNING
        assert alerts[0].message == "Value too high"

        # Test not triggering alert
        alerts = manager.check_alerts({'value': 3})
        assert len(alerts) == 0

    def test_cooldown_mechanism(self):
        """Test alert cooldown"""
        manager = AlertManager()

        def test_condition(data):
            return True

        rule = AlertRule(
            name="test_rule",
            condition=test_condition,
            level=AlertLevel.WARNING,
            message="Test alert",
            cooldown_minutes=0  # No cooldown for test
        )

        manager.add_rule(rule)

        # First alert should trigger
        alerts1 = manager.check_alerts({'value': 1})
        assert len(alerts1) == 1

        # Second alert should also trigger due to no cooldown
        alerts2 = manager.check_alerts({'value': 1})
        assert len(alerts2) == 1


class TestAnomalyDetector:
    """Test AnomalyDetector functionality"""

    def test_anomaly_detection_setup(self):
        """Test anomaly detector initialization"""
        detector = AnomalyDetector()
        assert not detector.is_trained
        assert len(detector.models) == 0

    def test_baseline_update(self):
        """Test baseline statistics update"""
        detector = AnomalyDetector()

        data_stream = [
            {'feature1': 1.0, 'feature2': 2.0},
            {'feature1': 2.0, 'feature2': 3.0},
            {'feature1': 3.0, 'feature2': 4.0}
        ]

        detector.update_baseline(data_stream, ['feature1', 'feature2'])

        assert 'feature1' in detector.baseline_stats
        assert 'feature2' in detector.baseline_stats
        assert detector.baseline_stats['feature1']['mean'] == 2.0

    def test_anomaly_model_training(self):
        """Test anomaly model training"""
        detector = AnomalyDetector()

        # Generate normal data
        np.random.seed(42)
        data_stream = []
        for _ in range(100):
            data_stream.append({
                'feature1': np.random.normal(0, 1),
                'feature2': np.random.normal(0, 1)
            })

        detector.update_baseline(data_stream, ['feature1', 'feature2'])
        detector.train_anomaly_model(data_stream, ['feature1', 'feature2'])

        assert detector.is_trained
        assert 'default' in detector.models

    def test_anomaly_detection(self):
        """Test anomaly detection on new data"""
        detector = AnomalyDetector()

        # Train with normal data
        np.random.seed(42)
        data_stream = []
        for _ in range(100):
            data_stream.append({
                'feature1': np.random.normal(0, 1),
                'feature2': np.random.normal(0, 1)
            })

        detector.update_baseline(data_stream, ['feature1', 'feature2'])
        detector.train_anomaly_model(data_stream, ['feature1', 'feature2'])

        # Test normal data
        normal_data = {'feature1': 0.0, 'feature2': 0.0}
        result = detector.detect_anomalies(normal_data, ['feature1', 'feature2'])
        assert 'is_anomaly' in result
        assert 'score' in result
        assert 'confidence' in result

        # Test anomalous data
        anomalous_data = {'feature1': 10.0, 'feature2': 10.0}
        result = detector.detect_anomalies(anomalous_data, ['feature1', 'feature2'])
        assert 'is_anomaly' in result


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality"""

    def test_metric_recording(self):
        """Test metric recording"""
        monitor = PerformanceMonitor(window_size=10)

        monitor.record_metric('test_metric', 1.0)
        monitor.record_metric('test_metric', 2.0)
        monitor.record_metric('test_metric', 3.0)

        stats = monitor.get_metric_stats('test_metric')
        assert stats is not None
        assert stats['current'] == 3.0
        assert stats['mean'] == 2.0
        assert stats['count'] == 3

    def test_threshold_checking(self):
        """Test threshold checking"""
        monitor = PerformanceMonitor()

        monitor.set_threshold('test_metric', warning=5.0, critical=10.0)

        monitor.record_metric('test_metric', 7.0)  # Should trigger warning

        alerts = monitor.check_thresholds()
        assert len(alerts) == 1
        assert alerts[0]['level'] == 'warning'
        assert alerts[0]['value'] == 7.0

    def test_window_size_limit(self):
        """Test window size limiting"""
        monitor = PerformanceMonitor(window_size=3)

        for i in range(5):
            monitor.record_metric('test_metric', float(i))

        stats = monitor.get_metric_stats('test_metric')
        assert stats['count'] == 3  # Should only keep last 3 values


class TestRealTimeMonitor:
    """Test RealTimeMonitor integration"""

    def test_monitor_creation(self):
        """Test monitor creation"""
        monitor = create_real_time_monitor()
        assert isinstance(monitor, RealTimeMonitor)
        assert not monitor.is_monitoring
        assert len(monitor.alert_manager.rules) == 3  # Default rules

    def test_feature_column_setting(self):
        """Test setting feature columns"""
        monitor = create_real_time_monitor()
        monitor.set_feature_columns(['col1', 'col2', 'col3'])
        assert monitor.feature_columns == ['col1', 'col2', 'col3']

    def test_data_processing(self):
        """Test data point processing"""
        monitor = create_real_time_monitor()
        monitor.set_feature_columns(['feature1', 'feature2'])

        data = {
            'data': {'feature1': 1.0, 'feature2': 2.0},
            'timestamp': pd.Timestamp.now()
        }

        result = monitor.process_data_point(data)

        assert 'timestamp' in result
        assert 'quality_score' in result
        assert 'processing_time' in result
        assert len(monitor.data_buffer) == 1

    def test_monitoring_status(self):
        """Test monitoring status retrieval"""
        monitor = create_real_time_monitor()

        status = monitor.get_monitoring_status()

        assert 'is_monitoring' in status
        assert 'active_alerts' in status
        assert 'total_alerts' in status
        assert 'anomaly_detector_trained' in status
        assert 'buffer_size' in status
        assert 'performance_metrics' in status
        assert 'feature_columns' in status


class TestAlertConfigurations:
    """Test alert configuration utilities"""

    def test_email_config(self):
        """Test email alert configuration"""
        config = setup_email_alerts(
            smtp_server="smtp.test.com",
            smtp_port=587,
            username="test@test.com",
            password="password",
            from_email="test@test.com",
            to_emails=["admin@test.com"]
        )

        assert config['smtp_server'] == "smtp.test.com"
        assert config['smtp_port'] == 587
        assert config['username'] == "test@test.com"
        assert config['from_email'] == "test@test.com"
        assert config['to_emails'] == ["admin@test.com"]

    def test_slack_config(self):
        """Test Slack alert configuration"""
        config = setup_slack_alerts("https://hooks.slack.com/test")

        assert config['webhook_url'] == "https://hooks.slack.com/test"

    def test_webhook_config(self):
        """Test webhook alert configuration"""
        config = setup_webhook_alerts("https://api.test.com/webhook")

        assert config['url'] == "https://api.test.com/webhook"


if __name__ == "__main__":
    pytest.main([__file__])