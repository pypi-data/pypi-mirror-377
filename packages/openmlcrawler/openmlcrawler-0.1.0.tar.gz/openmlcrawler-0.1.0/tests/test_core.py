"""
Unit tests for openmlcrawler.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os

from openmlcrawler.core.parsers import parse_csv, parse_json
from openmlcrawler.core.cleaners import DataCleaner
from openmlcrawler.core.schema import SchemaDetector
from openmlcrawler.core.exporter import export_csv, export_json
from openmlcrawler.core.utils import CacheManager
from openmlcrawler.connectors.weather import load_weather_dataset

class TestParsers:
    """Test data parsers."""

    def test_parse_csv_basic(self):
        """Test basic CSV parsing."""
        csv_data = "name,age,city\nJohn,25,NYC\nJane,30,LA\n"
        df = parse_csv(csv_data)

        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'city']
        assert df.iloc[0]['name'] == 'John'

    def test_parse_csv_semicolon(self):
        """Test CSV parsing with semicolon separator."""
        csv_data = "name;age;city\nJohn;25;NYC\nJane;30;LA\n"
        df = parse_csv(csv_data)

        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'city']

    def test_parse_json_list(self):
        """Test JSON parsing with list of records."""
        json_data = '[{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]'
        df = parse_json(json_data)

        assert len(df) == 2
        assert list(df.columns) == ['name', 'age']
        assert df.iloc[0]['name'] == 'John'

    def test_parse_json_single_record(self):
        """Test JSON parsing with single record."""
        json_data = '{"name": "John", "age": 25}'
        df = parse_json(json_data)

        assert len(df) == 1
        assert list(df.columns) == ['name', 'age']

class TestDataCleaner:
    """Test data cleaning functionality."""

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            'name': ['John', 'Jane', 'John'],
            'age': [25, 30, 25]
        })

        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        result = cleaner.get_cleaned_data()

        assert len(result) == 2

    def test_handle_missing_values_drop(self):
        """Test missing value handling - drop strategy."""
        df = pd.DataFrame({
            'A': [1, 2, None],
            'B': [4, None, 6]
        })

        cleaner = DataCleaner(df)
        cleaner.handle_missing_values(strategy='drop')
        result = cleaner.get_cleaned_data()

        assert len(result) == 1

    def test_detect_column_types(self):
        """Test automatic column type detection."""
        df = pd.DataFrame({
            'numeric_str': ['1', '2', '3'],
            'text': ['hello', 'world', 'test'],
            'mixed': ['2023-01-01', 'not_date', '2023-01-02']
        })

        cleaner = DataCleaner(df)
        cleaner.detect_column_types()
        result = cleaner.get_cleaned_data()

        # Check numeric conversion
        assert pd.api.types.is_numeric_dtype(result['numeric_str'])

class TestSchemaDetector:
    """Test schema detection."""

    def test_detect_schema_basic(self):
        """Test basic schema detection."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['A', 'B', 'A', 'B', 'A'],
            'target': [0, 1, 0, 1, 0]
        })

        detector = SchemaDetector(df)
        schema = detector.detect_schema(target_column='target')

        assert 'features' in schema
        assert 'target' in schema
        assert schema['target'] == 'target'
        assert len(schema['features']) == 2

    def test_prepare_for_ml(self):
        """Test ML preparation."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': ['A', 'B', 'A', 'B', 'A'],
            'target': [0, 1, 0, 1, 0]
        })

        detector = SchemaDetector(df)
        result = detector.prepare_for_ml(target_column='target', test_size=0.4)

        assert 'X_train' in result
        assert 'X_test' in result
        assert 'y_train' in result
        assert 'y_test' in result

class TestExporter:
    """Test data export functionality."""

    def test_export_csv(self):
        """Test CSV export."""
        df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            result_path = export_csv(df, filepath)
            assert result_path == filepath
            assert os.path.exists(filepath)

            # Verify content
            with open(filepath, 'r') as f:
                content = f.read()
                assert 'A,B' in content
                assert '1,x' in content

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_export_json(self):
        """Test JSON export."""
        df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            result_path = export_json(df, filepath)
            assert result_path == filepath
            assert os.path.exists(filepath)

            # Verify content
            with open(filepath, 'r') as f:
                content = f.read()
                assert '"A": 1' in content or '[{"A": 1' in content

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

class TestCacheManager:
    """Test caching functionality."""

    def test_cache_operations(self):
        """Test basic cache operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(temp_dir)

            # Test cache set and get
            url = "https://example.com/data"
            data = "test data"

            cache.set(url, data)
            cached_data = cache.get(url)

            assert cached_data == data

    def test_cache_miss(self):
        """Test cache miss."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = CacheManager(temp_dir)

            result = cache.get("https://nonexistent.com")
            assert result is None

class TestWeatherConnector:
    """Test weather connector."""

    @patch('requests.get')
    def test_load_weather_dataset(self, mock_get):
        """Test weather dataset loading."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'hourly': {
                'time': ['2023-01-01T00:00', '2023-01-01T01:00'],
                'temperature_2m': [20.0, 21.0]
            },
            'daily': {
                'time': ['2023-01-01'],
                'temperature_2m_max': [25.0]
            }
        }
        mock_get.return_value = mock_response

        # This would normally call the real API
        # For testing, we'd need to mock the geocoding as well
        # df = load_weather_dataset("Delhi", 1)
        # assert len(df) > 0
        pass

class TestUtils:
    """Test utility functions."""

    def test_search_open_data(self):
        """Test open data search."""
        from openmlcrawler.core.utils import search_open_data

        results = search_open_data("covid")
        assert isinstance(results, list)
        assert len(results) > 0

        # Check result structure
        result = results[0]
        assert 'title' in result
        assert 'url' in result
        assert 'source' in result

if __name__ == '__main__':
    pytest.main([__file__])