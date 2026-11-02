"""Checks using synthetic data only; no running API or private exports required."""

import contextlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from backend.cardiac_model import CardiacDigitalTwin
from backend.health_data_csv_parser import HealthCSVParser
from backend.optimizer_ai import AITrainingOptimizer
import healthkit_api_server as api
from simulation.workout_simulator import WorkoutSimulator

ROOT = Path(__file__).resolve().parents[1]


class DataAndSimulationTests(unittest.TestCase):
    def test_synthetic_csv_to_strategy_comparison(self):
        parser = HealthCSVParser(str(ROOT / 'examples/HealthAutoExport-demo.csv'))
        daily = parser.parse_daily_metrics()
        self.assertEqual(len(daily), 14)
        self.assertTrue({'resting_hr', 'hrv_sdnn', 'heart_rate'}.issubset(daily.columns))
        features = parser.compute_personal_features()
        twin = CardiacDigitalTwin()
        twin.calibrate(features)
        result = AITrainingOptimizer(twin, duration_min=30).optimize(features)
        comparison = result['comparison_table']
        self.assertEqual(set(comparison['strategy']), set(WorkoutSimulator.STRATEGIES))
        self.assertIn(result['best_strategy'], WorkoutSimulator.STRATEGIES)
        self.assertTrue(comparison['adjusted_ces'].between(0, 100).all())
        for frame in result['simulations'].values():
            self.assertGreater(len(frame), 0)
            self.assertTrue(np.isfinite(frame.select_dtypes(include='number')).all().all())


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()
        original = api.iphone_live_data.copy()
        api.iphone_live_data.update({key: None for key in original})
        self.addCleanup(api.iphone_live_data.update, original)

    def test_health_and_demo_metrics(self):
        self.assertEqual(self.client.get('/health').status_code, 200)
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['source'], 'Demo Mode')

    def test_upload_and_retrieve(self):
        payload = {'heart_rate': 75, 'steps': 5000, 'active_energy': 250}
        response = self.client.post('/api/upload', json=payload)
        self.assertEqual(response.status_code, 200)
        metrics = self.client.get('/api/metrics').json
        self.assertEqual(metrics['source'], 'iPhone (Live)')
        self.assertEqual(metrics['heart_rate']['value'], 75)
        self.assertEqual(metrics['steps']['steps'], 5000)
        self.assertEqual(metrics['active_energy']['value'], 250)

    def test_invalid_upload_does_not_replace_metrics(self):
        for payload in ({}, {'heart_rate': 75}, {'heart_rate': 999, 'steps': 0, 'active_energy': 0}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/upload', json=payload).status_code, 400)
                self.assertIsNone(api.iphone_live_data['timestamp'])


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Copy public application files without local exports or environments.
        cls.workspace = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.project = Path(cls.workspace.name)
        for file in ROOT.glob('*.py'):
            shutil.copy2(file, cls.project / file.name)
        for folder in ('backend', 'scoring', 'simulation'):
            shutil.copytree(ROOT / folder, cls.project / folder, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT / 'heart.glb', cls.project / 'heart.glb')

    def render(self, entry):
        import streamlit as st
        from streamlit.testing.v1 import AppTest
        # A live server on a developer's computer must not affect the smoke test.
        st.cache_resource.clear()
        with contextlib.chdir(self.project), patch('requests.get', side_effect=ConnectionError('Offline test')):
            result = AppTest.from_file(str(self.project / entry), default_timeout=60).run()
        self.assertEqual([error.message for error in result.exception], [])

    def test_main_dashboard_without_exports(self):
        self.render('app_final.py')

    def test_main_dashboard_with_synthetic_csv(self):
        data_dir = self.project / 'data'
        data_dir.mkdir(exist_ok=True)
        csv_file = data_dir / 'HealthAutoExport-demo.csv'
        shutil.copy2(ROOT / 'examples/HealthAutoExport-demo.csv', csv_file)
        try:
            self.render('app_final.py')
        finally:
            csv_file.unlink()

    def test_risk_dashboard_without_api(self):
        self.render('app_risk_alert.py')

    def test_3d_dashboard_without_exports(self):
        self.render('app.py')


if __name__ == '__main__':
    unittest.main()
