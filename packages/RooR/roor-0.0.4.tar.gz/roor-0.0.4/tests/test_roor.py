# -*- coding: utf-8 -*-
"""
Unit tests for the RooR package.
"""

import unittest
import os
import pandas as pd
from src.RooR import behavioral_analysis, attack_simulation, report_generation

class TestRooR(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        self.reports_dir = "test_reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

        # Create a dummy log file
        self.log_file = os.path.join(self.reports_dir, "dummy_logs.csv")
        log_data = {
            'timestamp': pd.to_datetime(['2023-10-27 10:00:00', '2023-10-27 10:05:00']),
            'event_type': ['login', 'logout']
        }
        pd.DataFrame(log_data).to_csv(self.log_file, index=False)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        import shutil
        if os.path.exists(self.reports_dir):
            shutil.rmtree(self.reports_dir)

    def test_analyze_logs(self):
        """Test the log analysis function."""
        anomalies = behavioral_analysis.analyze_logs(self.log_file)
        self.assertIsInstance(anomalies, pd.DataFrame)

    def test_simulate_lattice_based_attack(self):
        """Test the lattice-based attack simulation."""
        result = attack_simulation.simulate_lattice_based_attack("test_system")
        self.assertIn("attack_type", result)
        self.assertEqual(result["attack_type"], "lattice-based")
        self.assertIn("success", result)

    def test_evaluate_resilience(self):
        """Test the model resilience evaluation."""
        predictions = [1, 0, 1]
        ground_truth = [1, 1, 1]
        metrics = behavioral_analysis.evaluate_post_quantum_resilience(predictions, ground_truth)
        self.assertIn("accuracy", metrics)
        self.assertAlmostEqual(metrics["accuracy"], 2/3)

    def test_generate_json_report(self):
        """Test JSON report generation."""
        report_file = os.path.join(self.reports_dir, "report.json")
        data = {"status": "ok"}
        report_generation.generate_json_report(data, report_file)
        self.assertTrue(os.path.exists(report_file))

    def test_generate_csv_report(self):
        """Test CSV report generation."""
        report_file = os.path.join(self.reports_dir, "report.csv")
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        report_generation.generate_csv_report(data, report_file)
        self.assertTrue(os.path.exists(report_file))

if __name__ == '__main__':
    unittest.main()
